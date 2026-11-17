# SIH1701 Legal Research Engine

AI-Driven Research Engine for Commercial Courts.

## Architecture
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + Python
- **RAG Pipeline**: PyMuPDF, LangChain, FAISS, Gemini 1.5 Pro
- **Database**: SQLite/PostgreSQL

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

