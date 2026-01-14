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

from ..domain.models import Chunk, ChunkMetadata, ChunkMergeRecord, ChunkQuality, ChunkStatus, ChunkType, ChunkVersion, FileType
from ..domain.ports import VectorDatabasePort
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
        logger.debug(f"Generated payload for chunk {chunk.chunk_id}: content_length={len(chunk.content) if chunk.content else 0}, merged_from={chunk.merged_from}, derived_from={chunk.derived_from}, merge_record_id={chunk.merge_record_id}")
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
            merge_record_id=UUID(payload.get("merge_record_id")) if payload.get("merge_record_id") else None,
        )

    async def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> None:
        try:
            logger.info(f"Starting to insert {len(chunks)} chunks into collection '{collection_name}'")
            
            batch_size = 100
            total_inserted = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                points = []
                for chunk in batch:
                    payload = self._chunk_to_payload(chunk)
                    logger.debug(f"Preparing chunk {chunk.chunk_id} for insertion: document_id={chunk.document_id}, content_preview={chunk.content[:50] if chunk.content else 'N/A'}")
                    logger.debug(f"Payload details for chunk {chunk.chunk_id}: status={payload.get('status')}, merged_from={payload.get('merged_from')}, derived_from={payload.get('derived_from')}, content_length={len(payload.get('content', ''))}")
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
                logger.debug(f"Upsert result for batch {i//batch_size + 1}: {upsert_result}")
                total_inserted += len(batch)
                logger.info(f"Inserted batch {total_inserted}/{len(chunks)} chunks into '{collection_name}'")

            logger.info(f"Successfully inserted {len(chunks)} chunks into '{collection_name}'")
            
            # Verify insertion by querying the collection
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )
            logger.info(f"Collection '{collection_name}' now contains {len(result[0])} total points")
            
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
                    points=[PointStruct(id=chunk.chunk_id, vector=chunk.embedding, payload=self._chunk_to_payload(chunk))],
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
            logger.info(f"Found {len(document_list)} unique documents in collection '{collection_name}'")
            
            for doc in document_list:
                logger.debug(f"Document: {doc['document_id']}, file_name={doc['file_name']}, chunk_count={doc['chunk_count']}")
            
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
            logger.error(f"Failed to get document '{document_id}' from '{collection_name}': {e}", exc_info=True)
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

    async def insert_chunk_version(self, collection_name: str, version: ChunkVersion) -> None:
        try:
            point_id = version.version_id
            
            vector = version.embedding
            if not vector or len(vector) == 0:
                vector = [0.0] * 512
                logger.warning(f"Empty embedding for version {version.version_id}, using zero vector")
            
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

    async def get_merge_record(self, collection_name: str, record_id: UUID) -> Optional[ChunkMergeRecord]:
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
