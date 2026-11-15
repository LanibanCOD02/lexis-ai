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

## Frontend Tooling Integration

### UIPro CLI
UIPro is integrated into this project to manage high-quality UI components via AI (Antigravity).
- **Installation**: Run `npx uipro init --ai antigravity` in the `frontend` directory.
- **Basic Usage**: Ask your AI coding assistant to generate components using UIPro templates.

### 21st.dev CLI
The 21st.dev CLI provides access to a rich ecosystem of modern React components.
- **Installation**: `npm i -g @21st-dev/cli`
- **Authentication (Local)**: Run `21st login` in your terminal. This will open a browser to authenticate and save a token locally.
- **Authentication (CI/CD)**: For automated environments, do NOT use interactive login. Instead, set the `API_KEY_21ST` environment variable, or pass it explicitly: `21st <command> --api-key $API_KEY_21ST`.
- **Security Rule**: Never hardcode API keys in the codebase. Always refer to `frontend/.env.example` for required variables. Ensure your local `.env` is ignored by Git.
