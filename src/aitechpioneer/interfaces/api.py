import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from aitechpioneer.application.use_cases import (
    ChunkManagerUseCase,
    DocumentUploadUseCase,
    QARetrievalUseCase,
    RAGUseCase,
    create_embedding_service,
)
from aitechpioneer.domain.models import ChunkStatus, FileType, TaskStatus
from aitechpioneer.infrastructure.chunking import ParentChildChunker
from aitechpioneer.infrastructure.db import QdrantDatabase
from aitechpioneer.infrastructure.deepseek_llm import DeepSeekLLMService
from aitechpioneer.infrastructure.document_parser import DocumentParser
from aitechpioneer.infrastructure.task_manager import task_manager
from aitechpioneer.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation System with Qdrant and DeepSeek",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "frontend",
)
if os.path.exists(frontend_dir):
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(frontend_dir, "static")),
        name="static",
    )


@app.get("/api", include_in_schema=False)
async def api_redirect() -> dict[str, Any]:
    return {"message": "API endpoints are available at /api/*"}


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    status: str
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    file_name: str
    display_name: Optional[str] = None
    file_type: str
    file_path: Optional[str] = None
    uploaded_at: str
    chunk_count: int = 0


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int


class ChunkInfo(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_type: str
    status: str
    quality: str
    version: int
    start_index: int
    end_index: int
    derived_from: Optional[List[str]] = None
    merged_from: Optional[List[Dict[str, Any]]] = None


class ChunkListResponse(BaseModel):
    document_id: str
    chunks: List[ChunkInfo]
    total: int


class ChunkStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New chunk status: active, deprecated, or inactive")


class ChunkStatusUpdateResponse(BaseModel):
    chunk_id: str
    status: str
    message: str


class ChunkMergeRequest(BaseModel):
    chunk_id_1: str = Field(..., description="First chunk ID to merge")
    chunk_id_2: str = Field(..., description="Second chunk ID to merge")


class ChunkMergeResponse(BaseModel):
    chunk_id: str
    message: str


class ChunkMergePreviewRequest(BaseModel):
    chunk_id_1: str = Field(..., description="First chunk ID to merge")
    chunk_id_2: str = Field(..., description="Second chunk ID to merge")


class ChunkMergePreviewResponse(BaseModel):
    chunk_1_content: str
    chunk_2_content: str
    merged_content: str
    chunk_1_id: str
    chunk_2_id: str


class ChunkUndoMergeRequest(BaseModel):
    merged_chunk_id: str = Field(..., description="Merged chunk ID to undo")


class ChunkUndoMergeResponse(BaseModel):
    message: str
    restored_chunk_ids: List[str]


class ChunkRecommendMergeRequest(BaseModel):
    similarity_threshold: Optional[float] = Field(
        0.85,
        description="Minimum similarity threshold for recommendations",
        ge=0.0,
        le=1.0,
    )
    max_recommendations: Optional[int] = Field(
        10, description="Maximum number of recommendations", ge=1, le=50
    )


class ChunkRecommendMergeResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    message: str


class ChunkDeleteResponse(BaseModel):
    chunk_id: str
    message: str


class ChunkMergeForwardResponse(BaseModel):
    chunk_id: str
    message: str
    merged_with: str


class ChunkMergeBackwardResponse(BaseModel):
    chunk_id: str
    message: str
    merged_with: str


class SemanticResegmentRequest(BaseModel):
    max_chunk_size: Optional[int] = Field(1000, description="Maximum chunk size", ge=200, le=5000)
    min_chunk_size: Optional[int] = Field(200, description="Minimum chunk size", ge=50, le=1000)


class SemanticResegmentResponse(BaseModel):
    document_id: str
    message: str
    chunks_created: int
    chunks_deactivated: int


class ChunkVersionInfo(BaseModel):
    version_id: str
    version: int
    content: str
    status: str
    quality: str
    created_at: str
    created_by: str


class ChunkMergeRecordInfo(BaseModel):
    record_id: str
    merge_type: str
    source_chunk_ids: List[str]
    target_chunk_id: str
    created_at: str
    is_reversible: bool


class ChunkHistoryResponse(BaseModel):
    chunk_id: str
    current_status: str
    current_version: int
    is_latest_version: bool
    versions: List[ChunkVersionInfo]
    merge_records: List[ChunkMergeRecordInfo]
    created_at: str
    updated_at: str


class MergeHistoryResponse(BaseModel):
    records: List[ChunkMergeRecordInfo]
    total: int


class ChunkVersionsResponse(BaseModel):
    chunk_id: str
    versions: List[ChunkVersionInfo]
    total: int


class QARetrievalRecordInfo(BaseModel):
    record_id: str
    question: str
    answer: str
    retrieved_chunks: List[Dict[str, Any]]
    model: str
    created_at: str


class QARetrievalListResponse(BaseModel):
    records: List[QARetrievalRecordInfo]
    total: int


class UploadTaskInfo(BaseModel):
    task_id: str
    file_name: str
    file_type: str
    display_name: Optional[str] = None
    status: str
    progress: int
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class UploadTaskListResponse(BaseModel):
    tasks: List[UploadTaskInfo]
    total: int


class UploadTaskCreateResponse(BaseModel):
    task_id: str
    file_name: str
    status: str
    message: str


class QARetrievalStatisticsResponse(BaseModel):
    total_records: int
    total_questions: int
    total_chunks_retrieved: int
    avg_chunks_per_question: float
    oldest_record: Optional[str]
    newest_record: Optional[str]


class QuestionRequest(BaseModel):
    question: str = Field(..., description="Question to answer")
    collection_name: Optional[str] = Field("documents", description="Collection name to search")
    limit: Optional[int] = Field(5, description="Number of chunks to retrieve", ge=1, le=20)
    score_threshold: Optional[float] = Field(
        0.5, description="Minimum similarity score", ge=0.0, le=1.0
    )
    conversation_history: Optional[List[Dict]] = Field(
        None, description="Conversation history for context"
    )


class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    model: str
    usage: Dict[str, int]


class ErrorResponse(BaseModel):
    error: str
    detail: str


def get_use_cases() -> tuple[
    DocumentUploadUseCase,
    ChunkManagerUseCase,
    RAGUseCase,
    QARetrievalUseCase,
]:
    document_parser = DocumentParser()
    chunker = ParentChildChunker()
    embedding_service = create_embedding_service()
    vector_database = QdrantDatabase()
    llm_service = DeepSeekLLMService()

    document_upload_use_case = DocumentUploadUseCase(
        document_parser=document_parser,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_database=vector_database,
    )

    chunk_manager_use_case = ChunkManagerUseCase(
        vector_database=vector_database,
        embedding_service=embedding_service,
    )

    rag_use_case = RAGUseCase(
        embedding_service=embedding_service,
        vector_database=vector_database,
        llm_service=llm_service,
    )

    qa_retrieval_use_case = QARetrievalUseCase()

    return document_upload_use_case, chunk_manager_use_case, rag_use_case, qa_retrieval_use_case


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "documents": "/api/documents",
            "chunks": "/api/chunks",
            "questions": "/api/questions",
        },
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get(
    "/api/documents",
    response_model=DocumentListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_documents(collection_name: str = "documents") -> DocumentListResponse:
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        documents = await chunk_manager_use_case.vector_database.get_all_documents(collection_name)

        document_infos = [
            DocumentInfo(
                document_id=doc["document_id"],
                file_name=doc["file_name"],
                display_name=doc.get("display_name"),
                file_type=doc["file_type"],
                file_path=doc.get("file_path"),
                uploaded_at=doc["uploaded_at"],
                chunk_count=doc["chunk_count"],
            )
            for doc in documents
        ]

        return DocumentListResponse(
            documents=document_infos,
            total=len(document_infos),
        )
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/documents/{document_id}",
    response_model=DocumentInfo,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_document(document_id: str, collection_name: str = "documents"):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        document = await chunk_manager_use_case.vector_database.get_document(
            collection_name, document_id
        )

        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        return DocumentInfo(
            document_id=document["document_id"],
            file_name=document["file_name"],
            display_name=document.get("display_name"),
            file_type=document["file_type"],
            file_path=document.get("file_path"),
            uploaded_at=document["uploaded_at"],
            chunk_count=document.get("chunk_count", 0),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/documents/upload",
    response_model=DocumentUploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_document(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    display_name: Optional[str] = Form(None),
    collection_name: str = Form("documents"),
):
    try:
        if file_type not in [ft.value for ft in FileType]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Must be one of: {[ft.value for ft in FileType]}",
            )

        file_type_enum = FileType(file_type)

        document_upload_use_case, _, _, _ = get_use_cases()

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            document = await document_upload_use_case.execute(
                file_path=temp_file_path,
                file_type=file_type_enum,
                collection_name=collection_name,
                display_name=display_name,
            )

            return DocumentUploadResponse(
                document_id=document.document_id,
                file_name=document.file_name,
                file_type=document.file_type.value,
                status=document.status.value,
                message="Document uploaded and processed successfully",
            )

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/documents/upload-async",
    response_model=UploadTaskCreateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_document_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    display_name: Optional[str] = Form(None),
    collection_name: str = Form("documents"),
):
    try:
        if file_type not in [ft.value for ft in FileType]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Must be one of: {[ft.value for ft in FileType]}",
            )

        file_type_enum = FileType(file_type)

        content = await file.read()

        task = await task_manager.create_task(
            file_name=file.filename or "unknown",
            file_type=file_type_enum,
            display_name=display_name,
        )

        logger.info(f"Created upload task {task.task_id} for file {file.filename}")

        logger.info(f"About to add background task for {task.task_id}...")
        background_tasks.add_task(
            _process_upload_task,
            task_id=task.task_id,
            file_content=content,
            file_name=file.filename or "unknown",
            file_type=file_type_enum,
            display_name=display_name,
            collection_name=collection_name,
        )
        logger.info(f"Background task added successfully for {task.task_id}")

        return UploadTaskCreateResponse(
            task_id=task.task_id,
            file_name=task.file_name,
            status=task.status.value,
            message="Upload task created successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating upload task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_upload_task(
    task_id: str,
    file_content: bytes,
    file_name: str,
    file_type: FileType,
    display_name: Optional[str],
    collection_name: str,
):
    import os
    import tempfile

    temp_file_path = None
    try:
        logger.info(f"[{task_id}] Starting upload task processing")
        
        await task_manager.update_task(task_id, TaskStatus.UPLOADING, progress=10)
        logger.info(f"[{task_id}] Task status updated to UPLOADING")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type.value}")
        temp_file.write(file_content)
        temp_file.close()
        temp_file_path = temp_file.name
        logger.info(f"[{task_id}] Temp file created: {temp_file_path}")

        await task_manager.update_task(task_id, TaskStatus.PROCESSING, progress=30)
        logger.info(f"[{task_id}] Task status updated to PROCESSING")

        document_upload_use_case, _, _, _ = get_use_cases()
        logger.info(f"[{task_id}] Got document_upload_use_case")

        logger.info(f"[{task_id}] Calling document_upload_use_case.execute...")
        document = await document_upload_use_case.execute(
            file_path=temp_file_path,
            file_type=file_type,
            collection_name=collection_name,
            display_name=display_name,
        )
        logger.info(f"[{task_id}] Document upload completed, document_id: {document.document_id}")

        await task_manager.update_task(
            task_id,
            TaskStatus.COMPLETED,
            progress=100,
            document_id=document.document_id,
        )
        logger.info(f"[{task_id}] Task status updated to COMPLETED")

        logger.info(f"Upload task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"[{task_id}] Error processing upload task: {e}", exc_info=True)
        await task_manager.update_task(
            task_id,
            TaskStatus.FAILED,
            error_message=str(e),
        )
        logger.error(f"[{task_id}] Task status updated to FAILED: {str(e)}")

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"[{task_id}] Temp file removed: {temp_file_path}")
            except Exception as e:
                logger.error(f"[{task_id}] Error removing temp file {temp_file_path}: {e}")


