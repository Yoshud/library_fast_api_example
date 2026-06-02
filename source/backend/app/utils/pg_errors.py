from sqlalchemy.exc import IntegrityError


def get_pg_error_code(integrity_error: IntegrityError):
    if not hasattr(integrity_error, "orig"):
        return None
    return getattr(integrity_error.orig, "sqlstate", None) or getattr(integrity_error.orig, "pgcode", None)


FOREIGN_KEY_VIOLATION_PG_ERROR_CODE = "23503"
