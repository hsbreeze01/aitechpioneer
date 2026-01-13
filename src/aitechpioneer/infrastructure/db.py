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
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..domain.models import Chunk, ChunkMetadata, ChunkQuality, ChunkStatus, ChunkType, FileType
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
        return {
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
        )

    async def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> None:
        try:
            points = []
            for chunk in chunks:
                point = PointStruct(
                    id=chunk.chunk_id,
                    vector=chunk.embedding,
                    payload=self._chunk_to_payload(chunk),
                )
                points.append(point)

            self.client.upsert(
                collection_name=collection_name,
                points=points,
            )
            logger.info(f"Inserted {len(chunks)} chunks into '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to insert chunks into '{collection_name}': {e}")
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
            self.client.set_payload(
                collection_name=collection_name,
                payload=self._chunk_to_payload(chunk),
                points=[chunk.chunk_id],
            )
            if chunk.embedding:
                self.client.upsert(
                    collection_name=collection_name,
                    points=[PointStruct(id=chunk.chunk_id, vector=chunk.embedding)],
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
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )

            documents = {}
            for point in result[0]:
                if not point.payload:
                    continue
                document_id = point.payload.get("document_id")
                if document_id:
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
                    documents[document_id]["chunk_count"] += 1

            return list(documents.values())
        except Exception as e:
            logger.error(f"Failed to get documents from '{collection_name}': {e}")
            return []

    async def get_document(
        self, collection_name: str, document_id: str
    ) -> Optional[Dict[str, Any]]:
        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000,
            )

            for point in result[0]:
                if not point.payload:
                    continue
                if point.payload.get("document_id") == document_id:
                    return {
                        "document_id": document_id,
                        "file_name": point.payload.get("metadata", {}).get("source_file", ""),
                        "display_name": point.payload.get("metadata", {}).get("display_name"),
                        "file_path": point.payload.get("metadata", {}).get("file_path"),
                        "file_type": point.payload.get("metadata", {}).get("file_type", ""),
                        "uploaded_at": point.payload.get("created_at", ""),
                    }
            return None
        except Exception as e:
            logger.error(f"Failed to get document '{document_id}' from '{collection_name}': {e}")
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
                chunk = self._payload_to_chunk(point.payload, UUID(str(point.id)))
                chunks.append(chunk)

            chunks.sort(key=lambda x: (x.document_id, x.chunk_index, x.start_char))

            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks from '{collection_name}': {e}")
            return []


qdrant_db = QdrantDatabase()
