from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    MARKDOWN = "md"
    DOCX = "docx"


@dataclass
class DocumentMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    page_count: Optional[int] = None
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    file_name: str
    file_type: FileType
    file_path: str
    display_name: Optional[str] = None
    document_id: str = field(default_factory=lambda: str(uuid4()))
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        file_name: str,
        file_type: FileType,
        file_path: str,
        display_name: Optional[str] = None,
        content: str = "",
    ) -> "Document":
        metadata = DocumentMetadata(
            title=display_name or file_name,
            word_count=len(content.split()) if content else 0,
        )
        return cls(
            file_name=file_name,
            file_type=file_type,
            file_path=file_path,
            display_name=display_name,
            content=content,
            metadata=metadata,
        )

    def update_status(self, status: DocumentStatus) -> None:
        self.status = status
        self.updated_at = datetime.utcnow()

    def update_content(self, content: str) -> None:
        self.content = content
        self.metadata.word_count = len(content.split()) if content else 0
        self.updated_at = datetime.utcnow()


class ChunkStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    INACTIVE = "inactive"
    MERGED = "merged"
    SPLIT = "split"


class ChunkQuality(str, Enum):
    HIGH = "high"
    REPAIRED = "repaired"
    SUSPECT = "suspect"


class ChunkType(str, Enum):
    PARENT = "parent"
    CHILD = "child"


@dataclass
class ChunkMetadata:
    source_file: str
    file_type: FileType
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    word_count: int = 0
    token_count: int = 0
    display_name: Optional[str] = None
    file_path: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: UUID = field(default_factory=uuid4)
    document_id: str = ""
    parent_chunk_id: Optional[str] = None
    content: str = ""
    status: ChunkStatus = ChunkStatus.ACTIVE
    inactive_reason: Optional[str] = None
    quality: ChunkQuality = ChunkQuality.HIGH
    version: int = 1
    chunk_type: ChunkType = ChunkType.CHILD
    chunk_index: int = 0
    start_char: int = 0
    end_char: int = 0
    embedding: List[float] = field(default_factory=list)
    metadata: Optional[ChunkMetadata] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    merged_from: Optional[List[Dict[str, Any]]] = None
    derived_from: Optional[List[str]] = None
    previous_version_id: Optional[UUID] = None
    is_latest_version: bool = True
    merge_record_id: Optional[UUID] = None

    @classmethod
    def create(
        cls,
        document_id: str,
        content: str,
        chunk_type: ChunkType,
        chunk_index: int,
        start_char: int,
        end_char: int,
        parent_chunk_id: Optional[str] = None,
        metadata: Optional[ChunkMetadata] = None,
    ) -> "Chunk":
        return cls(
            document_id=document_id,
            content=content,
            chunk_type=chunk_type,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            parent_chunk_id=parent_chunk_id,
            metadata=metadata,
        )

    def update_status(self, status: ChunkStatus, inactive_reason: Optional[str] = None) -> None:
        self.status = status
        self.inactive_reason = inactive_reason
        self.version += 1
        self.updated_at = datetime.utcnow()

    def update_quality(self, quality: ChunkQuality) -> None:
        self.quality = quality
        self.version += 1
        self.updated_at = datetime.utcnow()

    def update_embedding(self, embedding: List[float]) -> None:
        self.embedding = embedding
        self.updated_at = datetime.utcnow()

    def update_content(self, content: str) -> None:
        self.content = content
        self.version += 1
        self.updated_at = datetime.utcnow()
        if self.metadata:
            self.metadata.word_count = len(content.split()) if content else 0


@dataclass
class RetrievedChunk:
    chunk_id: UUID
    document_id: str
    content: str
    score: float
    chunk_index: int
    start_char: int
    end_char: int


@dataclass
class ChunkVersion:
    version_id: UUID = field(default_factory=uuid4)
    chunk_id: UUID = field(default_factory=uuid4)
    version: int = 1
    content: str = ""
    embedding: List[float] = field(default_factory=list)
    status: ChunkStatus = ChunkStatus.ACTIVE
    quality: ChunkQuality = ChunkQuality.HIGH
    metadata: Optional[ChunkMetadata] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"


@dataclass
class ChunkMergeRecord:
    record_id: UUID = field(default_factory=uuid4)
    merge_type: str = ""
    source_chunk_ids: List[UUID] = field(default_factory=list)
    target_chunk_id: UUID = field(default_factory=uuid4)
    previous_state: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    is_reversible: bool = True


@dataclass
class QARetrievalRecord:
    record_id: UUID = field(default_factory=uuid4)
    question: str = ""
    answer: str = ""
    retrieved_chunks: List[RetrievedChunk] = field(default_factory=list)
    model: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)
    user_feedback: Optional["UserFeedback"] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        question: str,
        answer: str,
        retrieved_chunks: List[RetrievedChunk],
        model: str = "",
        usage: Optional[Dict[str, Any]] = None,
        user_feedback: Optional["UserFeedback"] = None,
    ) -> "QARetrievalRecord":
        return cls(
            question=question,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            model=model,
            usage=usage or {},
            user_feedback=user_feedback,
        )


class TaskStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionStatus(str, Enum):
    DISCOVERED = "discovered"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EffectRating(str, Enum):
    BETTER = "better"
    SAME = "same"
    WORSE = "worse"


