import logging
from pathlib import Path
from typing import Callable, Dict, Tuple

from docx import Document as DocxDocument
from pypdf import PdfReader

from ..domain.models import DocumentMetadata, FileType

logger = logging.getLogger(__name__)


class DocumentParser:
    def __init__(self):
        self._parsers: Dict[FileType, Callable[[Path], Tuple[str, DocumentMetadata]]] = {
            FileType.PDF: self._parse_pdf,
            FileType.TXT: self._parse_txt,
            FileType.MARKDOWN: self._parse_markdown,
            FileType.DOCX: self._parse_docx,
        }

    def parse(self, file_path: str, file_type: FileType) -> Tuple[str, DocumentMetadata]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_type not in self._parsers:
            raise ValueError(f"Unsupported file type: {file_type}")

        logger.info(f"Parsing document: {file_path} (type: {file_type})")

        parser = self._parsers[file_type]
        content, metadata = parser(path)

        logger.info(f"Successfully parsed document: {file_path}")
        logger.info(f"Content length: {len(content)} characters")
        logger.info(f"Metadata: {metadata}")

        return content, metadata

    def _parse_pdf(self, path: Path) -> Tuple[str, DocumentMetadata]:
        try:
            reader = PdfReader(path)

            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

            content = "\n\n".join(pages_text)

            metadata = DocumentMetadata(
                title=path.stem,
                page_count=len(reader.pages),
                word_count=len(content.split()) if content else 0,
            )

            metadata_info = reader.metadata
            if metadata_info:
                if "/Title" in metadata_info:
                    metadata.title = metadata_info["/Title"]
                if "/Author" in metadata_info:
                    metadata.author = metadata_info["/Author"]

            return content, metadata

        except Exception as e:
            logger.error(f"Error parsing PDF file {path}: {e}")
            raise

    def _parse_txt(self, path: Path) -> Tuple[str, DocumentMetadata]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = DocumentMetadata(
                title=path.stem,
                word_count=len(content.split()) if content else 0,
            )

            return content, metadata

        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="gbk") as f:
                    content = f.read()

                metadata = DocumentMetadata(
                    title=path.stem,
                    word_count=len(content.split()) if content else 0,
                )

                return content, metadata

            except Exception as e:
                logger.error(f"Error parsing TXT file {path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error parsing TXT file {path}: {e}")
            raise

    def _parse_markdown(self, path: Path) -> Tuple[str, DocumentMetadata]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = DocumentMetadata(
                title=path.stem,
                word_count=len(content.split()) if content else 0,
            )

            first_line = content.split("\n")[0]
            if first_line.startswith("#"):
                metadata.title = first_line.lstrip("#").strip()

            return content, metadata

        except Exception as e:
            logger.error(f"Error parsing Markdown file {path}: {e}")
            raise

    def _parse_docx(self, path: Path) -> Tuple[str, DocumentMetadata]:
        try:
            doc = DocxDocument(path)

            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)

            content = "\n\n".join(paragraphs)

            metadata = DocumentMetadata(
                title=path.stem,
                word_count=len(content.split()) if content else 0,
            )

            core_props = doc.core_properties
            if core_props.title:
                metadata.title = core_props.title
            if core_props.author:
                metadata.author = core_props.author

            return content, metadata

        except Exception as e:
            logger.error(f"Error parsing DOCX file {path}: {e}")
            raise

    def get_file_type(self, file_path: str) -> FileType:
        path = Path(file_path)
        extension = path.suffix.lower()

        file_type_map = {
            ".pdf": FileType.PDF,
            ".txt": FileType.TXT,
            ".md": FileType.MARKDOWN,
            ".docx": FileType.DOCX,
        }

        if extension not in file_type_map:
            raise ValueError(f"Unsupported file extension: {extension}")

        return file_type_map[extension]
