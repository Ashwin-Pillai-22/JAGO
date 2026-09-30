# JAGO Scholarship Platform

JAGO is a full-stack scholarship portal designed to help students discover relevant scholarships, register and sign in, upload required documents, and ask questions through a chatbot assistant.

## Overview

This project combines:

- A FastAPI backend for student management, authentication, scholarship data, and document handling
- A React + Vite frontend for the user interface
- A SQLite database for storing students, auth tokens, scholarship data, and uploaded documents
- CSV-based scholarship data under the `data/` directory

## Features

- Student registration and login
- Authenticated student profile access
- Scholarship listing and filtering by category or education level
- Scholarship statistics endpoint
- Student document upload for documents such as Aadhaar, domicile, caste, and marksheets
- Chat support for scholarship-related queries
- Frontend dashboard for browsing scholarships and interacting with the app

## Project Structure

```text
JAGO-main/
├── app/
│   ├── auth.py
│   ├── chatbot.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── seed.py
├── data/
│   ├── mota_annexure_ii_scholarship_data.csv
│   └── scholarships.csv
├── Frontend/
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
├── uploads/
├── jago.db
├── main.py
├── requirements.txt
├── README.md
└── .venv/
```

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic
- Frontend: React, Vite
- Database: SQLite
- Data Import: pandas
- File Uploads: local filesystem under `uploads/`

## Prerequisites

Before running the app, make sure you have:

- Python 3.10+
- Node.js 18+
- npm

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:

```bash
cd Frontend
npm install
```

## Running the Application

### Start the backend

From the project root:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You can also access the API documentation at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

### Start the frontend

From the `Frontend` directory:

```bash
npm run dev -- --host 0.0.0.0
```

Then open the local Vite URL shown in the terminal, usually:

- http://localhost:5173

## Seeding Scholarship Data

The project includes a database seeder that loads data from CSV files into SQLite.

Run:

```bash
python app/seed.py
```

This populates the scholarship and statistics tables from files in the `data/` folder.

## Database and File Storage

- SQLite database file: `jago.db`
- Uploaded documents are saved under `uploads/<student_id>/`

## Notes

- The backend is initialized in `app/main.py` and exposed through the `main.py` root file.
- The frontend is a separate Vite app inside the `Frontend/` directory and runs independently from the backend.
- The app uses local storage for uploaded documents rather than cloud storage, so it is best suited for local development or small deployments.

## License

This project is provided for educational and prototype use as part of the project workflow.
