import logging
import os
from typing import List

from sentence_transformers import SentenceTransformer

from ..domain.ports import EmbeddingServicePort

logger = logging.getLogger(__name__)


class LocalEmbeddingService(EmbeddingServicePort):
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self._model_name = model_name
        self._model = None
        self._embedding_size = 512

        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        local_model_path = os.path.join(project_root, "models", "bge-small-zh-v1.5")

        if os.path.exists(local_model_path):
            self._model_path = local_model_path
            logger.info(f"Using local model from: {local_model_path}")
        else:
            self._model_path = model_name
            logger.info(f"Using remote model: {model_name}")

    def _load_model(self):
        if self._model is None:
            logger.info(f"Loading model: {self._model_path}")
            self._model = SentenceTransformer(self._model_path)
            logger.info("Model loaded successfully")

    async def generate_embedding(self, text: str) -> List[float]:
        logger.info(f"Generating embedding for text (length: {len(text)})")
        embeddings = await self.generate_embeddings([text])
        logger.info(f"Generated embedding with dimension: {len(embeddings[0])}")
        return embeddings[0]

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._load_model()

        if self._model is None:
            raise RuntimeError("Model failed to load")

        try:
            embeddings = self._model.encode(
                texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
            )

            result = embeddings.tolist()
            logger.info(f"Successfully generated {len(result)} embeddings using local model")
            return result
        except Exception as e:
            logger.error(f"Error generating embeddings with local model: {e}")
            raise

    def get_embedding_size(self) -> int:
        return self._embedding_size
