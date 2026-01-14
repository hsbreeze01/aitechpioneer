import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from aitechpioneer.domain.models import (
    Chunk,
    ChunkMetadata,
    ChunkMergeRecord,
    ChunkQuality,
    ChunkStatus,
    ChunkType,
    ChunkVersion,
    Document,
    DocumentStatus,
    FileType,
    QARetrievalRecord,
    RetrievedChunk,
)
from aitechpioneer.domain.ports import (
    EmbeddingServicePort,
    LLMServicePort,
    VectorDatabasePort,
)
from aitechpioneer.infrastructure.chunking import ParentChildChunker
from aitechpioneer.infrastructure.document_parser import DocumentParser
from aitechpioneer.infrastructure.embedding import SiliconFlowEmbeddingService
from aitechpioneer.infrastructure.local_embedding import LocalEmbeddingService
from aitechpioneer.infrastructure.qa_storage import qa_retrieval_storage
from aitechpioneer.settings import settings

logger = logging.getLogger(__name__)


def create_embedding_service() -> EmbeddingServicePort:
    if settings.use_local_embedding:
        logger.info(f"Using local embedding service with model: {settings.local_embedding_model}")
        return LocalEmbeddingService(model_name=settings.local_embedding_model)
    else:
        logger.info(f"Using SiliconFlow embedding service with model: {settings.embedding_model}")
        return SiliconFlowEmbeddingService()


class DocumentUploadUseCase:
    def __init__(
        self,
        document_parser: DocumentParser,
        chunker: ParentChildChunker,
        embedding_service: EmbeddingServicePort,
        vector_database: VectorDatabasePort,
    ):
        self.document_parser = document_parser
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_database = vector_database

    async def execute(
        self,
        file_path: str,
        file_type: FileType,
        collection_name: str = "documents",
        display_name: Optional[str] = None,
    ) -> Document:
        logger.info(f"Starting document upload: {file_path}, type: {file_type}, display_name: {display_name}")

        document = None

        try:
            document = Document.create(
                file_name=file_path.split("/")[-1],
                file_type=file_type,
                file_path=file_path,
                display_name=display_name,
            )

            logger.info(f"Created document object: document_id={document.document_id}, file_name={document.file_name}")

            logger.info(f"Parsing document: {file_path}")
            content, metadata = self.document_parser.parse(file_path, file_type)
            document.content = content
            document.metadata = metadata

            logger.info(f"Document parsed successfully, content length: {len(content)}, metadata: {metadata}")

            if not content or len(content.strip()) < 10:
                error_msg = f"Document contains no extractable text or text is too short: {file_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("Chunking document with Parent-Child strategy")
            chunks = self.chunker.chunk_document(
                text=content,
                document_id=document.document_id,
                source_file=file_path,
                file_type=file_type,
                display_name=display_name,
                file_path=file_path,
            )

            logger.info(f"Document chunked into {len(chunks)} chunks")

            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.generate_embeddings(chunk_texts)

            logger.info(f"Generated {len(embeddings)} embeddings, vector size: {len(embeddings[0]) if embeddings else 0}")

            logger.info(f"Storing chunks in vector database: {collection_name}")
            if not await self.vector_database.collection_exists(collection_name):
                await self.vector_database.create_collection(collection_name, len(embeddings[0]))
                logger.info(f"Created collection: {collection_name}")

            for chunk, embedding in zip(chunks, embeddings):
                chunk.update_embedding(embedding)

            logger.info(f"Inserting {len(chunks)} chunks into vector database...")
            await self.vector_database.insert_chunks(collection_name, chunks)

            document.status = DocumentStatus.COMPLETED
            document.updated_at = document.updated_at

            logger.info(f"Document upload completed successfully: document_id={document.document_id}, status={document.status}")
            return document

        except Exception as e:
            logger.error(f"Error during document upload: {e}", exc_info=True)
            if document:
                document.status = DocumentStatus.FAILED
                document.updated_at = document.updated_at
                logger.error(f"Document marked as failed: document_id={document.document_id}")
            raise