class QuestionType(str, Enum):
    FACTUAL = "factual"
    EXPLANATORY = "explanatory"
    OPERATIONAL = "operational"
    COMPARATIVE = "comparative"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Scope(str, Enum):
    SINGLE_DOCUMENT = "single_document"
    MULTI_DOCUMENT = "multi_document"
    GLOBAL = "global"


class RootCause(str, Enum):
    CHUNK_TOO_SMALL = "chunk_too_small"
    CHUNK_TOO_LARGE = "chunk_too_large"
    BOUNDARY_ISSUE = "boundary_issue"
    INCOMPLETE_CONTENT = "incomplete_content"
    OTHER = "other"


@dataclass
class QuestionClassification:
    type: QuestionType = QuestionType.FACTUAL
    severity: Severity = Severity.LOW
    scope: Scope = Scope.SINGLE_DOCUMENT
    root_cause: RootCause = RootCause.OTHER
    priority: int = 1


@dataclass
class UserFeedback:
    rating: Optional[int] = None
    comment: Optional[str] = None
    is_helpful: Optional[bool] = None
    is_resolved: Optional[bool] = None


@dataclass
class RetrievalParams:
    top_k: int = 5
    score_threshold: float = 0.5
    retrieval_time: float = 0.0


@dataclass
class GenerationParams:
    model: str = ""
    temperature: float = 0.7
    generation_time: float = 0.0


@dataclass
class RetrievedChunkInfo:
    chunk_id: str
    content: str
    score: float
    document_id: str


@dataclass
class StatusHistory:
    status: str
    timestamp: datetime
    operator: str
    comment: Optional[str] = None


@dataclass
class VerificationRecord:
    verification_id: str = field(default_factory=lambda: str(uuid4()))
    question_id: str = ""
    test_plan_id: str = ""
    original_answer: str = ""
    new_answer: str = ""
    original_chunks: List[RetrievedChunkInfo] = field(default_factory=list)
    new_chunks: List[RetrievedChunkInfo] = field(default_factory=list)
    similarity_score: float = 0.0
    chunk_changes: Dict[str, int] = field(default_factory=dict)
    score_changes: Dict[str, float] = field(default_factory=dict)
    effect_rating: EffectRating = EffectRating.SAME
    user_comment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DecisionRecord:
    decision_id: str = field(default_factory=lambda: str(uuid4()))
    test_plan_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    decision: str = ""
    reason: str = ""
    operator: str = ""


@dataclass
class Question:
    question_id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    answer: str = ""
    retrieved_chunks: List[RetrievedChunkInfo] = field(default_factory=list)
    retrieval_params: RetrievalParams = field(default_factory=RetrievalParams)
    generation_params: GenerationParams = field(default_factory=GenerationParams)
    classification: QuestionClassification = field(default_factory=QuestionClassification)
    related_questions: List[str] = field(default_factory=list)
    related_chunks: List[str] = field(default_factory=list)
    status: QuestionStatus = QuestionStatus.DISCOVERED
    status_history: List[StatusHistory] = field(default_factory=list)
    user_feedback: UserFeedback = field(default_factory=UserFeedback)
    is_optimization_target: bool = False
    optimization_target_since: Optional[datetime] = None
    verification_records: List[VerificationRecord] = field(default_factory=list)
    decision_records: List[DecisionRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationOperation:
    operation_type: str = ""
    chunk_ids: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationSummary:
    operations: List[OptimizationOperation] = field(default_factory=list)
    affected_documents: List[str] = field(default_factory=list)
    affected_chunks: List[str] = field(default_factory=list)


@dataclass
class ImpactAnalysis:
    affected_questions: int = 0
    improvement_rate: float = 0.0
    regression_rate: float = 0.0


@dataclass
class RiskAssessment:
    level: str = "low"
    potential_issues: List[str] = field(default_factory=list)


@dataclass
class CostAssessment:
    remaining_issues: int = 0
    estimated_effort: str = "low"


@dataclass
class Decision:
    recommendation: str = ""
    reason: str = ""
    impact_analysis: ImpactAnalysis = field(default_factory=ImpactAnalysis)
    risk_assessment: RiskAssessment = field(default_factory=RiskAssessment)
    cost_assessment: CostAssessment = field(default_factory=CostAssessment)
    next_actions: List[str] = field(default_factory=list)


@dataclass
class TestPlanResults:
    total: int = 0
    better: int = 0
    same: int = 0
    worse: int = 0
    failed: int = 0


@dataclass
class TestPlan:
    test_plan_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: Optional[str] = None
    version: int = 1
    parent_plan_id: Optional[str] = None
    question_ids: List[str] = field(default_factory=list)
    optimization_summary: OptimizationSummary = field(default_factory=OptimizationSummary)
    status: str = "draft"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: TestPlanResults = field(default_factory=TestPlanResults)
    decision: Decision = field(default_factory=Decision)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""


@dataclass
class UploadTask:
    task_id: str = field(default_factory=lambda: str(uuid4()))
    file_name: str = ""
    file_type: FileType = FileType.TXT
    display_name: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        file_name: str,
        file_type: FileType,
        display_name: Optional[str] = None,
    ) -> "UploadTask":
        return cls(
            file_name=file_name,
            file_type=file_type,
            display_name=display_name,
        )

    def update_status(
        self,
        status: TaskStatus,
        progress: int = 0,
        error_message: Optional[str] = None,
    ) -> None:
        self.status = status
        self.progress = progress
        self.error_message = error_message
        self.updated_at = datetime.utcnow()

    def set_document_id(self, document_id: str) -> None:
        self.document_id = document_id
        self.updated_at = datetime.utcnow()
