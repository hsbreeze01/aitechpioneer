# Design: RAG System

## Overview

本设计文档详细说明了 RAG（检索增强生成）系统的技术架构和实现方案。系统采用严格的四层架构模式，确保业务逻辑与技术实现的解耦，支持文档上传、智能分块、向量存储和语义检索等核心功能。

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Interfaces Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web API    │  │   Web UI     │  │     CLI      │      │
│  │   (FastAPI)  │  │ (ui-ux-pro)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ Document Upload  │  │  Chunk Manager  │  │   RAG      │ │
│  │    Use Case      │  │    Use Case     │  │ Use Case   │ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Domain Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Document   │  │    Chunk     │  │   Embedding  │      │
│  │   Models     │  │   Models     │  │   Services   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Vector DB  │  │   LLM        │  │  Embedding   │      │
│  │    Ports     │  │   Ports      │  │   Ports      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Qdrant     │  │  DeepSeek    │  │  BGE Embed   │      │
│  │   Database   │  │    LLM       │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   File       │  │   Document   │  │   Chunking   │      │
│  │   Storage    │  │   Parser     │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Interfaces Layer
- **职责**: 处理外部请求，参数验证，调用应用层
- **组件**:
  - Web API (FastAPI): HTTP RESTful API 端点
  - Web UI: 基于 ui-ux-pro-max-skill 的前端界面
  - CLI: 命令行工具（可选）

#### Application Layer
- **职责**: 用例编排，业务流程控制
- **组件**:
  - Document Upload Use Case: 文档上传和处理流程
  - Chunk Manager Use Case: Chunk 管理操作
  - RAG Use Case: 检索增强生成流程

#### Domain Layer
- **职责**: 业务模型，领域服务，接口定义
- **组件**:
  - Document Models: 文档实体和值对象
  - Chunk Models: Chunk 实体和值对象
  - Embedding Services: 嵌入生成领域服务
  - Vector DB Ports: 向量数据库接口
  - LLM Ports: LLM 服务接口
  - Embedding Ports: 嵌入服务接口

#### Infrastructure Layer
- **职责**: 技术实现，外部系统集成
- **组件**:
  - Qdrant Database: 向量数据库实现
  - DeepSeek LLM: LLM 服务实现
  - BGE Embed Service: 嵌入服务实现
  - File Storage: 文件存储实现
  - Document Parser: 文档解析实现
  - Chunking Service: 分块服务实现

## Component Design

### 1. Document Processing

#### 1.1 Domain Models

```python
# src/aitechpioneer/domain/models.py

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    MD = "md"
    DOCX = "docx"


@dataclass
class DocumentMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    page_count: Optional[int] = None


@dataclass
class Document:
    document_id: str
    filename: str
    file_type: FileType
    file_size: int
    upload_time: datetime
    total_chunks: int = 0
    active_chunks: int = 0
    status: DocumentStatus = DocumentStatus.PROCESSING
    error_message: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    
    @classmethod
    def create(cls, filename: str, file_type: FileType, file_size: int) -> "Document":
        return cls(
            document_id=str(uuid4()),
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            upload_time=datetime.utcnow(),
        )
```

#### 1.2 Chunk Models

```python
# src/aitechpioneer/domain/models.py (continued)

class ChunkStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    INACTIVE = "inactive"


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
    file_type: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    word_count: int = 0
    token_count: int = 0


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    parent_chunk_id: Optional[str]
    content: str
    status: ChunkStatus
    quality: ChunkQuality
    version: int
    chunk_type: ChunkType
    chunk_index: int
    start_char: int
    end_char: int
    embedding: List[float]
    created_at: datetime
    updated_at: datetime
    metadata: ChunkMetadata
    inactive_reason: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        document_id: str,
        content: str,
        chunk_type: ChunkType,
        chunk_index: int,
        start_char: int,
        end_char: int,
        metadata: ChunkMetadata,
        parent_chunk_id: Optional[str] = None,
    ) -> "Chunk":
        return cls(
            chunk_id=str(uuid4()),
            document_id=document_id,
            parent_chunk_id=parent_chunk_id,
            content=content,
            status=ChunkStatus.ACTIVE,
            quality=ChunkQuality.HIGH,
            version=1,
            chunk_type=chunk_type,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            embedding=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=metadata,
        )
    
    def update_status(self, new_status: ChunkStatus, inactive_reason: Optional[str] = None):
        self.status = new_status
        self.inactive_reason = inactive_reason
        self.version += 1
        self.updated_at = datetime.utcnow()
    
    def update_quality(self, new_quality: ChunkQuality):
        self.quality = new_quality
        self.version += 1
        self.updated_at = datetime.utcnow()
```

