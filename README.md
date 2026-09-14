# DevFlow AI

**DevFlow AI** is a full-stack AI-assisted project-management workspace that turns project ideas into structured execution plans and trackable tasks.

## Features

- User registration, login and logout
- JWT-based authentication
- User-specific project access
- Create, view, update and delete projects
- Create, update, delete and organize tasks
- Task workflow: **Todo → In Progress → Completed**
- Task priorities: Low, Medium, High and Critical
- Dashboard statistics and delivery progress
- AI project planner with goals, tasks, estimates, dependencies and risks
- Approval workflow for adding AI-generated tasks to a project
- Project-aware AI Copilot
- Demo AI mode for local development without OpenAI credits
- Responsive dark-themed React interface

## Tech stack

- **Frontend:** React, Vite, CSS
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL with SQLAlchemy
- **Authentication:** JWT, Passlib/Bcrypt
- **AI integration:** OpenAI API with a demo-mode fallback

## Project structure

```text
Devflow-AI/
├── Backend/
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   ├── database.py
│   ├── ai_service.py
│   ├── requirements.txt
│   └── .env.example
├── Frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   └── package.json
├── .gitignore
└── README.md
```

## Run locally

### 1. Configure PostgreSQL

Create a PostgreSQL database and update `Backend/.env` using the example below.

### 2. Start the backend

Open a terminal in the `Backend` folder:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

The API will be available at:

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### 3. Start the frontend

Open a second terminal in the `Frontend` folder:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

If the backend is hosted somewhere else, create a frontend `.env` file containing:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Environment variables

`Backend/.env` should contain values similar to:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/devflow
SECRET_KEY=replace_with_a_long_random_secret
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
AI_MODE=demo
```

### AI mode

- `AI_MODE=demo`: Uses local deterministic responses and does not require OpenAI credits.
- `AI_MODE=live`: Uses the OpenAI API. A valid API key and available API credits are required.

**Never commit or share `Backend/.env` or real API keys.**

## API areas

- `/auth/register`
- `/auth/login`
- `/auth/me`
- `/projects`
- `/projects/{project_id}`
- `/projects/{project_id}/tasks`
- `/tasks`
- `/tasks/{task_id}`
- `/ai/analyze-project`
- `/ai/generate-plan`
- `/ai/apply-plan`
- `/ai/copilot`

## Demo note

The application can be demonstrated fully in demo mode. Live AI generation depends on the OpenAI account having available API credits.
