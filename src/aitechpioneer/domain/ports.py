from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from aitechpioneer.domain.models import Chunk, ChunkStatus


class VectorDatabasePort(ABC):
    @abstractmethod
    async def create_collection(self, collection_name: str, vector_size: int) -> None:
        pass

    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    async def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> None:
        pass

    @abstractmethod
    async def search_chunks(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        status_filter: Optional[ChunkStatus] = None,
    ) -> List[tuple[Chunk, float]]:
        pass

    @abstractmethod
    async def update_chunk(self, collection_name: str, chunk: Chunk) -> None:
        pass

    @abstractmethod
    async def delete_chunk(self, collection_name: str, chunk_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_chunks_by_document(self, collection_name: str, document_id: str) -> List[Chunk]:
        pass

    @abstractmethod
    async def get_all_chunks(self, collection_name: str) -> List[Chunk]:
        pass

    @abstractmethod
    async def get_chunk_by_id(self, collection_name: str, chunk_id: UUID) -> Optional[Chunk]:
        pass

    @abstractmethod
    async def get_all_documents(self, collection_name: str) -> List[Dict]:
        pass


class EmbeddingServicePort(ABC):
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def get_embedding_size(self) -> int:
        pass


class LLMServicePort(ABC):
    @abstractmethod
    async def generate_answer(
        self, question: str, context: str, conversation_history: Optional[List[Dict]] = None
    ) -> str:
        pass

    @abstractmethod
    async def generate_answer_with_sources(
        self,
        question: str,
        context: str,
        sources: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        pass
