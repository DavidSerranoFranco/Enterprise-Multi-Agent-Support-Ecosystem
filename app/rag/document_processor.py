from typing import List, Dict, Optional
import PyPDF2
from docx import Document as DocxDocument
from bs4 import BeautifulSoup
import io
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes different types of documents for indexing"""

    @staticmethod
    async def process_pdf(file_content: bytes) -> str:
        """Extracts text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise

    @staticmethod
    async def process_docx(file_content: bytes) -> str:
        """Extracts text from DOCX"""
        try:
            doc = DocxDocument(io.BytesIO(file_content))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
            raise

    @staticmethod
    async def process_html(content: str) -> str:
        """Extracts text from HTML"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error processing HTML: {e}")
            raise

    @staticmethod
    async def process_text(content: str) -> str:
        """Processes plain text"""
        return content.strip()

    async def process(
        self,
        content: bytes | str,
        file_type: str
    ) -> str:
        """Processes document according to its type"""
        processors = {
            "pdf": self.process_pdf,
            "docx": self.process_docx,
            "html": self.process_html,
            "txt": self.process_text,
            "text": self.process_text,
        }

        processor = processors.get(file_type.lower())
        if not processor:
            raise ValueError(f"Unsupported file type: {file_type}")

        if isinstance(content, str) and file_type in ["txt", "text", "html"]:
            return await processor(content)
        elif isinstance(content, bytes):
            return await processor(content)
        else:
            raise ValueError("Invalid content for the file type")

# Global instance
document_processor = DocumentProcessor()