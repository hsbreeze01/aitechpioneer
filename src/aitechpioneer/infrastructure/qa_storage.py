import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import QARetrievalRecord

logger = logging.getLogger(__name__)


class QARetrievalStorage:
    def __init__(self, storage_dir: str = "data/qa_records"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"QA Retrieval Storage initialized at: {self.storage_dir}")

    def _get_record_path(self, record_id: str) -> Path:
        return self.storage_dir / f"{record_id}.json"

    def save_record(self, record: QARetrievalRecord) -> None:
        try:
            record_data = {
                "record_id": str(record.record_id),
                "question": record.question,
                "answer": record.answer,
                "retrieved_chunks": [
                    {
                        "chunk_id": str(chunk.chunk_id),
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "score": chunk.score,
                        "chunk_index": chunk.chunk_index,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                    }
                    for chunk in record.retrieved_chunks
                ],
                "model": record.model,
                "usage": record.usage,
                "created_at": record.created_at.isoformat(),
            }

            record_path = self._get_record_path(str(record.record_id))
            with open(record_path, "w", encoding="utf-8") as f:
                json.dump(record_data, f, ensure_ascii=False, indent=2)

            logger.info(f"QA record saved: {record.record_id}")
        except Exception as e:
            logger.error(f"Failed to save QA record: {e}")
            raise

    def get_record(self, record_id: str) -> Optional[QARetrievalRecord]:
        try:
            record_path = self._get_record_path(record_id)
            if not record_path.exists():
                return None

            with open(record_path, "r", encoding="utf-8") as f:
                record_data = json.load(f)

            from ..domain.models import RetrievedChunk

            retrieved_chunks = [
                RetrievedChunk(
                    chunk_id=chunk["chunk_id"],
                    document_id=chunk["document_id"],
                    content=chunk["content"],
                    score=chunk["score"],
                    chunk_index=chunk["chunk_index"],
                    start_char=chunk["start_char"],
                    end_char=chunk["end_char"],
                )
                for chunk in record_data["retrieved_chunks"]
            ]

            record = QARetrievalRecord(
                record_id=record_data["record_id"],
                question=record_data["question"],
                answer=record_data["answer"],
                retrieved_chunks=retrieved_chunks,
                model=record_data["model"],
                usage=record_data["usage"],
                created_at=datetime.fromisoformat(record_data["created_at"]),
            )

            return record
        except Exception as e:
            logger.error(f"Failed to get QA record: {e}")
            return None

    def get_all_records(self) -> List[QARetrievalRecord]:
        try:
            records = []
            for record_file in self.storage_dir.glob("*.json"):
                record_id = record_file.stem
                record = self.get_record(record_id)
                if record:
                    records.append(record)

            records.sort(key=lambda x: x.created_at, reverse=True)
            return records
        except Exception as e:
            logger.error(f"Failed to get all QA records: {e}")
            return []

    def get_records_by_chunk(self, chunk_id: str) -> List[QARetrievalRecord]:
        try:
            all_records = self.get_all_records()
            filtered_records = [
                record
                for record in all_records
                if any(str(chunk.chunk_id) == chunk_id for chunk in record.retrieved_chunks)
            ]
            return filtered_records
        except Exception as e:
            logger.error(f"Failed to get records by chunk: {e}")
            return []

    def get_records_by_document(self, document_id: str) -> List[QARetrievalRecord]:
        try:
            all_records = self.get_all_records()
            filtered_records = [
                record
                for record in all_records
                if any(chunk.document_id == document_id for chunk in record.retrieved_chunks)
            ]
            return filtered_records
        except Exception as e:
            logger.error(f"Failed to get records by document: {e}")
            return []

    def delete_old_records(self, days: int = 7) -> int:
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = 0

            for record_file in self.storage_dir.glob("*.json"):
                try:
                    with open(record_file, "r", encoding="utf-8") as f:
                        record_data = json.load(f)

                    created_at = datetime.fromisoformat(record_data["created_at"])
                    if created_at < cutoff_date:
                        record_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old QA record: {record_file.stem}")
                except Exception as e:
                    logger.warning(f"Failed to process record file {record_file}: {e}")
                    continue

            logger.info(f"Deleted {deleted_count} old QA records (older than {days} days)")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to delete old QA records: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        try:
            all_records = self.get_all_records()

            chunk_usage = {}
            document_usage = {}

            for record in all_records:
                for chunk in record.retrieved_chunks:
                    chunk_id = str(chunk.chunk_id)
                    document_id = chunk.document_id

                    chunk_usage[chunk_id] = chunk_usage.get(chunk_id, 0) + 1
                    document_usage[document_id] = document_usage.get(document_id, 0) + 1

            top_chunks = sorted(chunk_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            top_documents = sorted(document_usage.items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                "total_records": len(all_records),
                "top_chunks": top_chunks,
                "top_documents": top_documents,
            }
        except Exception as e:
            logger.error(f"Failed to get QA statistics: {e}")
            return {
                "total_records": 0,
                "top_chunks": [],
                "top_documents": [],
            }


qa_retrieval_storage = QARetrievalStorage()
