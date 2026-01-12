import logging
from typing import List

import httpx

from ..domain.ports import EmbeddingServicePort
from ..settings import settings

logger = logging.getLogger(__name__)


class SiliconFlowEmbeddingService(EmbeddingServicePort):
    def __init__(self):
        self._api_key = settings.siliconflow_api_key
        self._model = settings.embedding_model
        self._api_url = settings.embedding_api_url
        self._embedding_size = 1024

    async def generate_embedding(self, text: str) -> List[float]:
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self._api_key:
            raise ValueError("SiliconFlow API key is not configured")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        all_embeddings = []
        batch_size = 32

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {
                "model": self._model,
                "input": batch,
            }

            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self._api_url, json=payload, headers=headers)
                    response.raise_for_status()
                    result = response.json()

                    batch_embeddings = [item["embedding"] for item in result["data"]]
                    all_embeddings.extend(batch_embeddings)
                    logger.info(
                        f"Successfully generated {len(batch_embeddings)} "
                        f"embeddings (batch {i // batch_size + 1})"
                    )

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                raise

        logger.info(f"Successfully generated total {len(all_embeddings)} embeddings")
        return all_embeddings

    def get_embedding_size(self) -> int:
        return self._embedding_size
