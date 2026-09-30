from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_PATH = Path(__file__).resolve().parent.parent / "jago.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def initialize_database():
    tables = set(inspect(engine).get_table_names())
    migrations = {
        "students": ({"name", "category", "state", "income", "education_level", "course"}, "students_legacy"),
        "scholarships": ({"name", "scheme", "category", "max_income", "education_level"}, "scholarships_legacy"),
    }
    for table_name, (required_columns, legacy_name) in migrations.items():
        if table_name not in tables:
            continue

        columns = {column["name"] for column in inspect(engine).get_columns(table_name)}
        if not required_columns.issubset(columns):
            if legacy_name in tables:
                raise RuntimeError(f"Legacy table {legacy_name} already exists; resolve it before migrating.")

            with engine.begin() as connection:
                connection.exec_driver_sql(f"ALTER TABLE {table_name} RENAME TO {legacy_name}")

    Base.metadata.create_all(bind=engine)