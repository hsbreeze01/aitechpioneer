from typing import List

from .models import Chunk
from .ports import EmbeddingServicePort


class EmbeddingService:
    def __init__(self, embedding_port: EmbeddingServicePort):
        self._embedding_port = embedding_port

    async def generate_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        return await self._embedding_port.generate_embedding(text)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            raise ValueError("No valid texts provided")

        return await self._embedding_port.generate_embeddings(valid_texts)

    async def generate_chunk_embedding(self, chunk: Chunk) -> Chunk:
        if not chunk.content:
            raise ValueError("Chunk content cannot be empty")

        embedding = await self.generate_embedding(chunk.content)
        chunk.update_embedding(embedding)
        return chunk

    async def generate_chunks_embeddings(self, chunks: List[Chunk]) -> List[Chunk]:
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks if chunk.content]
        if not texts:
            raise ValueError("No valid chunks provided")

        embeddings = await self.generate_embeddings(texts)

        result_chunks = []
        embedding_index = 0
        for chunk in chunks:
            if chunk.content:
                chunk.update_embedding(embeddings[embedding_index])
                embedding_index += 1
            result_chunks.append(chunk)

        return result_chunks

    def get_embedding_size(self) -> int:
        return self._embedding_port.get_embedding_size()
