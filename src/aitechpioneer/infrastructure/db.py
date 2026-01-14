import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..domain.models import (
    Chunk,
    ChunkMergeRecord,
    ChunkMetadata,
    ChunkQuality,
    ChunkStatus,
    ChunkType,
    ChunkVersion,
    CostAssessment,
    Decision,
    DecisionRecord,
    EffectRating,
    FileType,
    GenerationParams,
    ImpactAnalysis,
    OptimizationOperation,
    OptimizationSummary,
    Question,
    QuestionClassification,
    QuestionStatus,
    QuestionType,
    RetrievalParams,
    RetrievedChunkInfo,
    RiskAssessment,
    RootCause,
    Scope,
    Severity,
    StatusHistory,
    TestPlan,
    TestPlanResults,
    UserFeedback,
    VerificationRecord,
)
from ..domain.ports import (
    QuestionRepository,
    TestPlanRepository,
    VectorDatabasePort,
    VerificationRepository,
)
from ..settings import settings

logger = logging.getLogger(__name__)


class QdrantDatabase(VectorDatabasePort):
    def __init__(self):
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
        os.environ["no_proxy"] = "localhost,127.0.0.1"
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key or None,
            prefer_grpc=False,
        )
        logger.info(f"Connected to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")

    async def create_collection(self, collection_name: str, vector_size: int) -> None:
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Collection '{collection_name}' created successfully")
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            raise

    async def collection_exists(self, collection_name: str) -> bool:
        try:
            collections = self.client.get_collections()
            return collection_name in [c.name for c in collections.collections]
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            return False

    def _chunk_to_payload(self, chunk: Chunk) -> Dict[str, Any]:
        payload = {
            "chunk_id": str(chunk.chunk_id),
            "document_id": chunk.document_id,
            "parent_chunk_id": chunk.parent_chunk_id,
            "content": chunk.content,
            "status": chunk.status.value,
            "inactive_reason": chunk.inactive_reason,
            "quality": chunk.quality.value,
            "version": chunk.version,
            "chunk_type": chunk.chunk_type.value,
            "chunk_index": chunk.chunk_index,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
            "created_at": chunk.created_at.isoformat(),
            "updated_at": chunk.updated_at.isoformat(),
            "merged_from": chunk.merged_from,
            "derived_from": chunk.derived_from,
            "merge_record_id": str(chunk.merge_record_id) if chunk.merge_record_id else None,
            "metadata": (
                {
                    "source_file": chunk.metadata.source_file if chunk.metadata else "",
                    "file_type": chunk.metadata.file_type.value if chunk.metadata else "",
                    "page_number": chunk.metadata.page_number if chunk.metadata else None,
                    "section_title": chunk.metadata.section_title if chunk.metadata else None,
                    "word_count": chunk.metadata.word_count if chunk.metadata else 0,
                    "token_count": chunk.metadata.token_count if chunk.metadata else 0,
                    "display_name": chunk.metadata.display_name if chunk.metadata else None,
                    "file_path": chunk.metadata.file_path if chunk.metadata else None,
                }
                if chunk.metadata
                else {}
            ),
        }
        logger.debug(
            f"Generated payload for chunk {chunk.chunk_id}: "
            f"content_length={len(chunk.content) if chunk.content else 0}, "
            f"merged_from={chunk.merged_from}, "
            f"derived_from={chunk.derived_from}, "
            f"merge_record_id={chunk.merge_record_id}"
        )
        return payload

    def _payload_to_chunk(self, payload: Dict[str, Any], point_id: UUID) -> Chunk:
        metadata_dict = payload.get("metadata", {})
        metadata = None
        if metadata_dict:
            metadata = ChunkMetadata(
                source_file=metadata_dict.get("source_file", ""),
                file_type=FileType(metadata_dict.get("file_type", "txt")),
                page_number=metadata_dict.get("page_number"),
                section_title=metadata_dict.get("section_title"),
                word_count=metadata_dict.get("word_count", 0),
                token_count=metadata_dict.get("token_count", 0),
                display_name=metadata_dict.get("display_name"),
                file_path=metadata_dict.get("file_path"),
            )

        chunk_id_str = payload.get("chunk_id", str(point_id))
        chunk_id = UUID(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str

        return Chunk(
            chunk_id=chunk_id,
            document_id=payload.get("document_id", ""),
            parent_chunk_id=payload.get("parent_chunk_id"),
            content=payload.get("content", ""),
            status=ChunkStatus(payload.get("status", "active")),
            inactive_reason=payload.get("inactive_reason"),
            quality=ChunkQuality(payload.get("quality", "high")),
            version=payload.get("version", 1),
            chunk_type=ChunkType(payload.get("chunk_type", "child")),
            chunk_index=payload.get("chunk_index", 0),
            start_char=payload.get("start_char", 0),
            end_char=payload.get("end_char", 0),
            created_at=datetime.fromisoformat(
                payload.get("created_at", datetime.utcnow().isoformat())
            ),
            updated_at=datetime.fromisoformat(
                payload.get("updated_at", datetime.utcnow().isoformat())
            ),
            metadata=metadata,
            merged_from=payload.get("merged_from"),
            derived_from=payload.get("derived_from"),
            merge_record_id=(
                UUID(payload.get("merge_record_id"))
                if payload.get("merge_record_id")
                else None
            ),
        )

    async def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> None:
        try:
            logger.info(
                f"Starting to insert {len(chunks)} chunks "
                f"into collection '{collection_name}'"
            )

            batch_size = 100
            total_inserted = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                points = []
                for chunk in batch:
                    payload = self._chunk_to_payload(chunk)
                    logger.debug(
                        f"Preparing chunk {chunk.chunk_id} for insertion: "
                        f"document_id={chunk.document_id}, "
                        f"content_preview={chunk.content[:50] if chunk.content else 'N/A'}"
                    )
                    logger.debug(
                        f"Payload details for chunk {chunk.chunk_id}: "
                        f"status={payload.get('status')}, "
                        f"merged_from={payload.get('merged_from')}, "
                        f"derived_from={payload.get('derived_from')}, "
                        f"content_length={len(payload.get('content', ''))}"
                    )
                    point = PointStruct(
                        id=chunk.chunk_id,
                        vector=chunk.embedding,
                        payload=payload,
                    )
                    points.append(point)

                upsert_result = self.client.upsert(
                    collection_name=collection_name,
                    points=points,
                )
                logger.debug(
                    f"Upsert result for batch {i//batch_size + 1}: "
                    f"{upsert_result}"
                )
                total_inserted += len(batch)
                logger.info(
                    f"Inserted batch {total_inserted}/{len(chunks)} "
                    f"chunks into '{collection_name}'"
                )

            logger.info(f"Successfully inserted {len(chunks)} chunks into '{collection_name}'")

            # Verify insertion by querying the collection
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )
            logger.info(
                f"Collection '{collection_name}' now contains "
                f"{len(result[0])} total points"
            )

        except Exception as e:
            logger.error(f"Failed to insert chunks into '{collection_name}': {e}", exc_info=True)
            raise

    async def search_chunks(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        status_filter: Optional[ChunkStatus] = None,
    ) -> List[Tuple[Chunk, float]]:
        try:
            search_filter = None
            if status_filter:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="status",
                            match=MatchValue(value=status_filter.value),
                        )
                    ]
                )

            search_result = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            results = []
            for hit in search_result.points:
                if hit.payload is None:
                    logger.warning(f"Hit with id {hit.id} has no payload")
                    continue
                chunk = self._payload_to_chunk(hit.payload, UUID(str(hit.id)))
                results.append((chunk, hit.score))

            return results
        except Exception as e:
            logger.error(f"Failed to search in '{collection_name}': {e}")
            return []

    async def update_chunk(self, collection_name: str, chunk: Chunk) -> None:
        try:
            if chunk.embedding:
                self.client.upsert(
                    collection_name=collection_name,
                    points=[
                        PointStruct(
                            id=chunk.chunk_id,
                            vector=chunk.embedding,
                            payload=self._chunk_to_payload(chunk)
                        )
                    ],
                )
            else:
                self.client.set_payload(
                    collection_name=collection_name,
                    payload=self._chunk_to_payload(chunk),
                    points=[chunk.chunk_id],
                )
            logger.info(f"Updated chunk '{chunk.chunk_id}' in '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to update chunk '{chunk.chunk_id}' in '{collection_name}': {e}")
            raise

    async def delete_chunk(self, collection_name: str, chunk_id: UUID) -> None:
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=[chunk_id],
            )
            logger.info(f"Deleted chunk '{chunk_id}' from '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete chunk '{chunk_id}' from '{collection_name}': {e}")
            raise

    async def get_chunks_by_document(self, collection_name: str, document_id: str) -> List[Chunk]:
        try:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            )

            result = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=search_filter,
                limit=1000,
            )

            chunks = []
            for point in result[0]:
                if point.payload:
                    chunk = self._payload_to_chunk(point.payload, UUID(str(point.id)))
                    chunks.append(chunk)

            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks for document '{document_id}': {e}")
            return []

    async def get_chunk_by_id(self, collection_name: str, chunk_id: UUID) -> Optional[Chunk]:
        try:
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[chunk_id],
            )

            if result and result[0].payload:
                chunk = self._payload_to_chunk(result[0].payload, UUID(str(result[0].id)))
                return chunk

            return None
        except Exception as e:
            logger.error(f"Failed to get chunk '{chunk_id}': {e}")
            return None

    async def get_all_documents(self, collection_name: str) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Retrieving all documents from collection '{collection_name}'")

            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )

            logger.info(f"Retrieved {len(result[0])} points from collection '{collection_name}'")

            documents = {}
            for point in result[0]:
                if not point.payload:
                    logger.warning(f"Point {point.id} has no payload, skipping")
                    continue

                document_id = point.payload.get("document_id")
                if not document_id:
                    logger.warning(f"Point {point.id} has no document_id in payload, skipping")
                    continue

                logger.debug(f"Processing point {point.id} with document_id={document_id}")

                if document_id not in documents:
                    documents[document_id] = {
                        "document_id": document_id,
                        "file_name": point.payload.get("metadata", {}).get("source_file", ""),
                        "display_name": point.payload.get("metadata", {}).get("display_name"),
                        "file_path": point.payload.get("metadata", {}).get("file_path"),
                        "file_type": point.payload.get("metadata", {}).get("file_type", ""),
                        "uploaded_at": point.payload.get("created_at", ""),
                        "chunk_count": 0,
                    }
                    logger.debug(f"Created new document entry for document_id={document_id}")

                documents[document_id]["chunk_count"] += 1

            document_list = list(documents.values())
            logger.info(
                f"Found {len(document_list)} unique documents "
                f"in collection '{collection_name}'"
            )

            for doc in document_list:
                logger.debug(
                    f"Document: {doc['document_id']}, "
                    f"file_name={doc['file_name']}, "
                    f"chunk_count={doc['chunk_count']}"
                )

            return document_list
        except Exception as e:
            logger.error(f"Failed to get documents from '{collection_name}': {e}", exc_info=True)
            return []

    async def get_document(
        self, collection_name: str, document_id: str
    ) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Retrieving document {document_id} from collection '{collection_name}'")

            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )

            document_info = None
            chunk_count = 0

            for point in result[0]:
                if not point.payload:
                    continue
                if point.payload.get("document_id") == document_id:
                    if document_info is None:
                        document_info = {
                            "document_id": document_id,
                            "file_name": point.payload.get("metadata", {}).get("source_file", ""),
                            "display_name": point.payload.get("metadata", {}).get("display_name"),
                            "file_path": point.payload.get("metadata", {}).get("file_path"),
                            "file_type": point.payload.get("metadata", {}).get("file_type", ""),
                            "uploaded_at": point.payload.get("created_at", ""),
                        }
                    chunk_count += 1

            if document_info:
                document_info["chunk_count"] = chunk_count
                logger.info(f"Found document {document_id} with {chunk_count} chunks")
                return document_info

            logger.warning(f"Document {document_id} not found in collection '{collection_name}'")
            return None
        except Exception as e:
            logger.error(
                f"Failed to get document '{document_id}' "
                f"from '{collection_name}': {e}",
                exc_info=True
            )
            return None

    async def get_all_chunks(self, collection_name: str) -> List[Chunk]:
        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )

            chunks = []
            for point in result[0]:
                if not point.payload:
                    continue

                is_version_record = point.payload.get("is_version_record", False)
                is_merge_record = point.payload.get("is_merge_record", False)

                if is_version_record or is_merge_record:
                    logger.debug(f"Skipping version/merge record: {point.id}")
                    continue

                chunk = self._payload_to_chunk(point.payload, UUID(str(point.id)))
                chunks.append(chunk)

            chunks.sort(key=lambda x: (x.document_id, x.chunk_index, x.start_char))

            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks from '{collection_name}': {e}")
            return []

    async def get_adjacent_chunks(
        self,
        collection_name: str,
        chunk_id: UUID,
        similarity_threshold: float = 0.3,
        max_adjacent: int = 5,
    ) -> Dict[str, Optional[Chunk]]:
        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )

            all_chunks = []
            for point in result[0]:
                if not point.payload:
                    continue

                is_version_record = point.payload.get("is_version_record", False)
                is_merge_record = point.payload.get("is_merge_record", False)

                if is_version_record or is_merge_record:
                    continue

                chunk = self._payload_to_chunk(point.payload, UUID(str(point.id)))
                all_chunks.append(chunk)

            all_chunks.sort(key=lambda x: (x.document_id, x.chunk_index, x.start_char))

            target_chunk = None
            for chunk in all_chunks:
                if chunk.chunk_id == chunk_id:
                    target_chunk = chunk
                    break

            if not target_chunk:
                logger.warning(f"Chunk {chunk_id} not found")
                return {"prev": None, "next": None}

            document_chunks = [
                c for c in all_chunks
                if c.document_id == target_chunk.document_id
            ]

            document_chunks.sort(key=lambda x: x.chunk_index)

            target_index = -1
            for i, chunk in enumerate(document_chunks):
                if chunk.chunk_id == chunk_id:
                    target_index = i
                    break

            if target_index == -1:
                logger.warning(f"Chunk {chunk_id} not found in document chunks")
                return {"prev": None, "next": None}

            prev_chunks = []
            next_chunks = []

            for i in range(max(0, target_index - max_adjacent), target_index):
                prev_chunks.append(document_chunks[i])

            for i in range(target_index + 1, min(len(document_chunks), target_index + max_adjacent + 1)):
                next_chunks.append(document_chunks[i])

            prev_adjacent = None
            next_adjacent = None

            if prev_chunks:
                prev_adjacent = prev_chunks[-1]

            if next_chunks:
                next_adjacent = next_chunks[0]

            logger.info(
                f"Found adjacent chunks for {chunk_id}: "
                f"prev={prev_adjacent.chunk_id if prev_adjacent else None}, "
                f"next={next_adjacent.chunk_id if next_adjacent else None}"
            )

            return {
                "prev": prev_adjacent,
                "next": next_adjacent,
                "prev_chunks": prev_chunks,
                "next_chunks": next_chunks,
            }

        except Exception as e:
            logger.error(f"Failed to get adjacent chunks for {chunk_id}: {e}")
            return {"prev": None, "next": None}

    async def insert_chunk_version(self, collection_name: str, version: ChunkVersion) -> None:
        try:
            point_id = version.version_id

            vector = version.embedding
            if not vector or len(vector) == 0:
                vector = [0.0] * 512
                logger.warning(
                    f"Empty embedding for version {version.version_id}, "
                    f"using zero vector"
                )

            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "version_id": str(version.version_id),
                            "chunk_id": str(version.chunk_id),
                            "version": version.version,
                            "content": version.content,
                            "status": version.status.value,
                            "quality": version.quality.value,
                            "metadata": version.metadata.__dict__ if version.metadata else None,
                            "created_at": version.created_at.isoformat(),
                            "created_by": version.created_by,
                            "is_version_record": True,
                        },
                    )
                ],
            )
            logger.info(f"Inserted chunk version {version.version_id} for chunk {version.chunk_id}")
        except Exception as e:
            logger.error(f"Error inserting chunk version {version.version_id}: {e}")
            raise

    async def get_chunk_versions(self, collection_name: str, chunk_id: UUID) -> List[ChunkVersion]:
        try:
            results = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="chunk_id",
                            match=MatchValue(value=str(chunk_id)),
                        ),
                        FieldCondition(
                            key="is_version_record",
                            match=MatchValue(value=True),
                        ),
                    ]
                ),
                limit=100,
                with_payload=True,
                with_vectors=True,
            )[0]

            versions = []
            for point in results:
                payload = point.payload
                metadata = None
                if payload.get("metadata"):
                    metadata = ChunkMetadata(**payload["metadata"])

                version = ChunkVersion(
                    version_id=UUID(payload["version_id"]),
                    chunk_id=UUID(payload["chunk_id"]),
                    version=payload["version"],
                    content=payload["content"],
                    embedding=point.vector,
                    status=ChunkStatus(payload["status"]),
                    quality=ChunkQuality(payload["quality"]),
                    metadata=metadata,
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    created_by=payload["created_by"],
                )
                versions.append(version)

            logger.info(f"Found {len(versions)} versions for chunk {chunk_id}")
            return versions
        except Exception as e:
            logger.error(f"Error getting chunk versions for {chunk_id}: {e}")
            raise

    async def insert_merge_record(self, collection_name: str, record: ChunkMergeRecord) -> None:
        try:
            point_id = record.record_id
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=[0.0] * 512,
                        payload={
                            "record_id": str(record.record_id),
                            "merge_type": record.merge_type,
                            "source_chunk_ids": [str(id) for id in record.source_chunk_ids],
                            "target_chunk_id": str(record.target_chunk_id),
                            "previous_state": record.previous_state,
                            "created_at": record.created_at.isoformat(),
                            "created_by": record.created_by,
                            "is_reversible": record.is_reversible,
                            "is_merge_record": True,
                        },
                    )
                ],
            )
            logger.info(f"Inserted merge record {record.record_id}")
        except Exception as e:
            logger.error(f"Error inserting merge record {record.record_id}: {e}")
            raise

    async def get_merge_record(
        self,
        collection_name: str,
        record_id: UUID,
    ) -> Optional[ChunkMergeRecord]:
        try:
            results = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="record_id",
                            match=MatchValue(value=str(record_id)),
                        ),
                        FieldCondition(
                            key="is_merge_record",
                            match=MatchValue(value=True),
                        ),
                    ]
                ),
                limit=1,
                with_payload=True,
                with_vectors=False,
            )[0]

            if not results:
                return None

            point = results[0]
            payload = point.payload

            record = ChunkMergeRecord(
                record_id=UUID(payload["record_id"]),
                merge_type=payload["merge_type"],
                source_chunk_ids=[UUID(id) for id in payload["source_chunk_ids"]],
                target_chunk_id=UUID(payload["target_chunk_id"]),
                previous_state=payload["previous_state"],
                created_at=datetime.fromisoformat(payload["created_at"]),
                created_by=payload["created_by"],
                is_reversible=payload["is_reversible"],
            )

            logger.info(f"Found merge record {record_id}")
            return record
        except Exception as e:
            logger.error(f"Error getting merge record {record_id}: {e}")
            raise

    async def get_merge_records(
        self,
        collection_name: str,
        document_id: Optional[str] = None,
        chunk_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[ChunkMergeRecord]:
        try:
            must_conditions = [
                FieldCondition(
                    key="is_merge_record",
                    match=MatchValue(value=True),
                )
            ]

            if document_id:
                must_conditions.append(
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                )

            if chunk_id:
                results = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=Filter(
                        must=must_conditions,
                        should=[
                            FieldCondition(
                                key="source_chunk_ids",
                                match=MatchAny(any=[str(chunk_id)]),
                            ),
                            FieldCondition(
                                key="target_chunk_id",
                                match=MatchValue(value=str(chunk_id)),
                            ),
                        ]
                    ),
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                )[0]
            else:
                results = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=Filter(must=must_conditions),
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                )[0]

            records = []
            for point in results:
                payload = point.payload

                record = ChunkMergeRecord(
                    record_id=UUID(payload["record_id"]),
                    merge_type=payload["merge_type"],
                    source_chunk_ids=[UUID(id) for id in payload["source_chunk_ids"]],
                    target_chunk_id=UUID(payload["target_chunk_id"]),
                    previous_state=payload["previous_state"],
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    created_by=payload["created_by"],
                    is_reversible=payload["is_reversible"],
                )
                records.append(record)

            logger.info(f"Found {len(records)} merge records")
            return records
        except Exception as e:
            logger.error(f"Error getting merge records: {e}")
            raise


