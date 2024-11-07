from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    WORD_DOC = "docx"
    POWERPOINT = "pptx"


class MimeType(str, Enum):
    PDF = "application/pdf"
    WORD_DOC = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    POWERPOINT = (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    
