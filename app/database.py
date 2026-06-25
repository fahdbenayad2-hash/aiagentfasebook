from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.config import get_settings

settings = get_settings()

# SQLite configuration for concurrent access
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    pool_pre_ping=True,
)

# Enable WAL mode for better concurrency
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migration():
    """Add new columns to existing tables (Alembic not configured — raw ALTER TABLE)."""
    from app.services.logging_service import logger
    from sqlalchemy import text
    with engine.connect() as conn:
        migrations = [
            ("customers", "preferred_size", "VARCHAR"),
            ("customers", "fabric_preference", "VARCHAR"),
            ("customers", "last_orders_summary", "VARCHAR"),
            ("customers", "interaction_count", "INTEGER DEFAULT 0"),
            ("products", "complementary_product_ids", "VARCHAR"),
            ("products", "colors", "VARCHAR"),
            ("products", "sizes", "VARCHAR"),
            ("conversations", "manual_mode", "BOOLEAN DEFAULT 0"),
            ("users", "notification_phone", "VARCHAR"),
            ("users", "notify_new_order", "BOOLEAN DEFAULT 1"),
            ("users", "notify_handoff", "BOOLEAN DEFAULT 1"),
        ]
        for table, column, col_type in migrations:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
            except Exception:
                conn.rollback()
                logger.warning(f"Migration skipped: column {column} on {table} already exists or error occurred")