qdrant_db = QdrantDatabase()


class QdrantQuestionRepository(QuestionRepository):
    def __init__(self):
        self.collection_name = "questions"
        self.client = qdrant_db.client

    async def _ensure_collection(self):
        if not await qdrant_db.collection_exists(self.collection_name):
            await qdrant_db.create_collection(self.collection_name, 512)

    def _question_to_payload(self, question: Question) -> Dict[str, Any]:
        return {
            "question_id": question.question_id,
            "question": question.question,
            "answer": question.answer,
            "retrieved_chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "score": chunk.score,
                    "document_id": chunk.document_id,
                }
                for chunk in question.retrieved_chunks
            ],
            "retrieval_params": {
                "top_k": question.retrieval_params.top_k,
                "score_threshold": question.retrieval_params.score_threshold,
                "retrieval_time": question.retrieval_params.retrieval_time,
            },
            "generation_params": {
                "model": question.generation_params.model,
                "temperature": question.generation_params.temperature,
                "generation_time": question.generation_params.generation_time,
            },
            "classification": {
                "type": question.classification.type.value,
                "severity": question.classification.severity.value,
                "scope": question.classification.scope.value,
                "root_cause": question.classification.root_cause.value,
                "priority": question.classification.priority,
            },
            "related_questions": question.related_questions,
            "related_chunks": question.related_chunks,
            "status": question.status.value,
            "status_history": [
                {
                    "status": h.status,
                    "timestamp": h.timestamp.isoformat(),
                    "operator": h.operator,
                    "comment": h.comment,
                }
                for h in question.status_history
            ],
            "user_feedback": {
                "rating": question.user_feedback.rating,
                "comment": question.user_feedback.comment,
                "is_helpful": question.user_feedback.is_helpful,
                "is_resolved": question.user_feedback.is_resolved,
            },
            "is_optimization_target": question.is_optimization_target,
            "optimization_target_since": (
                question.optimization_target_since.isoformat()
                if question.optimization_target_since
                else None
            ),
            "verification_records": [
                {
                    "verification_id": v.verification_id,
                    "question_id": v.question_id,
                    "test_plan_id": v.test_plan_id,
                    "original_answer": v.original_answer,
                    "new_answer": v.new_answer,
                    "original_chunks": [
                        {
                            "chunk_id": c.chunk_id,
                            "content": c.content,
                            "score": c.score,
                            "document_id": c.document_id,
                        }
                        for c in v.original_chunks
                    ],
                    "new_chunks": [
                        {
                            "chunk_id": c.chunk_id,
                            "content": c.content,
                            "score": c.score,
                            "document_id": c.document_id,
                        }
                        for c in v.new_chunks
                    ],
                    "similarity_score": v.similarity_score,
                    "chunk_changes": v.chunk_changes,
                    "score_changes": v.score_changes,
                    "effect_rating": v.effect_rating.value,
                    "user_comment": v.user_comment,
                    "timestamp": v.timestamp.isoformat(),
                }
                for v in question.verification_records
            ],
            "decision_records": [
                {
                    "decision_id": d.decision_id,
                    "test_plan_id": d.test_plan_id,
                    "timestamp": d.timestamp.isoformat(),
                    "decision": d.decision,
                    "reason": d.reason,
                    "operator": d.operator,
                }
                for d in question.decision_records
            ],
            "created_at": question.created_at.isoformat(),
            "updated_at": question.updated_at.isoformat(),
        }

    def _payload_to_question(self, payload: Dict[str, Any]) -> Question:
        return Question(
            question_id=payload.get("question_id", ""),
            question=payload.get("question", ""),
            answer=payload.get("answer", ""),
            retrieved_chunks=[
                RetrievedChunkInfo(
                    chunk_id=c["chunk_id"],
                    content=c["content"],
                    score=c["score"],
                    document_id=c["document_id"],
                )
                for c in payload.get("retrieved_chunks", [])
            ],
            retrieval_params=RetrievalParams(
                top_k=payload.get("retrieval_params", {}).get("top_k", 5),
                score_threshold=payload.get("retrieval_params", {}).get("score_threshold", 0.5),
                retrieval_time=payload.get("retrieval_params", {}).get("retrieval_time", 0.0),
            ),
            generation_params=GenerationParams(
                model=payload.get("generation_params", {}).get("model", ""),
                temperature=payload.get("generation_params", {}).get("temperature", 0.7),
                generation_time=payload.get("generation_params", {}).get("generation_time", 0.0),
            ),
            classification=QuestionClassification(
                type=QuestionType(payload.get("classification", {}).get("type", "factual")),
                severity=Severity(payload.get("classification", {}).get("severity", "low")),
                scope=Scope(payload.get("classification", {}).get("scope", "single_document")),
                root_cause=RootCause(payload.get("classification", {}).get("root_cause", "other")),
                priority=payload.get("classification", {}).get("priority", 1),
            ),
            related_questions=payload.get("related_questions", []),
            related_chunks=payload.get("related_chunks", []),
            status=QuestionStatus(payload.get("status", "discovered")),
            status_history=[
                StatusHistory(
                    status=h["status"],
                    timestamp=datetime.fromisoformat(h["timestamp"]),
                    operator=h["operator"],
                    comment=h.get("comment"),
                )
                for h in payload.get("status_history", [])
            ],
            user_feedback=UserFeedback(
                rating=payload.get("user_feedback", {}).get("rating"),
                comment=payload.get("user_feedback", {}).get("comment"),
                is_helpful=payload.get("user_feedback", {}).get("is_helpful"),
                is_resolved=payload.get("user_feedback", {}).get("is_resolved"),
            ),
            is_optimization_target=payload.get("is_optimization_target", False),
            optimization_target_since=(
                datetime.fromisoformat(payload["optimization_target_since"])
                if payload.get("optimization_target_since")
                else None
            ),
            verification_records=[
                VerificationRecord(
                    verification_id=v["verification_id"],
                    question_id=v["question_id"],
                    test_plan_id=v["test_plan_id"],
                    original_answer=v["original_answer"],
                    new_answer=v["new_answer"],
                    original_chunks=[
                        RetrievedChunkInfo(
                            chunk_id=c["chunk_id"],
                            content=c["content"],
                            score=c["score"],
                            document_id=c["document_id"],
                        )
                        for c in v["original_chunks"]
                    ],
                    new_chunks=[
                        RetrievedChunkInfo(
                            chunk_id=c["chunk_id"],
                            content=c["content"],
                            score=c["score"],
                            document_id=c["document_id"],
                        )
                        for c in v["new_chunks"]
                    ],
                    similarity_score=v["similarity_score"],
                    chunk_changes=v["chunk_changes"],
                    score_changes=v["score_changes"],
                    effect_rating=EffectRating(v["effect_rating"]),
                    user_comment=v.get("user_comment"),
                    timestamp=datetime.fromisoformat(v["timestamp"]),
                )
                for v in payload.get("verification_records", [])
            ],
            decision_records=[
                DecisionRecord(
                    decision_id=d["decision_id"],
                    test_plan_id=d["test_plan_id"],
                    timestamp=datetime.fromisoformat(d["timestamp"]),
                    decision=d["decision"],
                    reason=d["reason"],
                    operator=d["operator"],
                )
                for d in payload.get("decision_records", [])
            ],
            created_at=datetime.fromisoformat(
                payload.get("created_at", datetime.utcnow().isoformat())
            ),
            updated_at=datetime.fromisoformat(
                payload.get("updated_at", datetime.utcnow().isoformat())
            ),
        )

    async def create(self, question: Question) -> Question:
        await self._ensure_collection()
        question.updated_at = datetime.utcnow()
        payload = self._question_to_payload(question)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=question.question_id, vector=[], payload=payload)],
        )
        logger.info(f"Created question {question.question_id}")
        return question

    async def get_by_id(self, question_id: str) -> Optional[Question]:
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[question_id],
            )
            if result and result[0].payload:
                return self._payload_to_question(result[0].payload)
            return None
        except Exception as e:
            logger.error(f"Failed to get question {question_id}: {e}")
            return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[QuestionStatus] = None,
        is_optimization_target: Optional[bool] = None,
    ) -> List[Question]:
        try:
            filter_conditions = []
            if status:
                filter_conditions.append(
                    FieldCondition(key="status", match=MatchValue(value=status.value))
                )
            if is_optimization_target is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="is_optimization_target",
                        match=MatchValue(value=is_optimization_target)
                    )
                )

            search_filter = Filter(must=filter_conditions) if filter_conditions else None

            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=limit,
                offset=skip,
            )

            questions = []
            for point in result[0]:
                if point.payload:
                    questions.append(self._payload_to_question(point.payload))

            return questions
        except Exception as e:
            logger.error(f"Failed to get questions: {e}")
            return []

    async def update(self, question: Question) -> Question:
        question.updated_at = datetime.utcnow()
        payload = self._question_to_payload(question)
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=payload,
            points=[question.question_id],
        )
        logger.info(f"Updated question {question.question_id}")
        return question

    async def delete(self, question_id: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[question_id],
            )
            logger.info(f"Deleted question {question_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete question {question_id}: {e}")
            return False

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Question]:
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                offset=skip,
            )

            questions = []
            for point in result[0]:
                if point.payload and query.lower() in point.payload.get("question", "").lower():
                    questions.append(self._payload_to_question(point.payload))

            return questions
        except Exception as e:
            logger.error(f"Failed to search questions: {e}")
            return []


