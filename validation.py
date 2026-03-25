ALLOWED_EXTENSIONS = {".txt", ".pdf"}
MAX_QUERY_LENGTH = 500
MIN_QUERY_LENGTH = 3


def is_allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = "." + filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_query(query: str) -> tuple[bool, str]:
    if not query or not query.strip():
        return False, "Query cannot be empty."
    if len(query.strip()) < MIN_QUERY_LENGTH:
        return False, f"Query too short. Minimum {MIN_QUERY_LENGTH} characters."
    if len(query.strip()) > MAX_QUERY_LENGTH:
        return False, f"Query too long. Maximum {MAX_QUERY_LENGTH} characters."
    return True, ""