class ChunkManagerUseCase:
    def __init__(
        self,
        vector_database: VectorDatabasePort,
        embedding_service: EmbeddingServicePort,
    ):
        self.vector_database = vector_database
        self.embedding_service = embedding_service

    async def update_chunk_status(
        self,
        chunk_id: str,
        status: ChunkStatus,
        collection_name: str = "documents",
    ) -> Chunk:
        logger.info(f"Updating chunk status: {chunk_id} -> {status}")

        try:
            chunk = await self.vector_database.get_chunk_by_id(collection_name, UUID(chunk_id))
            if not chunk:
                raise ValueError(f"Chunk {chunk_id} not found")

            chunk.update_status(status)

            await self.vector_database.update_chunk(collection_name, chunk)

            logger.info(f"Chunk status updated successfully: {chunk_id}")
            return chunk

        except Exception as e:
            logger.error(f"Error updating chunk status: {e}")
            raise

    async def get_chunk(
        self,
        chunk_id: str,
        collection_name: str = "documents",
    ) -> Chunk:
        logger.info(f"Getting chunk: {chunk_id}")

        try:
            chunk = await self.vector_database.get_chunk_by_id(collection_name, UUID(chunk_id))
            if not chunk:
                raise ValueError(f"Chunk {chunk_id} not found")

            return chunk

        except Exception as e:
            logger.error(f"Error getting chunk: {e}")
            raise

    async def merge_chunks(
        self,
        chunk_id_1: str,
        chunk_id_2: str,
        collection_name: str = "documents",
    ) -> Chunk:
        logger.info(f"Merging chunks: {chunk_id_1} + {chunk_id_2}")

        try:
            chunk1 = await self.vector_database.get_chunk_by_id(collection_name, UUID(chunk_id_1))
            chunk2 = await self.vector_database.get_chunk_by_id(collection_name, UUID(chunk_id_2))

            if not chunk1 or not chunk2:
                raise ValueError("One or both chunks not found")

            if chunk1.status != ChunkStatus.ACTIVE or chunk2.status != ChunkStatus.ACTIVE:
                raise ValueError("Can only merge active chunks")

            if chunk1.version != chunk2.version:
                raise ValueError("Cannot merge chunks with different versions")

            merged_content = f"{chunk1.content}\n\n{chunk2.content}"
            logger.info(f"Generating embedding for merged content (length: {len(merged_content)})")
            merged_embedding = await self.embedding_service.generate_embedding(merged_content)
            logger.info(f"Generated embedding with dimension: {len(merged_embedding)}")

            version1 = ChunkVersion(
                chunk_id=chunk1.chunk_id,
                version=chunk1.version,
                content=chunk1.content,
                embedding=chunk1.embedding,
                status=chunk1.status,
                quality=chunk1.quality,
                metadata=chunk1.metadata,
                created_at=chunk1.created_at,
                created_by="system",
            )

            version2 = ChunkVersion(
                chunk_id=chunk2.chunk_id,
                version=chunk2.version,
                content=chunk2.content,
                embedding=chunk2.embedding,
                status=chunk2.status,
                quality=chunk2.quality,
                metadata=chunk2.metadata,
                created_at=chunk2.created_at,
                created_by="system",
            )

            await self.vector_database.insert_chunk_version(collection_name, version1)
            await self.vector_database.insert_chunk_version(collection_name, version2)

            chunk1.status = ChunkStatus.MERGED
            chunk1.inactive_reason = f"Merged with chunk {chunk2.chunk_id}"
            chunk1.is_latest_version = False
            chunk1.updated_at = datetime.utcnow()

            chunk2.status = ChunkStatus.MERGED
            chunk2.inactive_reason = f"Merged with chunk {chunk1.chunk_id}"
            chunk2.is_latest_version = False
            chunk2.updated_at = datetime.utcnow()

            await self.vector_database.update_chunk(collection_name, chunk1)
            await self.vector_database.update_chunk(collection_name, chunk2)

            merged_chunk = Chunk(
                document_id=chunk1.document_id,
                chunk_type=chunk1.chunk_type,
                content=merged_content,
                parent_chunk_id=chunk1.parent_chunk_id,
                start_char=chunk1.start_char,
                end_char=chunk2.end_char,
                status=ChunkStatus.ACTIVE,
                quality=ChunkQuality.HIGH,
                derived_from=[str(chunk1.chunk_id), str(chunk2.chunk_id)],
                merged_from=[
                    {
                        "chunk_id": str(chunk1.chunk_id),
                        "content": chunk1.content,
                        "status": chunk1.status.value,
                        "version": chunk1.version,
                    },
                    {
                        "chunk_id": str(chunk2.chunk_id),
                        "content": chunk2.content,
                        "status": chunk2.status.value,
                        "version": chunk2.version,
                    },
                ],
                previous_version_id=None,
                is_latest_version=True,
            )
            merged_chunk.update_embedding(merged_embedding)

            await self.vector_database.insert_chunks(collection_name, [merged_chunk])

            merge_record = ChunkMergeRecord(
                merge_type="merge",
                source_chunk_ids=[chunk1.chunk_id, chunk2.chunk_id],
                target_chunk_id=merged_chunk.chunk_id,
                previous_state={
                    "chunk1": {
                        "chunk_id": str(chunk1.chunk_id),
                        "content": chunk1.content,
                        "status": chunk1.status.value,
                        "version": chunk1.version,
                    },
                    "chunk2": {
                        "chunk_id": str(chunk2.chunk_id),
                        "content": chunk2.content,
                        "status": chunk2.status.value,
                        "version": chunk2.version,
                    },
                },
                created_by="system",
                is_reversible=True,
            )

            await self.vector_database.insert_merge_record(collection_name, merge_record)

            merged_chunk.merge_record_id = merge_record.record_id
            await self.vector_database.update_chunk(collection_name, merged_chunk)

            logger.info(f"Chunks merged successfully: {merged_chunk.chunk_id}")
            return merged_chunk

        except Exception as e:
            logger.error(f"Error merging chunks: {e}")
            raise

    async def undo_merge(
        self,
        merged_chunk_id: str,
        collection_name: str = "documents",
    ) -> List[Chunk]:
        logger.info(f"Undoing chunk merge: {merged_chunk_id}")

        try:
            merged_chunk = await self.vector_database.get_chunk_by_id(
                collection_name, UUID(merged_chunk_id)
            )
            if not merged_chunk:
                raise ValueError(f"Merged chunk {merged_chunk_id} not found")

            if merged_chunk.status != ChunkStatus.ACTIVE:
                raise ValueError("Can only undo merge on active chunks")

            if not merged_chunk.merge_record_id:
                raise ValueError("This chunk does not have a merge record")

            merge_record = await self.vector_database.get_merge_record(
                collection_name, merged_chunk.merge_record_id
            )
            if not merge_record:
                raise ValueError(f"Merge record {merged_chunk.merge_record_id} not found")

            if not merge_record.is_reversible:
                raise ValueError("This merge operation cannot be undone")

            restored_chunks = []
            for source_chunk_id in merge_record.source_chunk_ids:
                source_chunk = await self.vector_database.get_chunk_by_id(
                    collection_name, source_chunk_id
                )
                if not source_chunk:
                    raise ValueError(f"Source chunk {source_chunk_id} not found")

                if source_chunk.status != ChunkStatus.MERGED:
                    raise ValueError(f"Source chunk {source_chunk_id} is not in MERGED status")

                source_chunk.status = ChunkStatus.ACTIVE
                source_chunk.inactive_reason = None
                source_chunk.is_latest_version = True
                source_chunk.updated_at = datetime.utcnow()

                await self.vector_database.update_chunk(collection_name, source_chunk)
                restored_chunks.append(source_chunk)

            merged_chunk.status = ChunkStatus.INACTIVE
            merged_chunk.inactive_reason = "Merge undone"
            merged_chunk.is_latest_version = False
            merged_chunk.updated_at = datetime.utcnow()

            await self.vector_database.update_chunk(collection_name, merged_chunk)

            undo_record = ChunkMergeRecord(
                merge_type="undo_merge",
                source_chunk_ids=[merged_chunk.chunk_id],
                target_chunk_id=restored_chunks[0].chunk_id,
                previous_state={
                    "merged_chunk": {
                        "chunk_id": str(merged_chunk.chunk_id),
                        "content": merged_chunk.content,
                        "status": merged_chunk.status.value,
                    },
                    "original_merge_record_id": str(merge_record.record_id),
                },
                created_by="system",
                is_reversible=False,
            )

            await self.vector_database.insert_merge_record(collection_name, undo_record)

            logger.info(
                f"Merge undone successfully: {merged_chunk_id}, "
                f"restored {len(restored_chunks)} chunks"
            )
            return restored_chunks

        except Exception as e:
            logger.error(f"Error undoing chunk merge: {e}")
            raise

    async def delete_chunk(
        self,
        chunk_id: str,
        collection_name: str = "documents",
    ) -> bool:
        logger.info(f"Deleting chunk: {chunk_id}")

        try:
            await self.vector_database.delete_chunk(collection_name, UUID(chunk_id))
            logger.info(f"Chunk deleted successfully: {chunk_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting chunk: {e}")
            raise

    async def recommend_merges(
        self,
        collection_name: str = "documents",
        similarity_threshold: float = 0.85,
        max_recommendations: int = 10,
    ) -> List[Dict[str, Any]]:
        logger.info(f"Recommending chunk merges (threshold={similarity_threshold})")

        try:
            all_chunks = await self.vector_database.get_all_chunks(collection_name)
            active_chunks = [c for c in all_chunks if c.status == ChunkStatus.ACTIVE]

            active_chunks.sort(key=lambda x: (x.document_id, x.chunk_index, x.start_char))

            recommendations = []

            for i in range(len(active_chunks) - 1):
                chunk1 = active_chunks[i]
                chunk2 = active_chunks[i + 1]

                if chunk1.document_id != chunk2.document_id:
                    continue

                if chunk1.merged_from or chunk2.merged_from:
                    continue

                if len(chunk1.embedding) == 0 or len(chunk2.embedding) == 0:
                    continue

                similarity = self._calculate_cosine_similarity(chunk1.embedding, chunk2.embedding)

                if similarity >= similarity_threshold:
                    recommendations.append(
                        {
                            "chunk_id_1": str(chunk1.chunk_id),
                            "chunk_id_2": str(chunk2.chunk_id),
                            "document_id": chunk1.document_id,
                            "similarity": similarity,
                            "chunk_1_content": (
                                chunk1.content[:100] + "..."
                                if len(chunk1.content) > 100
                                else chunk1.content
                            ),
                            "chunk_2_content": (
                                chunk2.content[:100] + "..."
                                if len(chunk2.content) > 100
                                else chunk2.content
                            ),
                        }
                    )

            recommendations.sort(key=lambda x: x["similarity"], reverse=True)
            recommendations = recommendations[:max_recommendations]

            logger.info(f"Found {len(recommendations)} merge recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Error recommending merges: {e}")
            raise

    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        import math

        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    async def merge_forward(
        self,
        chunk_id: str,
        collection_name: str = "documents",
    ) -> Chunk:
        logger.info(f"Merging chunk forward: {chunk_id}")

        try:
            current_chunk = await self.vector_database.get_chunk_by_id(
                collection_name, UUID(chunk_id)
            )
            if not current_chunk:
                raise ValueError(f"Chunk {chunk_id} not found")

            all_chunks = await self.vector_database.get_all_chunks(collection_name)
            active_chunks = [c for c in all_chunks if c.status == ChunkStatus.ACTIVE]

            active_chunks.sort(key=lambda x: (x.document_id, x.chunk_index, x.start_char))

            current_index = None
            for i, chunk in enumerate(active_chunks):
                if str(chunk.chunk_id) == chunk_id:
                    current_index = i
                    break

            if current_index is None:
                raise ValueError(f"Chunk {chunk_id} not found in active chunks")

            if current_index >= len(active_chunks) - 1:
                raise ValueError(f"Chunk {chunk_id} is the last chunk, cannot merge forward")

            next_chunk = active_chunks[current_index + 1]

            if next_chunk.document_id != current_chunk.document_id:
                raise ValueError("Next chunk is from a different document")

            return await self.merge_chunks(
                chunk_id_1=chunk_id,
                chunk_id_2=str(next_chunk.chunk_id),
                collection_name=collection_name,
            )

        except Exception as e:
            logger.error(f"Error merging chunk forward: {e}")
            raise

    async def merge_backward(
        self,
        chunk_id: str,
        collection_name: str = "documents",
    ) -> Chunk:
        logger.info(f"Merging chunk backward: {chunk_id}")

        try:
            current_chunk = await self.vector_database.get_chunk_by_id(
                collection_name, UUID(chunk_id)
            )
            if not current_chunk:
                raise ValueError(f"Chunk {chunk_id} not found")

            all_chunks = await self.vector_database.get_all_chunks(collection_name)
            active_chunks = [c for c in all_chunks if c.status == ChunkStatus.ACTIVE]

            active_chunks.sort(key=lambda x: (x.document_id, x.chunk_index, x.start_char))

            current_index = None
            for i, chunk in enumerate(active_chunks):
                if str(chunk.chunk_id) == chunk_id:
                    current_index = i
                    break

            if current_index is None:
                raise ValueError(f"Chunk {chunk_id} not found in active chunks")

            if current_index == 0:
                raise ValueError(f"Chunk {chunk_id} is the first chunk, cannot merge backward")

            prev_chunk = active_chunks[current_index - 1]

            if prev_chunk.document_id != current_chunk.document_id:
                raise ValueError("Previous chunk is from a different document")

            return await self.merge_chunks(
                chunk_id_1=str(prev_chunk.chunk_id),
                chunk_id_2=chunk_id,
                collection_name=collection_name,
            )

        except Exception as e:
            logger.error(f"Error merging chunk backward: {e}")
            raise

    async def semantic_resegment(
        self,
        document_id: str,
        collection_name: str = "documents",
        max_chunk_size: int = 1000,
        min_chunk_size: int = 200,
    ) -> List[Chunk]:
        logger.info(f"Semantic resegmenting chunks for document: {document_id}")

        try:
            all_chunks = await self.vector_database.get_all_chunks(collection_name)
            document_chunks = [
                c
                for c in all_chunks
                if c.document_id == document_id and c.status == ChunkStatus.ACTIVE
            ]

            if not document_chunks:
                raise ValueError(f"No active chunks found for document {document_id}")

            document_chunks.sort(key=lambda x: (x.chunk_index, x.start_char))

            full_content = "\n\n".join([chunk.content for chunk in document_chunks])

            new_chunks = []
            current_chunk_content = ""
            chunk_index = 0

            sentences = full_content.split("。")
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                if len(current_chunk_content) + len(sentence) + 1 <= max_chunk_size:
                    current_chunk_content += sentence + "。"
                else:
                    if current_chunk_content:
                        new_chunk = Chunk(
                            document_id=document_id,
                            chunk_type=ChunkType.CHILD,
                            content=current_chunk_content,
                            parent_chunk_id=None,
                            start_char=0,
                            end_char=len(current_chunk_content),
                            status=ChunkStatus.ACTIVE,
                            quality=ChunkQuality.HIGH,
                            derived_from=[str(c.chunk_id) for c in document_chunks],
                        )
                        new_chunk.chunk_index = chunk_index
                        chunk_index += 1
                        new_chunks.append(new_chunk)

                    current_chunk_content = sentence + "。"

            if current_chunk_content:
                new_chunk = Chunk(
                    document_id=document_id,
                    chunk_type=ChunkType.CHILD,
                    content=current_chunk_content,
                    parent_chunk_id=None,
                    start_char=0,
                    end_char=len(current_chunk_content),
                    status=ChunkStatus.ACTIVE,
                    quality=ChunkQuality.HIGH,
                    derived_from=[str(c.chunk_id) for c in document_chunks],
                )
                new_chunk.chunk_index = chunk_index
                new_chunks.append(new_chunk)

            for new_chunk in new_chunks:
                embedding = await self.embedding_service.generate_embedding(new_chunk.content)
                new_chunk.update_embedding(embedding)

            await self.vector_database.insert_chunks(collection_name, new_chunks)

            for old_chunk in document_chunks:
                old_chunk.status = ChunkStatus.INACTIVE
                old_chunk.inactive_reason = "Replaced by semantic resegmentation"
                await self.vector_database.update_chunk(collection_name, old_chunk)

            logger.info(f"Semantic resegmentation completed: {len(new_chunks)} new chunks created")
            return new_chunks

        except Exception as e:
            logger.error(f"Error during semantic resegmentation: {e}")
            raise

    async def get_chunk_history(
        self,
        chunk_id: str,
        collection_name: str = "documents",
    ) -> Dict[str, Any]:
        logger.info(f"Getting chunk history: {chunk_id}")

        try:
            chunk = await self.vector_database.get_chunk_by_id(collection_name, UUID(chunk_id))
            if not chunk:
                logger.error(f"Chunk {chunk_id} not found")
                raise ValueError(f"Chunk {chunk_id} not found")

            logger.info(f"Retrieving versions for chunk {chunk.chunk_id}")
            versions = await self.vector_database.get_chunk_versions(collection_name, chunk.chunk_id)
            logger.info(f"Found {len(versions)} versions for chunk {chunk.chunk_id}")

            logger.info(f"Retrieving merge records for chunk {chunk.chunk_id}")
            merge_records = await self.vector_database.get_merge_records(
                collection_name, chunk_id=chunk.chunk_id, limit=10
            )
            logger.info(f"Found {len(merge_records)} merge records for chunk {chunk.chunk_id}")

            history = {
                "chunk_id": str(chunk.chunk_id),
                "current_status": chunk.status.value,
                "current_version": chunk.version,
                "is_latest_version": chunk.is_latest_version,
                "versions": [
                    {
                        "version_id": str(v.version_id),
                        "version": v.version,
                        "content": v.content,
                        "status": v.status.value,
                        "quality": v.quality.value,
                        "created_at": v.created_at.isoformat(),
                        "created_by": v.created_by,
                    }
                    for v in versions
                ],
                "merge_records": [
                    {
                        "record_id": str(r.record_id),
                        "merge_type": r.merge_type,
                        "source_chunk_ids": [str(id) for id in r.source_chunk_ids],
                        "target_chunk_id": str(r.target_chunk_id),
                        "created_at": r.created_at.isoformat(),
                        "is_reversible": r.is_reversible,
                    }
                    for r in merge_records
                ],
                "created_at": chunk.created_at.isoformat(),
                "updated_at": chunk.updated_at.isoformat(),
            }

            logger.info(f"Retrieved chunk history for {chunk_id}")
            return history

        except Exception as e:
            logger.error(f"Error getting chunk history: {str(e)}", exc_info=True)
            raise

    async def get_merge_history(
        self,
        collection_name: str = "documents",
        document_id: Optional[str] = None,
        chunk_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        logger.info(f"Getting merge history (document_id={document_id}, chunk_id={chunk_id})")

        try:
            chunk_uuid = UUID(chunk_id) if chunk_id else None
            merge_records = await self.vector_database.get_merge_records(
                collection_name, document_id=document_id, chunk_id=chunk_uuid, limit=limit
            )

            history = [
                {
                    "record_id": str(r.record_id),
                    "merge_type": r.merge_type,
                    "source_chunk_ids": [str(id) for id in r.source_chunk_ids],
                    "target_chunk_id": str(r.target_chunk_id),
                    "created_at": r.created_at.isoformat(),
                    "created_by": r.created_by,
                    "is_reversible": r.is_reversible,
                }
                for r in merge_records
            ]

            logger.info(f"Retrieved {len(history)} merge records")
            return history

        except Exception as e:
            logger.error(f"Error getting merge history: {e}")
            raise


class RAGUseCase:
    def __init__(
        self,
        embedding_service: EmbeddingServicePort,
        vector_database: VectorDatabasePort,
        llm_service: LLMServicePort,
    ):
        self.embedding_service = embedding_service
        self.vector_database = vector_database
        self.llm_service = llm_service

    async def answer_question(
        self,
        question: str,
        collection_name: str = "documents",
        limit: int = 5,
        score_threshold: float = 0.5,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        logger.info(f"Answering question: {question}")

        try:
            logger.info("Generating question embedding")
            question_embedding = await self.embedding_service.generate_embedding(question)

            logger.info(f"Retrieving relevant chunks (limit={limit})")
            chunks_with_scores = await self.vector_database.search_chunks(
                collection_name=collection_name,
                query_vector=question_embedding,
                limit=limit,
                score_threshold=score_threshold,
                status_filter=ChunkStatus.ACTIVE,
            )

            if not chunks_with_scores:
                logger.warning("No relevant chunks found")
                return {
                    "answer": "抱歉，我无法在文档中找到相关信息来回答您的问题。",
                    "sources": [],
                    "model": "unknown",
                    "usage": {},
                }

            logger.info(f"Found {len(chunks_with_scores)} relevant chunks")

            chunks = [chunk for chunk, score in chunks_with_scores]
            scores = [score for chunk, score in chunks_with_scores]

            context = "\n\n".join([chunk.content for chunk in chunks])

            sources = [
                {
                    "chunk_id": str(chunk.chunk_id),
                    "document_id": chunk.document_id,
                    "content": (
                        chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                    ),
                    "score": score,
                }
                for chunk, score in zip(chunks, scores)
            ]

            logger.info("Generating answer using LLM")
            response = await self.llm_service.generate_answer_with_sources(
                question=question,
                context=context,
                sources=sources,
                conversation_history=conversation_history,
            )

            logger.info("Saving QA retrieval record")
            retrieved_chunks = [
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=score,
                    chunk_index=chunk.chunk_index,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                )
                for chunk, score in zip(chunks, scores)
            ]

            qa_record = QARetrievalRecord.create(
                question=question,
                answer=response.get("answer", ""),
                retrieved_chunks=retrieved_chunks,
                model=response.get("model", ""),
                usage=response.get("usage", {}),
            )

            qa_retrieval_storage.save_record(qa_record)

            logger.info("Answer generated successfully")
            return response

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise


class QARetrievalUseCase:
    def __init__(self):
        self.storage = qa_retrieval_storage

    async def get_all_records(self) -> List[QARetrievalRecord]:
        logger.info("Getting all QA retrieval records")
        return self.storage.get_all_records()

    async def get_records_by_chunk(self, chunk_id: str) -> List[QARetrievalRecord]:
        logger.info(f"Getting QA records for chunk: {chunk_id}")
        return self.storage.get_records_by_chunk(chunk_id)

    async def get_records_by_document(self, document_id: str) -> List[QARetrievalRecord]:
        logger.info(f"Getting QA records for document: {document_id}")
        return self.storage.get_records_by_document(document_id)

    async def get_statistics(self) -> Dict[str, Any]:
        logger.info("Getting QA retrieval statistics")
        return self.storage.get_statistics()

    async def delete_old_records(self, days: int = 7) -> int:
        logger.info(f"Deleting old QA records (older than {days} days)")
        return self.storage.delete_old_records(days)