#### 1.3 Domain Ports

```python
# src/aitechpioneer/domain/ports.py

from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Chunk, Document


class VectorDatabasePort(ABC):
    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int) -> bool:
        pass
    
    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        pass
    
    @abstractmethod
    def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> bool:
        pass
    
    @abstractmethod
    def search_chunks(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_status: Optional[str] = None,
    ) -> List[Chunk]:
        pass
    
    @abstractmethod
    def update_chunk(self, collection_name: str, chunk: Chunk) -> bool:
        pass
    
    @abstractmethod
    def delete_chunk(self, collection_name: str, chunk_id: str) -> bool:
        pass


class EmbeddingServicePort(ABC):
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        pass


class LLMServicePort(ABC):
    @abstractmethod
    def generate_answer(self, question: str, context: str) -> str:
        pass
    
    @abstractmethod
    def generate_answer_with_sources(
        self, question: str, chunks: List[Chunk]
    ) -> tuple[str, List[Chunk]]:
        pass
```

### 2. Chunking Strategy

#### 2.1 Parent-Child Chunking Algorithm

```python
# src/aitechpioneer/infrastructure/chunking.py

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    parent_chunk_size: int = 1750
    parent_chunk_overlap: int = 0
    child_chunk_size: int = 650
    child_chunk_overlap: int = 50


class ParentChildChunker:
    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()
    
    def chunk_document(self, text: str) -> Tuple[List[str], List[str]]:
        parent_chunks = self._create_parent_chunks(text)
        child_chunks = []
        
        for i, parent_chunk in enumerate(parent_chunks):
            parent_children = self._create_child_chunks(parent_chunk)
            child_chunks.extend(parent_children)
        
        return parent_chunks, child_chunks
    
    def _create_parent_chunks(self, text: str) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.config.parent_chunk_size
            
            if end >= text_length:
                chunks.append(text[start:])
                break
            
            end = self._find_natural_boundary(text, end)
            chunks.append(text[start:end])
            start = end - self.config.parent_chunk_overlap
        
        return chunks
    
    def _create_child_chunks(self, parent_text: str) -> List[str]:
        chunks = []
        start = 0
        text_length = len(parent_text)
        
        while start < text_length:
            end = start + self.config.child_chunk_size
            
            if end >= text_length:
                chunks.append(parent_text[start:])
                break
            
            end = self._find_natural_boundary(parent_text, end)
            chunks.append(parent_text[start:end])
            start = end - self.config.child_chunk_overlap
        
        return chunks
    
    def _find_natural_boundary(self, text: str, position: int) -> int:
        if position >= len(text):
            return len(text)
        
        search_range = min(200, len(text) - position)
        for i in range(search_range):
            pos = position + i
            if text[pos] in ['\n\n', '。', '！', '？', '.', '!', '?']:
                return pos + 1
        
        return position
```

### 3. Embedding Service

#### 3.1 BGE Embedding Implementation

```python
# src/aitechpioneer/infrastructure/embedding.py

from typing import List
from sentence_transformers import SentenceTransformer
from ..domain.ports import EmbeddingServicePort


class BGEEmbeddingService(EmbeddingServicePort):
    def __init__(self, model_name: str = "BAAI/bge-base-zh-v1.5"):
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
    
    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        return self._dimension
```

### 4. Vector Database

#### 4.1 Qdrant Implementation

