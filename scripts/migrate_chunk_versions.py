import asyncio
import logging
from uuid import UUID

from aitechpioneer.domain.models import Chunk, ChunkVersion, ChunkQuality, ChunkMergeRecord
from aitechpioneer.infrastructure.db import QdrantDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


async def migrate_existing_chunks():
    logger.info("Starting migration of existing chunks to version history...")

    vector_database = QdrantDatabase()
    collection_name = "documents"

    try:
        chunks = await vector_database.get_all_chunks(collection_name)
        logger.info(f"Found {len(chunks)} chunks to migrate")

        migrated_count = 0
        skipped_count = 0

        for chunk in chunks:
            try:
                existing_versions = await vector_database.get_chunk_versions(
                    collection_name, chunk.chunk_id
                )

                if existing_versions:
                    logger.info(f"Chunk {chunk.chunk_id} already has version history, skipping")
                    skipped_count += 1
                    continue

                version = ChunkVersion(
                    version_id=UUID(int=0),
                    chunk_id=chunk.chunk_id,
                    version=chunk.version,
                    content=chunk.content,
                    status=chunk.status,
                    quality=chunk.quality,
                    created_at=chunk.created_at,
                    created_by="system",
                )

                await vector_database.insert_chunk_version(collection_name, version)
                logger.info(f"Created initial version for chunk {chunk.chunk_id}")
                migrated_count += 1

            except Exception as e:
                logger.error(f"Error migrating chunk {chunk.chunk_id}: {e}")
                continue

        logger.info(f"Migration completed: {migrated_count} chunks migrated, {skipped_count} skipped")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


async def migrate_merged_from_to_merge_records():
    logger.info("Starting migration of merged_from data to merge records...")

    vector_database = QdrantDatabase()
    collection_name = "documents"

    try:
        chunks = await vector_database.get_all_chunks(collection_name)
        logger.info(f"Found {len(chunks)} chunks to check for merged_from data")

        migrated_count = 0
        skipped_count = 0

        for chunk in chunks:
            try:
                if not chunk.merged_from:
                    continue

                existing_merge_records = await vector_database.get_merge_records(
                    collection_name, chunk_id=chunk.chunk_id, limit=1
                )

                if existing_merge_records:
                    logger.info(f"Chunk {chunk.chunk_id} already has merge records, skipping")
                    skipped_count += 1
                    continue

                source_chunk_ids = []
                for merge_info in chunk.merged_from:
                    source_chunk_ids.append(UUID(merge_info["chunk_id"]))

                merge_record = ChunkMergeRecord(
                    record_id=UUID(int=0),
                    merge_type="MANUAL",
                    source_chunk_ids=source_chunk_ids,
                    target_chunk_id=chunk.chunk_id,
                    created_at=chunk.created_at,
                    created_by="system",
                    is_reversible=True,
                )

                await vector_database.insert_merge_record(collection_name, merge_record)
                logger.info(f"Created merge record for chunk {chunk.chunk_id}")
                migrated_count += 1

            except Exception as e:
                logger.error(f"Error migrating merged_from for chunk {chunk.chunk_id}: {e}")
                continue

        logger.info(f"Migration completed: {migrated_count} merge records created, {skipped_count} skipped")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


async def main():
    logger.info("=" * 80)
    logger.info("Starting data migration for chunk version history")
    logger.info("=" * 80)

    await migrate_existing_chunks()
    await migrate_merged_from_to_merge_records()

    logger.info("=" * 80)
    logger.info("Data migration completed successfully")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
