import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from aitechpioneer.application.use_cases import (
    ChunkManagerUseCase,
    DocumentUploadUseCase,
    QARetrievalUseCase,
    RAGUseCase,
    create_embedding_service,
)
from aitechpioneer.domain.models import ChunkStatus, FileType
from aitechpioneer.infrastructure.chunking import ParentChildChunker
from aitechpioneer.infrastructure.db import QdrantDatabase
from aitechpioneer.infrastructure.deepseek_llm import DeepSeekLLMService
from aitechpioneer.infrastructure.document_parser import DocumentParser

logger = logging.getLogger(__name__)

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
    file_type: str
    uploaded_at: str


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
                file_type=doc["file_type"],
                uploaded_at=doc["uploaded_at"],
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


@app.post(
    "/api/documents/upload",
    response_model=DocumentUploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_document(
    file: UploadFile = File(...),
    file_type: str = Form(...),
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


@app.get(
    "/api/chunks",
    response_model=ChunkListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_all_chunks(collection_name: str = "documents"):
    try:
        _, chunk_manager_use_case, _, _ = get_use_cases()

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
            total=len(chunks),
        )

    except Exception as e:
        logger.error(f"Error getting all chunks: {e}")
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


frontend_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "frontend",
)
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