```python
# src/aitechpioneer/infrastructure/qdrant_db.py

from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from ..domain.ports import VectorDatabasePort
from ..domain.models import Chunk
from ..settings import settings


class QdrantVectorDatabase(VectorDatabasePort):
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key or None,
        )
    
    def create_collection(self, collection_name: str, vector_size: int) -> bool:
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return True
        except Exception:
            return False
    
    def collection_exists(self, collection_name: str) -> bool:
        try:
            collections = self.client.get_collections()
            return collection_name in [c.name for c in collections.collections]
        except Exception:
            return False
    
    def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> bool:
        try:
            points = [
                PointStruct(
                    id=chunk.chunk_id,
                    vector=chunk.embedding,
                    payload=self._chunk_to_payload(chunk),
                )
                for chunk in chunks
            ]
            self.client.upsert(collection_name=collection_name, points=points)
            return True
        except Exception:
            return False
    
    def search_chunks(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_status: Optional[str] = None,
    ) -> List[Chunk]:
        try:
            query_filter = None
            if filter_status:
                query_filter = Filter(
                    must=[FieldCondition(key="status", match=MatchValue(value=filter_status))]
                )
            
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )
            
            return [self._payload_to_chunk(hit.payload) for hit in search_result]
        except Exception:
            return []
    
    def update_chunk(self, collection_name: str, chunk: Chunk) -> bool:
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=self._chunk_to_payload(chunk),
                points=[chunk.chunk_id],
            )
            return True
        except Exception:
            return False
    
    def delete_chunk(self, collection_name: str, chunk_id: str) -> bool:
        try:
            self.client.delete(collection_name=collection_name, points_selector=[chunk_id])
            return True
        except Exception:
            return False
    
    def _chunk_to_payload(self, chunk: Chunk) -> dict:
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "parent_chunk_id": chunk.parent_chunk_id,
            "content": chunk.content,
            "status": chunk.status.value,
            "inactive_reason": chunk.inactive_reason,
            "quality": chunk.quality.value,
            "version": chunk.version,
            "chunk_type": chunk.chunk_type.value,
            "chunk_index": chunk.chunk_index,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
            "created_at": chunk.created_at.isoformat(),
            "updated_at": chunk.updated_at.isoformat(),
            "metadata": {
                "source_file": chunk.metadata.source_file,
                "file_type": chunk.metadata.file_type,
                "page_number": chunk.metadata.page_number,
                "section_title": chunk.metadata.section_title,
                "word_count": chunk.metadata.word_count,
                "token_count": chunk.metadata.token_count,
            },
        }
    
    def _payload_to_chunk(self, payload: dict) -> Chunk:
        from datetime import datetime
        from ..domain.models import ChunkMetadata
        
        return Chunk(
            chunk_id=payload["chunk_id"],
            document_id=payload["document_id"],
            parent_chunk_id=payload.get("parent_chunk_id"),
            content=payload["content"],
            status=payload["status"],
            inactive_reason=payload.get("inactive_reason"),
            quality=payload["quality"],
            version=payload["version"],
            chunk_type=payload["chunk_type"],
            chunk_index=payload["chunk_index"],
            start_char=payload["start_char"],
            end_char=payload["end_char"],
            embedding=[],
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
            metadata=ChunkMetadata(**payload["metadata"]),
        )
```

### 5. LLM Service

#### 5.1 DeepSeek LLM Implementation

```python
# src/aitechpioneer/infrastructure/deepseek_llm.py

from typing import List, Tuple
import httpx
from ..domain.ports import LLMServicePort
from ..domain.models import Chunk
from ..settings import settings


class DeepSeekLLMService(LLMServicePort):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文：
{context}

问题：
{question}

回答："""
        
        response = self._call_api(prompt)
        return response
    
    def generate_answer_with_sources(
        self, question: str, chunks: List[Chunk]
    ) -> Tuple[str, List[Chunk]]:
        context = "\n\n".join([chunk.content for chunk in chunks])
        answer = self.generate_answer(question, context)
        return answer, chunks
    
    def _call_api(self, prompt: str) -> str:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"DeepSeek API 调用失败: {e}")
```

### 6. Application Use Cases

#### 6.1 Document Upload Use Case

