from loguru import logger
from piccolo.engine import engine_finder


async def open_database_connection_pool():
    """Start database connection pool."""
    engine = engine_finder()
    if engine is None:
        logger.error("No Piccolo engine found. Cannot start connection pool.")
        raise RuntimeError("Database engine not configured")

    try:
        await engine.start_connection_pool()
        logger.info("Database connection pool started.")
    except Exception as e:
        logger.exception(
            f"Failed to start database connection pool for engine {engine}: {e}"
        )
        raise


async def close_database_connection_pool():
    """Close database connection pool."""
    engine = engine_finder()
    if engine is None:
        logger.warning("No Piccolo engine found. Cannot close connection pool.")
        return

    try:
        await engine.close_connection_pool()
        logger.info("Database connection pool closed.")
    except Exception as e:
        logger.exception(
            f"Error closing database connection pool for engine {engine}: {e}"
        )
