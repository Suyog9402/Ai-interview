"""Custom exceptions for the application"""


class InterviewPipelineException(Exception):
    """Base exception for interview pipeline"""
    pass


class StorageException(InterviewPipelineException):
    """Exception raised for storage operations"""
    pass


class TranscriptionException(InterviewPipelineException):
    """Exception raised for transcription operations"""
    pass


class ExtractionException(InterviewPipelineException):
    """Exception raised for data extraction operations"""
    pass


class MatchingException(InterviewPipelineException):
    """Exception raised for matching operations"""
    pass


class RAGException(InterviewPipelineException):
    """Exception raised for RAG operations"""
    pass


class MemoryException(InterviewPipelineException):
    """Exception raised for memory operations"""
    pass