```python
# src/aitechpioneer/application/use_cases.py

from typing import List
from ..domain.models import Document, Chunk, ChunkType, ChunkMetadata
from ..domain.ports import VectorDatabasePort, EmbeddingServicePort
from ..infrastructure.chunking import ParentChildChunker
from ..infrastructure.document_parser import DocumentParser


class DocumentUploadUseCase:
    def __init__(
        self,
        vector_db: VectorDatabasePort,
        embedding_service: EmbeddingServicePort,
        chunker: ParentChildChunker,
        parser: DocumentParser,
    ):
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.chunker = chunker
        self.parser = parser
    
    def execute(self, file_path: str, filename: str) -> Document:
        text = self.parser.parse(file_path)
        document = Document.create(filename, self.parser.get_file_type(filename), len(text))
        
        parent_chunks, child_chunks = self.chunker.chunk_document(text)
        
        all_chunks = []
        for i, parent_text in enumerate(parent_chunks):
            parent_chunk = self._create_chunk(
                document, parent_text, ChunkType.PARENT, i, 0, len(parent_text), filename
            )
            all_chunks.append(parent_chunk)
            
            for j, child_text in enumerate(child_chunks):
                child_chunk = self._create_chunk(
                    document, child_text, ChunkType.CHILD, j, 0, len(child_text), filename, parent_chunk.chunk_id
                )
                all_chunks.append(child_chunk)
        
        embeddings = self.embedding_service.generate_embeddings_batch([c.content for c in all_chunks])
        for chunk, embedding in zip(all_chunks, embeddings):
            chunk.embedding = embedding
        
        collection_name = f"doc_{document.document_id}"
        if not self.vector_db.collection_exists(collection_name):
            self.vector_db.create_collection(collection_name, self.embedding_service.get_embedding_dimension())
        
        self.vector_db.insert_chunks(collection_name, all_chunks)
        
        document.total_chunks = len(all_chunks)
        document.active_chunks = len(all_chunks)
        document.status = DocumentStatus.COMPLETED
        
        return document
    
    def _create_chunk(
        self,
        document: Document,
        content: str,
        chunk_type: ChunkType,
        chunk_index: int,
        start_char: int,
        end_char: int,
        filename: str,
        parent_chunk_id: str = None,
    ) -> Chunk:
        metadata = ChunkMetadata(
            source_file=filename,
            file_type=document.file_type.value,
            word_count=len(content.split()),
            token_count=len(content) // 2,
        )
        return Chunk.create(
            document_id=document.document_id,
            content=content,
            chunk_type=chunk_type,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            metadata=metadata,
            parent_chunk_id=parent_chunk_id,
        )
```

#### 6.2 Chunk Manager Use Case

```python
# src/aitechpioneer/application/use_cases.py (continued)

class ChunkManagerUseCase:
    def __init__(self, vector_db: VectorDatabasePort):
        self.vector_db = vector_db
    
    def update_chunk_status(
        self, collection_name: str, chunk_id: str, new_status: str, inactive_reason: str = None
    ) -> bool:
        chunk = self._get_chunk(collection_name, chunk_id)
        if not chunk:
            return False
        
        chunk.update_status(new_status, inactive_reason)
        return self.vector_db.update_chunk(collection_name, chunk)
    
    def merge_chunks(self, collection_name: str, chunk_id1: str, chunk_id2: str) -> bool:
        chunk1 = self._get_chunk(collection_name, chunk_id1)
        chunk2 = self._get_chunk(collection_name, chunk_id2)
        
        if not chunk1 or not chunk2:
            return False
        
        merged_content = chunk1.content + "\n\n" + chunk2.content
        chunk1.content = merged_content
        chunk1.end_char = chunk2.end_char
        chunk1.version += 1
        chunk1.updated_at = datetime.utcnow()
        
        self.vector_db.delete_chunk(collection_name, chunk_id2)
        return self.vector_db.update_chunk(collection_name, chunk1)
    
    def delete_chunk(self, collection_name: str, chunk_id: str) -> bool:
        return self.vector_db.delete_chunk(collection_name, chunk_id)
    
    def _get_chunk(self, collection_name: str, chunk_id: str) -> Chunk:
        results = self.vector_db.search_chunks(
            collection_name,
            [0] * 768,
            limit=1,
        )
        for chunk in results:
            if chunk.chunk_id == chunk_id:
                return chunk
        return None
```

#### 6.3 RAG Use Case

