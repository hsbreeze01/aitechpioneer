from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..domain.models import Chunk, ChunkMetadata, ChunkType, FileType


@dataclass
class ChunkConfig:
    parent_chunk_size: int = 400
    parent_chunk_overlap: int = 0
    child_chunk_size: int = 150
    child_chunk_overlap: int = 20


class ParentChildChunker:
    def __init__(self, config: ChunkConfig = ChunkConfig()):
        self.config = config

    def chunk_document(
        self,
        text: str,
        document_id: str,
        source_file: str,
        file_type: FileType,
    ) -> List[Chunk]:
        parent_chunk_dicts = self._create_parent_chunks(text)
        all_chunks = []

        for i, parent_chunk_dict in enumerate(parent_chunk_dicts):
            parent_chunk_obj = self._create_chunk(
                document_id=document_id,
                content=parent_chunk_dict["content"],
                chunk_type=ChunkType.PARENT,
                chunk_index=i,
                start_char=parent_chunk_dict["start_char"],
                end_char=parent_chunk_dict["end_char"],
                source_file=source_file,
                file_type=file_type,
            )
            all_chunks.append(parent_chunk_obj)

            child_chunk_dicts = self._create_child_chunks(
                parent_chunk_dict, str(parent_chunk_obj.chunk_id)
            )
            for j, child_chunk_dict in enumerate(child_chunk_dicts):
                child_chunk_obj = self._create_chunk(
                    document_id=document_id,
                    content=child_chunk_dict["content"],
                    chunk_type=ChunkType.CHILD,
                    chunk_index=j,
                    start_char=child_chunk_dict["start_char"],
                    end_char=child_chunk_dict["end_char"],
                    source_file=source_file,
                    file_type=file_type,
                    parent_chunk_id=str(parent_chunk_obj.chunk_id),
                )
                all_chunks.append(child_chunk_obj)

        return all_chunks

    def _create_parent_chunks(self, text: str) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.config.parent_chunk_size

            if end >= text_length:
                chunk_dict = {
                    "content": text[start:],
                    "start_char": start,
                    "end_char": text_length,
                }
                chunks.append(chunk_dict)
                break

            end = self._find_natural_boundary(text, end)
            chunk_dict = {
                "content": text[start:end],
                "start_char": start,
                "end_char": end,
            }
            chunks.append(chunk_dict)
            start = end - self.config.parent_chunk_overlap

        return chunks

    def _create_child_chunks(
        self, parent_chunk_dict: Dict[str, Any], parent_id: str
    ) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        text_length = len(parent_chunk_dict["content"])

        while start < text_length:
            end = start + self.config.child_chunk_size

            if end >= text_length:
                chunk_dict = {
                    "content": parent_chunk_dict["content"][start:],
                    "start_char": parent_chunk_dict["start_char"] + start,
                    "end_char": parent_chunk_dict["start_char"] + text_length,
                }
                chunks.append(chunk_dict)
                break

            end = self._find_natural_boundary(parent_chunk_dict["content"], end)
            chunk_dict = {
                "content": parent_chunk_dict["content"][start:end],
                "start_char": parent_chunk_dict["start_char"] + start,
                "end_char": parent_chunk_dict["start_char"] + end,
            }
            chunks.append(chunk_dict)
            start = end - self.config.child_chunk_overlap

        return chunks

    def _find_natural_boundary(self, text: str, position: int) -> int:
        if position >= len(text):
            return len(text)

        search_range = min(200, len(text) - position)
        for i in range(search_range):
            pos = position + i
            if text[pos] in ["\n\n", "。", "！", "？", ".", "!", "?"]:
                return pos + 1

        return position

    def _create_chunk(
        self,
        document_id: str,
        content: str,
        chunk_type: ChunkType,
        chunk_index: int,
        start_char: int,
        end_char: int,
        source_file: str,
        file_type: FileType,
        parent_chunk_id: Optional[str] = None,
    ) -> Chunk:
        metadata = ChunkMetadata(
            source_file=source_file,
            file_type=file_type,
            word_count=len(content.split()) if content else 0,
        )

        return Chunk(
            document_id=document_id,
            content=content,
            chunk_type=chunk_type,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            metadata=metadata,
            parent_chunk_id=parent_chunk_id,
        )
