"""Custom exceptions for LegalAI."""


class LegalAIException(Exception):
    """Base exception for LegalAI."""
    def __init__(self, message: str, code: str = "LEGAL_AI_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DocumentProcessingError(LegalAIException):
    """Error during document processing."""
    def __init__(self, message: str):
        super().__init__(message, code="DOC_PROCESSING_ERROR")


class OCRError(LegalAIException):
    """Error during OCR processing."""
    def __init__(self, message: str):
        super().__init__(message, code="OCR_ERROR")


class SectionPredictionError(LegalAIException):
    """Error during legal section prediction."""
    def __init__(self, message: str):
        super().__init__(message, code="SECTION_PREDICTION_ERROR")


class RAGError(LegalAIException):
    """Error during RAG retrieval/generation."""
    def __init__(self, message: str):
        super().__init__(message, code="RAG_ERROR")


class FileValidationError(LegalAIException):
    """Error during file validation."""
    def __init__(self, message: str):
        super().__init__(message, code="FILE_VALIDATION_ERROR")


class ModelNotReadyError(LegalAIException):
    """Error when AI model is not loaded."""
    def __init__(self, message: str):
        super().__init__(message, code="MODEL_NOT_READY")