```python
# src/aitechpioneer/application/use_cases.py (continued)

class RAGUseCase:
    def __init__(
        self,
        vector_db: VectorDatabasePort,
        embedding_service: EmbeddingServicePort,
        llm_service: LLMServicePort,
    ):
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.llm_service = llm_service
    
    def answer_question(self, collection_name: str, question: str) -> Tuple[str, List[Chunk]]:
        query_embedding = self.embedding_service.generate_embedding(question)
        
        chunks = self.vector_db.search_chunks(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=5,
            filter_status="active",
        )
        
        if not chunks:
            return "未找到相关信息", []
        
        answer, source_chunks = self.llm_service.generate_answer_with_sources(question, chunks)
        return answer, source_chunks
```

### 7. Web API Design

#### 7.1 API Endpoints

```python
# src/aitechpioneer/interfaces/api.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from ..application.use_cases import DocumentUploadUseCase, ChunkManagerUseCase, RAGUseCase


app = FastAPI(title="RAG System API", version="1.0.0")


class ChunkStatusUpdate(BaseModel):
    status: str
    inactive_reason: Optional[str] = None


class ChunkMergeRequest(BaseModel):
    chunk_id1: str
    chunk_id2: str


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        document = document_upload_use_case.execute(file.file, file.filename)
        return {"document_id": document.document_id, "status": document.status.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}/chunks")
async def get_chunks(document_id: str):
    collection_name = f"doc_{document_id}"
    chunks = vector_db.search_chunks(collection_name, [0] * 768, limit=100)
    return {"chunks": [chunk_to_dict(c) for c in chunks]}


@app.put("/api/chunks/{chunk_id}/status")
async def update_chunk_status(chunk_id: str, update: ChunkStatusUpdate):
    collection_name = extract_collection_name(chunk_id)
    success = chunk_manager_use_case.update_chunk_status(
        collection_name, chunk_id, update.status, update.inactive_reason
    )
    if not success:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"status": "updated"}


@app.post("/api/chunks/merge")
async def merge_chunks(request: ChunkMergeRequest):
    collection_name = extract_collection_name(request.chunk_id1)
    success = chunk_manager_use_case.merge_chunks(collection_name, request.chunk_id1, request.chunk_id2)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to merge chunks")
    return {"status": "merged"}


@app.delete("/api/chunks/{chunk_id}")
async def delete_chunk(chunk_id: str):
    collection_name = extract_collection_name(chunk_id)
    success = chunk_manager_use_case.delete_chunk(collection_name, chunk_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"status": "deleted"}


@app.post("/api/questions/answer", response_model=QuestionResponse)
async def answer_question(document_id: str, request: QuestionRequest):
    collection_name = f"doc_{document_id}"
    answer, chunks = rag_use_case.answer_question(collection_name, request.question)
    return QuestionResponse(
        answer=answer,
        sources=[chunk_to_dict(c) for c in chunks]
    )
```

### 8. Web UI Design

#### 8.1 UI Components

基于 ui-ux-pro-max-skill 的设计指导，实现以下 UI 组件：

**主页面布局**:
- 顶部导航栏：文档管理、问答、设置
- 侧边栏：文档列表、筛选器
- 主内容区：动态内容展示

**文档上传组件**:
- 拖拽上传区域
- 文件类型图标
- 上传进度条
- 错误提示

**Chunk 管理组件**:
- Chunk 列表视图
- Chunk 详情面板
- 状态切换按钮
- 合并操作按钮
- 质量标记选择器

**问答组件**:
- 问题输入框
- 答案展示区域
- 来源 Chunk 引用
- 相关性评分显示

#### 8.2 技术栈选择

根据 ui-ux-pro-max-skill 的支持，使用以下技术栈：

**React + Tailwind CSS**
- 使用 React 组件库
- Tailwind CSS 用于样式
- React Query 用于数据获取
- Zustand 用于状态管理
- Tailwind CSS 用于样式
- Alpine.js 用于交互

### 9. Data Flow

#### 9.1 Document Upload Flow

```
用户上传文件
    ↓
Web API 接收文件
    ↓
Document Upload Use Case 处理
    ↓
Document Parser 解析文档
    ↓
Parent-Child Chunker 分块
    ↓
BGE Embedding Service 生成嵌入
    ↓
Qdrant Database 存储向量和元数据
    ↓
返回文档 ID 和状态
```

