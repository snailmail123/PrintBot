import io
from model.document import MimeType
from utils import extract_file_text

class FileProcessor:
    def _process_attachment_by_type(self, content_type: str, content_bytes: bytes):
        """Process attachments based on their MIME type."""
        content_io = io.BytesIO(content_bytes)

        if content_type == MimeType.PDF.value:
            print("Processing PDF attachment.")
            return extract_file_text.pdf_to_text(content_io)
        elif content_type == MimeType.WORD_DOC.value:
            print("Processing Word document attachment.")
            return extract_file_text.docx_to_text(content_io)
        elif content_type == MimeType.POWERPOINT.value:
            print("Processing PowerPoint attachment.")
            return extract_file_text.pptx_to_text(content_io)
        else:
            print(f"Unsupported content type: {content_type}")
            return None