class QdrantVerificationRepository(VerificationRepository):
    def __init__(self):
        self.collection_name = "questions"
        self.client = qdrant_db.client

    async def create(self, verification: VerificationRecord) -> VerificationRecord:
        verification.timestamp = datetime.utcnow()
        return verification

    async def get_by_id(self, verification_id: str) -> Optional[VerificationRecord]:
        return None

    async def get_by_question_id(self, question_id: str) -> List[VerificationRecord]:
        try:
            question_repo = QdrantQuestionRepository()
            question = await question_repo.get_by_id(question_id)
            return question.verification_records if question else []
        except Exception as e:
            logger.error(f"Failed to get verifications for question {question_id}: {e}")
            return []

    async def get_by_test_plan_id(self, test_plan_id: str) -> List[VerificationRecord]:
        try:
            question_repo = QdrantQuestionRepository()
            questions = await question_repo.get_all()
            verifications = []
            for question in questions:
                for v in question.verification_records:
                    if v.test_plan_id == test_plan_id:
                        verifications.append(v)
            return verifications
        except Exception as e:
            logger.error(f"Failed to get verifications for test plan {test_plan_id}: {e}")
            return []

    async def update(self, verification: VerificationRecord) -> VerificationRecord:
        return verification

    async def delete(self, verification_id: str) -> bool:
        return False


