from pathlib import Path

import pandas as pd

from .database import SessionLocal, initialize_database
from .models import Scholarship, ScholarshipStatistics, Student


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"


def optional_value(value):
    return None if pd.isna(value) or str(value).strip() == "" else value


def seed_database():
    initialize_database()
    db = SessionLocal()

    try:
        scholarships = pd.read_csv(DATA_DIRECTORY / "scholarships.csv")
        existing_scholarships = {
            (item.name, item.scheme): item for item in db.query(Scholarship).all()
        }
        for row in scholarships.to_dict(orient="records"):
            identity = (row["name"], row["scheme"])
            scholarship = existing_scholarships.get(identity)
            if scholarship is None:
                scholarship = Scholarship(
                    name=row["name"],
                    scheme=row["scheme"],
                    category=optional_value(row.get("category")),
                    max_income=optional_value(row.get("max_income")),
                    education_level=optional_value(row.get("education_level")),
                    description=optional_value(row.get("description")),
                    application_url=optional_value(row.get("application_url")),
                )
                db.add(scholarship)
            else:
                scholarship.category = optional_value(row.get("category"))
                scholarship.max_income = optional_value(row.get("max_income"))
                scholarship.education_level = optional_value(row.get("education_level"))
                scholarship.description = optional_value(row.get("description"))
                scholarship.application_url = optional_value(row.get("application_url"))

            existing_scholarships[identity] = scholarship

        statistics = pd.read_csv(DATA_DIRECTORY / "mota_annexure_ii_scholarship_data.csv")
        existing_statistics = {
            (item.financial_year, item.scheme)
            for item in db.query(ScholarshipStatistics).all()
        }
        for row in statistics.to_dict(orient="records"):
            identity = (row["financial_year"], row["scheme"])
            if identity in existing_statistics:
                continue

            db.add(
                ScholarshipStatistics(
                    financial_year=row["financial_year"],
                    scheme=row["scheme"],
                    fund_released_crore=float(row["fund_released_crore"]),
                    beneficiaries=int(row["beneficiaries"]),
                    source=row["source"],
                )
            )
            existing_statistics.add(identity)

        db.commit()
        print("Database seeded successfully.")
        print(f"Students: {db.query(Student).count()}")
        print(f"Scholarships: {db.query(Scholarship).count()}")
        print(f"Statistics: {db.query(ScholarshipStatistics).count()}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()