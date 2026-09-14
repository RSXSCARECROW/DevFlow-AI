# DevFlow AI

> An AI-powered, full-stack project management workspace that turns project ideas into structured execution plans and trackable tasks.

DevFlow AI helps development teams organize projects, manage tasks, track progress, and use AI to generate actionable project plans through a clean, modern workspace.

## Overview

DevFlow AI combines traditional project management features with AI-assisted planning.

Users can:

* Create and manage projects
* Add, update, and track tasks
* Monitor project progress
* Generate structured project plans using AI
* Apply AI-generated tasks directly to projects
* Ask questions through an AI Copilot
* Access protected features through JWT authentication

## Features

### Project Management

* Create and manage multiple projects
* View project descriptions and progress
* Track task completion
* Monitor project status through a dashboard

### Task Management

* Create tasks within projects
* Organize tasks by status
* Update task progress
* Track completed and pending work

### AI Project Planner

* Convert project ideas into structured execution plans
* Generate milestones and actionable tasks
* Apply generated plans directly to a project
* Support demo mode for local development without an external AI API

### AI Copilot

* Ask project-related questions
* Receive AI-assisted recommendations
* Get help breaking down project requirements and tasks

### Authentication

* User registration
* User login
* JWT-based authentication
* Protected project and task endpoints

### Modern User Interface

* Responsive React frontend
* Dark-themed dashboard
* Project overview cards
* Task board interface
* AI planning interface
* Copilot interaction panel

## Tech Stack

### Frontend

* React
* Vite
* JavaScript
* HTML5
* CSS3
* Fetch API

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* JWT Authentication
* Pydantic
* Uvicorn

### AI

* OpenAI-compatible AI integration
* AI-generated project plans
* AI Copilot responses
* Demo AI mode for local testing

### Development Tools

* Git
* GitHub
* VS Code
* Python virtual environment
* npm

## Project Structure

```text
Devflow-AI/
├── Backend/
│   ├── ai_service.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env.example
│
├── Frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
└── README.md
```

## Application Screenshots

## Application Screenshots

### Login

![DevFlow AI Login](screenshots/Login.jpeg)

### Dashboard

![DevFlow AI Dashboard](screenshots/Dashboard.jpeg)

### Project and Task Board

![DevFlow AI Task Board](screenshots/Taskboard.jpeg)

### AI Project Planner

![DevFlow AI Planner](screenshots/AI-planner.jpeg)

### AI Copilot

![DevFlow AI Copilot](screenshots/Copilot.jpeg)

## Getting Started

### Prerequisites

Install the following before running the project:

* Python 3.10+
* Node.js and npm
* PostgreSQL
* Git

### 1. Clone the repository

```bash
git clone https://github.com/RSXSCarecrow/DevFlow-AI.git
cd DevFlow-AI
```

## Backend Setup

### 2. Move into the backend directory

```bash
cd Backend
```

### 3. Create a virtual environment

On Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file inside the `Backend` directory using `.env.example` as a template.

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/devflow
SECRET_KEY=replace_with_a_long_random_secret
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
AI_MODE=demo
```

For local testing, keep:

```env
AI_MODE=demo
```

Never commit your real `.env` file or API keys to GitHub.

### 6. Start the backend

```bash
python -m uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a second terminal.

### 7. Move into the frontend directory

From the project root:

```powershell
cd Frontend
```

### 8. Install frontend dependencies

```bash
npm install
```

### 9. Start the frontend

```bash
npm run dev
```

The frontend will usually run at:

```text
http://localhost:5173
```

Open the displayed local URL in your browser.

## Running the Application

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Start the React frontend.
4. Register a user account.
5. Create a project.
6. Add tasks.
7. Test project progress tracking.
8. Try the AI Project Planner.
9. Test the AI Copilot.

## API Endpoints

### Authentication

```text
POST /auth/register
POST /auth/login
```

### Projects

```text
GET    /projects
POST   /projects
GET    /projects/{project_id}
PUT    /projects/{project_id}
DELETE /projects/{project_id}
```

### Tasks

```text
GET    /projects/{project_id}/tasks
POST   /projects/{project_id}/tasks
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

### AI Features

```text
POST /ai/generate-plan
POST /ai/apply-plan
POST /ai/copilot
```

### Health Check

```text
GET /health
```

## AI Demo Mode

DevFlow AI includes a demo mode for local development.

When:

```env
AI_MODE=demo
```

the application uses predefined demo responses for AI features. This allows the project to be tested without requiring an active external AI API key.

For real AI integration, configure the required AI environment variables and change the AI mode according to the implementation.

## Security Notes

* Do not upload `.env` files.
* Do not expose API keys in screenshots or documentation.
* Use a strong `SECRET_KEY`.
* Use a secure database password.
* Rotate any credentials that were accidentally exposed.
* Keep production credentials outside the repository.

## Future Improvements

* Deploy the frontend and backend
* Add real-time collaboration
* Add team invitations and role-based permissions
* Add project deadlines and reminders
* Add file attachments
* Add activity history
* Add advanced analytics
* Add AI-powered task prioritization
* Add automated project risk detection
* Add CI/CD with GitHub Actions
* Add automated testing
* Add production database configuration

## Project Status

DevFlow AI is currently a functional full-stack MVP with:

* React frontend
* FastAPI backend
* JWT authentication
* Project and task management
* Progress tracking
* AI project planning
* AI Copilot
* GitHub repository setup

## Author

**RSXSCarecrow**

GitHub: https://github.com/RSXSCarecrow

## License

This project is currently available for educational and portfolio purposes.