class QdrantTestPlanRepository(TestPlanRepository):
    def __init__(self):
        self.collection_name = "test_plans"
        self.client = qdrant_db.client

    async def _ensure_collection(self):
        if not await qdrant_db.collection_exists(self.collection_name):
            await qdrant_db.create_collection(self.collection_name, 512)

    def _test_plan_to_payload(self, test_plan: TestPlan) -> Dict[str, Any]:
        return {
            "test_plan_id": test_plan.test_plan_id,
            "name": test_plan.name,
            "description": test_plan.description,
            "version": test_plan.version,
            "parent_plan_id": test_plan.parent_plan_id,
            "question_ids": test_plan.question_ids,
            "optimization_summary": {
                "operations": [
                    {
                        "operation_type": op.operation_type,
                        "chunk_ids": op.chunk_ids,
                        "timestamp": op.timestamp.isoformat(),
                    }
                    for op in test_plan.optimization_summary.operations
                ],
                "affected_documents": test_plan.optimization_summary.affected_documents,
                "affected_chunks": test_plan.optimization_summary.affected_chunks,
            },
            "status": test_plan.status,
            "started_at": test_plan.started_at.isoformat() if test_plan.started_at else None,
            "completed_at": test_plan.completed_at.isoformat() if test_plan.completed_at else None,
            "results": {
                "total": test_plan.results.total,
                "better": test_plan.results.better,
                "same": test_plan.results.same,
                "worse": test_plan.results.worse,
                "failed": test_plan.results.failed,
            },
            "decision": {
                "recommendation": test_plan.decision.recommendation,
                "reason": test_plan.decision.reason,
                "impact_analysis": {
                    "affected_questions": test_plan.decision.impact_analysis.affected_questions,
                    "improvement_rate": test_plan.decision.impact_analysis.improvement_rate,
                    "regression_rate": test_plan.decision.impact_analysis.regression_rate,
                },
                "risk_assessment": {
                    "level": test_plan.decision.risk_assessment.level,
                    "potential_issues": test_plan.decision.risk_assessment.potential_issues,
                },
                "cost_assessment": {
                    "remaining_issues": test_plan.decision.cost_assessment.remaining_issues,
                    "estimated_effort": test_plan.decision.cost_assessment.estimated_effort,
                },
                "next_actions": test_plan.decision.next_actions,
            },
            "created_at": test_plan.created_at.isoformat(),
            "updated_at": test_plan.updated_at.isoformat(),
            "created_by": test_plan.created_by,
        }

    def _payload_to_test_plan(self, payload: Dict[str, Any]) -> TestPlan:
        return TestPlan(
            test_plan_id=payload.get("test_plan_id", ""),
            name=payload.get("name", ""),
            description=payload.get("description"),
            version=payload.get("version", 1),
            parent_plan_id=payload.get("parent_plan_id"),
            question_ids=payload.get("question_ids", []),
            optimization_summary=OptimizationSummary(
                operations=[
                    OptimizationOperation(
                        operation_type=op["operation_type"],
                        chunk_ids=op["chunk_ids"],
                        timestamp=datetime.fromisoformat(op["timestamp"]),
                    )
                    for op in payload.get("optimization_summary", {})
                    .get("operations", [])
                ],
                affected_documents=payload.get("optimization_summary", {})
                .get("affected_documents", []),
                affected_chunks=payload.get("optimization_summary", {})
                .get("affected_chunks", []),
            ),
            status=payload.get("status", "draft"),
            started_at=datetime.fromisoformat(payload["started_at"])
            if payload.get("started_at")
            else None,
            completed_at=datetime.fromisoformat(payload["completed_at"])
            if payload.get("completed_at")
            else None,
            results=TestPlanResults(
                total=payload.get("results", {}).get("total", 0),
                better=payload.get("results", {}).get("better", 0),
                same=payload.get("results", {}).get("same", 0),
                worse=payload.get("results", {}).get("worse", 0),
                failed=payload.get("results", {}).get("failed", 0),
            ),
            decision=Decision(
                recommendation=payload.get("decision", {}).get("recommendation", ""),
                reason=payload.get("decision", {}).get("reason", ""),
                impact_analysis=ImpactAnalysis(
                    affected_questions=payload.get("decision", {})
                    .get("impact_analysis", {})
                    .get("affected_questions", 0),
                    improvement_rate=payload.get("decision", {})
                    .get("impact_analysis", {})
                    .get("improvement_rate", 0.0),
                    regression_rate=payload.get("decision", {})
                    .get("impact_analysis", {})
                    .get("regression_rate", 0.0),
                ),
                risk_assessment=RiskAssessment(
                    level=payload.get("decision", {})
                    .get("risk_assessment", {})
                    .get("level", "low"),
                    potential_issues=payload.get("decision", {})
                    .get("risk_assessment", {})
                    .get("potential_issues", []),
                ),
                cost_assessment=CostAssessment(
                    remaining_issues=payload.get("decision", {})
                    .get("cost_assessment", {})
                    .get("remaining_issues", 0),
                    estimated_effort=payload.get("decision", {})
                    .get("cost_assessment", {})
                    .get("estimated_effort", "low"),
                ),
                next_actions=payload.get("decision", {}).get("next_actions", []),
            ),
            created_at=datetime.fromisoformat(
                payload.get("created_at", datetime.utcnow().isoformat())
            ),
            updated_at=datetime.fromisoformat(
                payload.get("updated_at", datetime.utcnow().isoformat())
            ),
            created_by=payload.get("created_by", ""),
        )

    async def create(self, test_plan: TestPlan) -> TestPlan:
        await self._ensure_collection()
        test_plan.updated_at = datetime.utcnow()
        payload = self._test_plan_to_payload(test_plan)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=test_plan.test_plan_id, vector=[], payload=payload)],
        )
        logger.info(f"Created test plan {test_plan.test_plan_id}")
        return test_plan

    async def get_by_id(self, test_plan_id: str) -> Optional[TestPlan]:
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[test_plan_id],
            )
            if result and result[0].payload:
                return self._payload_to_test_plan(result[0].payload)
            return None
        except Exception as e:
            logger.error(f"Failed to get test plan {test_plan_id}: {e}")
            return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[TestPlan]:
        try:
            filter_conditions = []
            if status:
                filter_conditions.append(
                    FieldCondition(key="status", match=MatchValue(value=status))
                )

            search_filter = Filter(must=filter_conditions) if filter_conditions else None

            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=limit,
                offset=skip,
            )

            test_plans = []
            for point in result[0]:
                if point.payload:
                    test_plans.append(self._payload_to_test_plan(point.payload))

            return test_plans
        except Exception as e:
            logger.error(f"Failed to get test plans: {e}")
            return []

    async def update(self, test_plan: TestPlan) -> TestPlan:
        test_plan.updated_at = datetime.utcnow()
        payload = self._test_plan_to_payload(test_plan)
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=payload,
            points=[test_plan.test_plan_id],
        )
        logger.info(f"Updated test plan {test_plan.test_plan_id}")
        return test_plan

    async def delete(self, test_plan_id: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[test_plan_id],
            )
            logger.info(f"Deleted test plan {test_plan_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete test plan {test_plan_id}: {e}")
            return False

    async def get_by_version(self, parent_plan_id: str, version: int) -> Optional[TestPlan]:
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="parent_plan_id",
                            match=MatchValue(value=parent_plan_id)
                        ),
                        FieldCondition(key="version", match=MatchValue(value=version)),
                    ]
                ),
                limit=1,
            )

            if result[0] and result[0][0].payload:
                return self._payload_to_test_plan(result[0][0].payload)
            return None
        except Exception as e:
            logger.error(
                f"Failed to get test plan version {version} "
                f"for parent {parent_plan_id}: {e}"
            )
            return None

    async def get_versions(self, parent_plan_id: str) -> List[TestPlan]:
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="parent_plan_id",
                            match=MatchValue(value=parent_plan_id)
                        ),
                    ]
                ),
                limit=100,
            )

            test_plans = []
            for point in result[0]:
                if point.payload:
                    test_plans.append(self._payload_to_test_plan(point.payload))

            return test_plans
        except Exception as e:
            logger.error(f"Failed to get test plan versions for parent {parent_plan_id}: {e}")
            return []

