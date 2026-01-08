from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
import logging

from ..settings import settings

logger = logging.getLogger(__name__)


class QdrantDatabase:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key or None,
        )
        logger.info(f"Connected to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance: Distance = Distance.COSINE,
    ) -> bool:
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )
            logger.info(f"Collection '{collection_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        try:
            collections = self.client.get_collections()
            return collection_name in [c.name for c in collections.collections]
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            return False

    def insert_points(
        self,
        collection_name: str,
        points: List[PointStruct],
    ) -> bool:
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points,
            )
            logger.info(f"Inserted {len(points)} points into '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to insert points into '{collection_name}': {e}")
            return False

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                })
            
            return results
        except Exception as e:
            logger.error(f"Failed to search in '{collection_name}': {e}")
            return []

    def delete_collection(self, collection_name: str) -> bool:
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return False


qdrant_db = QdrantDatabase()