@app.get(
    "/api/upload-tasks",
    response_model=UploadTaskListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_upload_tasks():
    try:
        tasks = await task_manager.get_all_tasks()
        _, chunk_manager_use_case, _, _ = get_use_cases()

        valid_tasks = []
        for task in tasks:
            if task.status == TaskStatus.COMPLETED and task.document_id:
                try:
                    document = await chunk_manager_use_case.vector_database.get_document(
                        "documents", task.document_id
                    )
                    if not document:
                        logger.warning(f"Task {task.task_id} marked as completed but document {task.document_id} not found in database")
                        await task_manager.update_task(
                            task.task_id,
                            TaskStatus.FAILED,
                            error_message=f"Document {task.document_id} not found in database"
                        )
                        task.status = TaskStatus.FAILED
                        task.error_message = f"Document {task.document_id} not found in database"
                except Exception as e:
                    logger.error(f"Error validating document for task {task.task_id}: {e}")

            valid_tasks.append(task)

        task_infos = [
            UploadTaskInfo(
                task_id=task.task_id,
                file_name=task.file_name,
                file_type=task.file_type.value,
                display_name=task.display_name,
                status=task.status.value,
                progress=task.progress,
                document_id=task.document_id,
                error_message=task.error_message,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
            )
            for task in valid_tasks
        ]

        return UploadTaskListResponse(
            tasks=task_infos,
            total=len(task_infos),
        )

    except Exception as e:
        logger.error(f"Error getting upload tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/upload-tasks/{task_id}",
    response_model=UploadTaskInfo,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_upload_task(task_id: str):
    try:
        task = await task_manager.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return UploadTaskInfo(
            task_id=task.task_id,
            file_name=task.file_name,
            file_type=task.file_type.value,
            display_name=task.display_name,
            status=task.status.value,
            progress=task.progress,
            document_id=task.document_id,
            error_message=task.error_message,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upload task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/api/upload-tasks/{task_id}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_upload_task(task_id: str):
    try:
        deleted = await task_manager.delete_task(task_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return {"message": f"Task {task_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting upload task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/upload-tasks/{task_id}/retry",
    response_model=UploadTaskInfo,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def retry_upload_task(task_id: str):
    try:
        task = await task_manager.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if task.status != TaskStatus.FAILED:
            raise HTTPException(status_code=400, detail="Only failed tasks can be retried")

        await task_manager.retry_task(task_id)

        retried_task = await task_manager.get_task(task_id)

        if not retried_task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found after retry")

        return UploadTaskInfo(
            task_id=retried_task.task_id,
            file_name=retried_task.file_name,
            file_type=retried_task.file_type.value,
            display_name=retried_task.display_name,
            status=retried_task.status.value,
            progress=retried_task.progress,
            document_id=retried_task.document_id,
            error_message=retried_task.error_message,
            created_at=retried_task.created_at.isoformat(),
            updated_at=retried_task.updated_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying upload task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _test_background_task(message: str):
    print(f"[TEST PRINT] Background task executed: {message}")
    logger.info(f"[TEST] Background task executed: {message}")


@app.get(
    "/api/test-background",
    responses={500: {"model": ErrorResponse}},
)
async def test_background(background_tasks: BackgroundTasks):
    try:
        logger.info("[TEST] About to add background task...")
        background_tasks.add_task(_test_background_task, "Test message")
        logger.info("[TEST] Background task added successfully")
        return {"message": "Background task added"}
    except Exception as e:
        logger.error(f"[TEST] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/chunks",
    response_model=ChunkListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_all_chunks(collection_name: str = "documents", chunk_id: Optional[str] = None):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        if chunk_id:
            chunk_uuid = UUID(chunk_id)
            chunk = await chunk_manager_use_case.vector_database.get_chunk_by_id(collection_name, chunk_uuid)
            
            if not chunk:
                raise HTTPException(status_code=404, detail=f"Chunk with ID {chunk_id} not found")
            
            chunk_infos = [
                ChunkInfo(
                    chunk_id=str(chunk.chunk_id),
                    document_id=chunk.document_id,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type.value,
                    status=chunk.status.value,
                    quality=chunk.quality.value,
                    version=chunk.version,
                    start_index=chunk.start_char,
                    end_index=chunk.end_char,
                    derived_from=chunk.derived_from,
                    merged_from=chunk.merged_from,
                )
            ]
        else:
            chunks = await chunk_manager_use_case.vector_database.get_all_chunks(collection_name)

            chunk_infos = [
                ChunkInfo(
                    chunk_id=str(chunk.chunk_id),
                    document_id=chunk.document_id,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type.value,
                    status=chunk.status.value,
                    quality=chunk.quality.value,
                    version=chunk.version,
                    start_index=chunk.start_char,
                    end_index=chunk.end_char,
                    derived_from=chunk.derived_from,
                    merged_from=chunk.merged_from,
                )
                for chunk in chunks
            ]

        return ChunkListResponse(
            document_id="all",
            chunks=chunk_infos,
            total=len(chunk_infos),
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid chunk_id format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid chunk_id format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/documents/{document_id}/chunks",
    response_model=ChunkListResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_document_chunks(document_id: str, collection_name: str = "documents"):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        chunks = await chunk_manager_use_case.vector_database.get_chunks_by_document(
            collection_name, document_id
        )

        chunk_infos = [
            ChunkInfo(
                chunk_id=str(chunk.chunk_id),
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_type=chunk.chunk_type.value,
                status=chunk.status.value,
                quality=chunk.quality.value,
                version=chunk.version,
                start_index=chunk.start_char,
                end_index=chunk.end_char,
                derived_from=chunk.derived_from,
                merged_from=chunk.merged_from,
            )
            for chunk in chunks
        ]

        return ChunkListResponse(
            document_id=document_id,
            chunks=chunk_infos,
            total=len(chunks),
        )

    except Exception as e:
        logger.error(f"Error getting document chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/api/chunks/{chunk_id}/status",
    response_model=ChunkStatusUpdateResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def update_chunk_status(
    chunk_id: str,
    request: ChunkStatusUpdateRequest,
    collection_name: str = "documents",
):
    try:
        if request.status not in [cs.value for cs in ChunkStatus]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[cs.value for cs in ChunkStatus]}",
            )

        status_enum = ChunkStatus(request.status)

        _, chunk_manager_use_case, _, _ = get_use_cases()

        chunk = await chunk_manager_use_case.update_chunk_status(
            chunk_id=chunk_id,
            status=status_enum,
            collection_name=collection_name,
        )

        return ChunkStatusUpdateResponse(
            chunk_id=str(chunk.chunk_id),
            status=chunk.status.value,
            message="Chunk status updated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chunk status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/chunks/merge/preview",
    response_model=ChunkMergePreviewResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def preview_merge_chunks(
    request: ChunkMergePreviewRequest,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        chunk_1 = await chunk_manager_use_case.get_chunk(
            chunk_id=request.chunk_id_1,
            collection_name=collection_name,
        )

        chunk_2 = await chunk_manager_use_case.get_chunk(
            chunk_id=request.chunk_id_2,
            collection_name=collection_name,
        )

        merged_content = chunk_1.content + "\n" + chunk_2.content

        return ChunkMergePreviewResponse(
            chunk_1_content=chunk_1.content,
            chunk_2_content=chunk_2.content,
            merged_content=merged_content,
            chunk_1_id=str(chunk_1.chunk_id),
            chunk_2_id=str(chunk_2.chunk_id),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing chunk merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/chunks/merge",
    response_model=ChunkMergeResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def merge_chunks(
    request: ChunkMergeRequest,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        merged_chunk = await chunk_manager_use_case.merge_chunks(
            chunk_id_1=request.chunk_id_1,
            chunk_id_2=request.chunk_id_2,
            collection_name=collection_name,
        )

        return ChunkMergeResponse(
            chunk_id=str(merged_chunk.chunk_id),
            message="Chunks merged successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error merging chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/chunks/merge/undo",
    response_model=ChunkUndoMergeResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def undo_merge_chunks(
    request: ChunkUndoMergeRequest,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        restored_chunks = await chunk_manager_use_case.undo_merge(
            merged_chunk_id=request.merged_chunk_id,
            collection_name=collection_name,
        )

        return ChunkUndoMergeResponse(
            message="Merge undone successfully",
            restored_chunk_ids=[str(chunk.chunk_id) for chunk in restored_chunks],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error undoing chunk merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/chunks/recommend-merges",
    response_model=ChunkRecommendMergeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def recommend_merges(
    request: ChunkRecommendMergeRequest,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        recommendations = await chunk_manager_use_case.recommend_merges(
            collection_name=collection_name,
            similarity_threshold=request.similarity_threshold or 0.85,
            max_recommendations=request.max_recommendations or 10,
        )

        return ChunkRecommendMergeResponse(
            message=f"Found {len(recommendations)} merge recommendations",
            recommendations=recommendations,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recommending merges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/api/chunks/{chunk_id}",
    response_model=ChunkDeleteResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_chunk(
    chunk_id: str,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        await chunk_manager_use_case.delete_chunk(
            chunk_id=chunk_id,
            collection_name=collection_name,
        )

        return ChunkDeleteResponse(
            chunk_id=chunk_id,
            message="Chunk deleted successfully",
        )

    except Exception as e:
        logger.error(f"Error deleting chunk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/questions/answer",
    response_model=QuestionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def answer_question(request: QuestionRequest):
    try:
        _, _, rag_use_case, qa_retrieval_use_case = get_use_cases()

        response = await rag_use_case.answer_question(
            question=request.question,
            collection_name=request.collection_name or "documents",
            limit=request.limit or 5,
            score_threshold=request.score_threshold or 0.7,
            conversation_history=request.conversation_history,
        )

        return QuestionResponse(
            answer=response["answer"],
            sources=response["sources"],
            model=response["model"],
            usage=response["usage"],
        )

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/chunks/{chunk_id}/merge-forward",
    response_model=ChunkMergeForwardResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def merge_chunk_forward(
    chunk_id: str,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        merged_chunk = await chunk_manager_use_case.merge_forward(
            chunk_id=chunk_id,
            collection_name=collection_name,
        )

        return ChunkMergeForwardResponse(
            chunk_id=str(merged_chunk.chunk_id),
            message="Chunk merged forward successfully",
            merged_with=str(merged_chunk.derived_from[-1]) if merged_chunk.derived_from else "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error merging chunk forward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/chunks/{chunk_id}/merge-backward",
    response_model=ChunkMergeBackwardResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def merge_chunk_backward(
    chunk_id: str,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        merged_chunk = await chunk_manager_use_case.merge_backward(
            chunk_id=chunk_id,
            collection_name=collection_name,
        )

        return ChunkMergeBackwardResponse(
            chunk_id=str(merged_chunk.chunk_id),
            message="Chunk merged backward successfully",
            merged_with=str(merged_chunk.derived_from[-1]) if merged_chunk.derived_from else "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error merging chunk backward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/documents/{document_id}/semantic-resegment",
    response_model=SemanticResegmentResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def semantic_resegment_document(
    document_id: str,
    request: SemanticResegmentRequest,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        chunks = await chunk_manager_use_case.semantic_resegment(
            document_id=document_id,
            collection_name=collection_name,
            max_chunk_size=request.max_chunk_size or 1000,
            min_chunk_size=request.min_chunk_size or 200,
        )

        active_chunks = [c for c in chunks if c.status == ChunkStatus.ACTIVE]
        deactivated_chunks = [c for c in chunks if c.status == ChunkStatus.INACTIVE]

        return SemanticResegmentResponse(
            document_id=document_id,
            message="Document resegmented successfully",
            chunks_created=len(active_chunks),
            chunks_deactivated=len(deactivated_chunks),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resegmenting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/chunks/{chunk_id}/history",
    response_model=ChunkHistoryResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_chunk_history(
    chunk_id: str,
    collection_name: str = "documents",
):
    try:
        logger.info(f"API: Getting chunk history for chunk_id={chunk_id}, collection_name={collection_name}")
        _, chunk_manager_use_case, _, _ = get_use_cases()

        history = await chunk_manager_use_case.get_chunk_history(
            chunk_id=chunk_id,
            collection_name=collection_name,
        )

        versions = [
            ChunkVersionInfo(
                version_id=v["version_id"],
                version=v["version"],
                content=v["content"],
                status=v["status"],
                quality=v["quality"],
                created_at=v["created_at"],
                created_by=v["created_by"],
            )
            for v in history["versions"]
        ]

        merge_records = [
            ChunkMergeRecordInfo(
                record_id=r["record_id"],
                merge_type=r["merge_type"],
                source_chunk_ids=r["source_chunk_ids"],
                target_chunk_id=r["target_chunk_id"],
                created_at=r["created_at"],
                is_reversible=r["is_reversible"],
            )
            for r in history["merge_records"]
        ]

        return ChunkHistoryResponse(
            chunk_id=history["chunk_id"],
            current_status=history["current_status"],
            current_version=history["current_version"],
            is_latest_version=history["is_latest_version"],
            versions=versions,
            merge_records=merge_records,
            created_at=history["created_at"],
            updated_at=history["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chunk history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/merge-history",
    response_model=MergeHistoryResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_merge_history(
    document_id: Optional[str] = None,
    chunk_id: Optional[str] = None,
    limit: int = 100,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        history = await chunk_manager_use_case.get_merge_history(
            collection_name=collection_name,
            document_id=document_id,
            chunk_id=chunk_id,
            limit=limit,
        )

        records = [
            ChunkMergeRecordInfo(
                record_id=r["record_id"],
                merge_type=r["merge_type"],
                source_chunk_ids=r["source_chunk_ids"],
                target_chunk_id=r["target_chunk_id"],
                created_at=r["created_at"],
                is_reversible=r["is_reversible"],
            )
            for r in history
        ]

        return MergeHistoryResponse(
            records=records,
            total=len(records),
        )

    except Exception as e:
        logger.error(f"Error getting merge history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/chunks/{chunk_id}/versions",
    response_model=ChunkVersionsResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_chunk_versions(
    chunk_id: str,
    collection_name: str = "documents",
):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

        history = await chunk_manager_use_case.get_chunk_history(
            chunk_id=chunk_id,
            collection_name=collection_name,
        )

        versions = [
            ChunkVersionInfo(
                version_id=v["version_id"],
                version=v["version"],
                content=v["content"],
                status=v["status"],
                quality=v["quality"],
                created_at=v["created_at"],
                created_by=v["created_by"],
            )
            for v in history["versions"]
        ]

        return ChunkVersionsResponse(
            chunk_id=history["chunk_id"],
            versions=versions,
            total=len(versions),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chunk versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/qa/records",
    response_model=QARetrievalListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_qa_records():
    try:
        _, _, _, qa_retrieval_use_case = get_use_cases()

        records = await qa_retrieval_use_case.get_all_records()

        record_infos = [
            QARetrievalRecordInfo(
                record_id=str(record.record_id),
                question=record.question,
                answer=record.answer,
                retrieved_chunks=[
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
                model=record.model,
                created_at=record.created_at.isoformat(),
            )
            for record in records
        ]

        return QARetrievalListResponse(
            records=record_infos,
            total=len(record_infos),
        )

    except Exception as e:
        logger.error(f"Error getting QA records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/qa/records/chunk/{chunk_id}",
    response_model=QARetrievalListResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_qa_records_by_chunk(chunk_id: str):
    try:
        _, _, _, qa_retrieval_use_case = get_use_cases()

        records = await qa_retrieval_use_case.get_records_by_chunk(chunk_id)

        record_infos = [
            QARetrievalRecordInfo(
                record_id=str(record.record_id),
                question=record.question,
                answer=record.answer,
                retrieved_chunks=[
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
                model=record.model,
                created_at=record.created_at.isoformat(),
            )
            for record in records
        ]

        return QARetrievalListResponse(
            records=record_infos,
            total=len(record_infos),
        )

    except Exception as e:
        logger.error(f"Error getting QA records for chunk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/qa/records/document/{document_id}",
    response_model=QARetrievalListResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_qa_records_by_document(document_id: str):
    try:
        _, _, _, qa_retrieval_use_case = get_use_cases()

        records = await qa_retrieval_use_case.get_records_by_document(document_id)

        record_infos = [
            QARetrievalRecordInfo(
                record_id=str(record.record_id),
                question=record.question,
                answer=record.answer,
                retrieved_chunks=[
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
                model=record.model,
                created_at=record.created_at.isoformat(),
            )
            for record in records
        ]

        return QARetrievalListResponse(
            records=record_infos,
            total=len(record_infos),
        )

    except Exception as e:
        logger.error(f"Error getting QA records for document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/qa/statistics",
    response_model=QARetrievalStatisticsResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_qa_statistics():
    try:
        _, _, _, qa_retrieval_use_case = get_use_cases()

        stats = await qa_retrieval_use_case.get_statistics()

        return QARetrievalStatisticsResponse(
            total_records=stats.get("total_records", 0),
            total_questions=stats.get("total_questions", 0),
            total_chunks_retrieved=stats.get("total_chunks_retrieved", 0),
            avg_chunks_per_question=stats.get("avg_chunks_per_question", 0.0),
            oldest_record=stats.get("oldest_record"),
            newest_record=stats.get("newest_record"),
        )

    except Exception as e:
        logger.error(f"Error getting QA statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/api/qa/records/cleanup",
    responses={500: {"model": ErrorResponse}},
)
async def cleanup_old_qa_records(days: int = 7):
    try:
        _, _, _, qa_retrieval_use_case = get_use_cases()

        deleted_count = await qa_retrieval_use_case.delete_old_records(days=days)

        return {
            "message": f"Deleted {deleted_count} old QA records",
            "deleted_count": deleted_count,
            "days": days,
        }

    except Exception as e:
        logger.error(f"Error cleaning up QA records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/test/create-invalid-task",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
)
async def create_invalid_task():
    try:
        task = await task_manager.create_task(
            file_name="AI 原生应用架构白皮书.pdf",
            file_type=FileType.PDF,
            display_name="AI 原生应用架构白皮书"
        )
        
        await task_manager.update_task(
            task.task_id,
            TaskStatus.COMPLETED,
            progress=100,
            document_id="20996bee-e154-42d7-9c2a-23e909e6ba2a"
        )
        
        return {
            "message": "Invalid task created successfully",
            "task_id": task.task_id,
            "document_id": "20996bee-e154-42d7-9c2a-23e909e6ba2a"
        }
        
    except Exception as e:
        logger.error(f"Error creating invalid task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if os.path.exists(frontend_dir):
    app.mount(
        "/",
        StaticFiles(directory=frontend_dir, html=True),
        name="frontend",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
