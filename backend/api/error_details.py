from openai import APIStatusError, AuthenticationError
from qdrant_client.http.exceptions import UnexpectedResponse


def external_service_error_detail(error: Exception, fallback: str) -> str:
    if isinstance(error, AuthenticationError):
        return "OpenAI authentication failed. Check OPENAI_API_KEY."

    if isinstance(error, APIStatusError):
        return f"OpenAI request failed with status {error.status_code}."

    if isinstance(error, UnexpectedResponse):
        status_code = getattr(error, "status_code", None)
        if status_code in {401, 403}:
            return "Qdrant authentication failed. Check QDRANT_URL and QDRANT_API_KEY."
        if status_code == 404:
            return "Qdrant collection was not found. Run ingestion to create and populate it."
        if status_code:
            return f"Qdrant request failed with status {status_code}."
        return "Qdrant request failed."

    return fallback