#### 9.2 Question Answering Flow

```
用户输入问题
    ↓
Web API 接收问题
    ↓
RAG Use Case 处理
    ↓
BGE Embedding Service 生成问题嵌入
    ↓
Qdrant Database 检索相关 Chunk（仅 active 状态）
    ↓
DeepSeek LLM 生成答案
    ↓
返回答案和来源 Chunk
```

#### 9.3 Chunk Management Flow

```
用户查看 Chunk 列表
    ↓
Web API 获取 Chunk 数据
    ↓
Qdrant Database 查询 Chunk
    ↓
用户更新 Chunk 状态
    ↓
Chunk Manager Use Case 处理
    ↓
Qdrant Database 更新 Chunk
    ↓
返回更新结果
```

## Configuration

### Environment Variables

```bash
# .env
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

DEEPSEEK_API_KEY=your_deepseek_api_key

LOG_LEVEL=INFO
DEBUG=False

APP_NAME=aitechpioneer
APP_VERSION=1.0.0
```

### Settings Configuration

```python
# src/aitechpioneer/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""

    deepseek_api_key: str = ""

    log_level: str = "INFO"
    debug: bool = False

    app_name: str = "aitechpioneer"
    app_version: str = "1.0.0"


settings = Settings()
```

## Dependencies

### Python Dependencies

```toml
# pyproject.toml

[project]
name = "aitechpioneer"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-multipart>=0.0.6",
    "qdrant-client>=1.16.0,<1.17.0",
    "sentence-transformers>=2.2.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "pypdf>=3.17.0",
    "python-docx>=1.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.11.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

## Security Considerations

### Input Validation
- 在 Interfaces Layer 进行所有输入验证
- 使用 Pydantic 模型进行数据验证
- 限制文件上传大小和类型

### API Key Management
- 使用环境变量存储 API 密钥
- 不在代码中硬编码密钥
- 定期轮换密钥

### Access Control
- 实现基本的认证机制（未来扩展）
- 限制 API 调用频率
- 记录所有操作日志

## Performance Optimization

### Caching Strategy
- 缓存 Embedding 模型加载
- 缓存文档解析结果
- 使用 Redis 缓存常用查询结果（未来）

### Batch Processing
- 批量生成 Embedding
- 批量插入向量数据
- 批量更新 Chunk 状态

### Connection Pooling
- Qdrant 客户端连接池
- HTTP 客户端连接池
- 数据库连接池（如果使用）

## Monitoring & Logging

### Logging Strategy
- 使用 Python logging 模块
- 分层日志记录（DEBUG, INFO, WARNING, ERROR）
- 结构化日志格式（JSON）
- 敏感信息脱敏

### Metrics Collection
- API 响应时间
- 文档处理时间
- 检索延迟
- LLM 调用次数

### Error Handling
- 统一错误处理中间件
- 详细的错误日志
- 用户友好的错误消息
- 重试机制（网络请求）

## Testing Strategy

### Unit Tests
- 测试 Domain 层的业务逻辑
- 测试 Application 层的用例编排
- 使用 mock 隔离依赖

### Integration Tests
- 测试完整的文档上传流程
- 测试问答流程
- 测试 Chunk 管理操作

### End-to-End Tests
- 测试完整的用户旅程
- 测试 API 端点
- 测试前端交互

## Deployment

### Local Development
```bash
# 安装依赖
pip install -e .

# 启动 Qdrant
docker run -p 6333:6333 qdrant/qdrant:v1.16.3

# 启动 API 服务
uvicorn aitechpioneer.interfaces.api:app --reload

# 启动前端（根据选择的技术栈）
npm run dev
```

### Production Deployment
- 使用 Docker 容器化
- 使用 Nginx 作为反向代理
- 使用 PM2 管理 Node.js 进程（如果使用）
- 配置 SSL/TLS
- 设置监控和告警

## Future Enhancements

### Short-term
- 添加用户认证和授权
- 实现文档版本控制
- 添加高级检索功能（重排序、查询扩展）
- 支持更多文档格式

### Long-term
- 多租户支持
- 实时协作功能
- 多模态文档处理（图片、表格）
- 分布式部署
- 高级分析和统计
