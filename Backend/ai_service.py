import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _demo_mode() -> bool:
    return os.getenv("AI_MODE", "demo").lower() == "demo"


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=api_key)


def _ask_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    response = _client().chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def _demo_plan(project_idea: str) -> dict[str, Any]:
    title = project_idea.strip().rstrip(".")[:80] or "New Software Project"
    return {
        "project_title": title,
        "summary": f"A practical implementation plan for: {project_idea.strip()}.",
        "goals": [
            "Define the core user workflow",
            "Build a reliable backend and data model",
            "Implement and test the main feature",
            "Prepare the application for deployment",
        ],
        "tasks": [
            {
                "title": "Define requirements and user workflow",
                "description": "Clarify the target users, inputs, outputs, and success criteria.",
                "priority": "High",
                "estimated_hours": 3,
                "dependencies": [],
            },
            {
                "title": "Design application architecture",
                "description": "Choose the backend, frontend, database, and integration structure.",
                "priority": "High",
                "estimated_hours": 4,
                "dependencies": ["Define requirements and user workflow"],
            },
            {
                "title": "Implement backend foundation",
                "description": "Create the API, models, validation, configuration, and error handling.",
                "priority": "High",
                "estimated_hours": 8,
                "dependencies": ["Design application architecture"],
            },
            {
                "title": "Implement the core feature",
                "description": "Build the main functionality described in the project idea.",
                "priority": "Critical",
                "estimated_hours": 12,
                "dependencies": ["Implement backend foundation"],
            },
            {
                "title": "Add testing and edge-case handling",
                "description": "Test successful flows, invalid inputs, authorization, and failure cases.",
                "priority": "High",
                "estimated_hours": 6,
                "dependencies": ["Implement the core feature"],
            },
            {
                "title": "Prepare documentation and deployment",
                "description": "Document setup, environment variables, architecture, and deployment steps.",
                "priority": "Medium",
                "estimated_hours": 5,
                "dependencies": ["Add testing and edge-case handling"],
            },
        ],
        "risks": [
            "Requirements may change during implementation",
            "External API or model limits may affect availability",
            "Deployment configuration may require environment-specific changes",
        ],
        "recommended_order": [
            "Define requirements and user workflow",
            "Design application architecture",
            "Implement backend foundation",
            "Implement the core feature",
            "Add testing and edge-case handling",
            "Prepare documentation and deployment",
        ],
    }


def _demo_copilot(context: dict[str, Any], question: str) -> dict[str, Any]:
    tasks = context.get("tasks", [])
    incomplete = [task for task in tasks if task.get("status") != "Completed"]
    overdue = [task for task in incomplete if task.get("due_date")]
    high_priority = [task for task in incomplete if task.get("priority") in {"High", "Critical"}]
    next_task = high_priority[0] if high_priority else (incomplete[0] if incomplete else None)

    if next_task:
        answer = f"Based on the current project data, prioritize '{next_task['title']}' ({next_task.get('priority', 'Medium')} priority)."
        actions = [f"Work on: {next_task['title']}"]
        referenced = [next_task["id"]]
    else:
        answer = "There are no incomplete tasks in this project. Consider reviewing the project and planning the next milestone."
        actions = ["Review completed work", "Create the next milestone"]
        referenced = []

    if overdue:
        actions.insert(0, f"Review the {len(overdue)} task(s) with due dates first")

    return {
        "answer": answer,
        "recommended_actions": actions,
        "referenced_task_ids": referenced,
        "mode": "demo",
        "question": question,
    }


def analyze_project(name: str, description: str) -> dict[str, Any]:
    if _demo_mode():
        return {
            "summary": f"{name} is a project focused on {description or 'delivering a useful application'}.",
            "suggestions": ["Break the work into milestones", "Prioritize the core workflow", "Add tests before deployment"],
            "priority": "High",
            "estimated_complexity": "Medium",
            "mode": "demo",
        }
    return _ask_json(
        "You are a senior software architect. Return valid JSON only with keys: summary, suggestions, priority, estimated_complexity.",
        f"Analyze this project. Name: {name}. Description: {description}",
    )


def generate_project_plan(project_idea: str) -> dict[str, Any]:
    if _demo_mode():
        return _demo_plan(project_idea)

    system = """You are a senior AI software architect. Return valid JSON only.
Schema: {
  project_title: string,
  summary: string,
  goals: [string],
  tasks: [{title: string, description: string, priority: one of Low/Medium/High/Critical, estimated_hours: number, dependencies: [string]}],
  risks: [string],
  recommended_order: [string]
}
Generate practical, sequential tasks. Dependencies must contain task titles from the same response. Keep it to 5-12 tasks."""
    return _ask_json(system, project_idea)


def copilot_answer(context: dict[str, Any], question: str) -> dict[str, Any]:
    if _demo_mode():
        return _demo_copilot(context, question)

    system = """You are DevFlow Copilot, an AI project-management assistant.
Use only the supplied project context. Return valid JSON with keys: answer, recommended_actions, referenced_task_ids.
Do not invent task IDs or facts. referenced_task_ids must be a list of IDs present in the context."""
    prompt = f"PROJECT CONTEXT:\n{json.dumps(context, default=str)}\n\nUSER QUESTION:\n{question}"
    return _ask_json(system, prompt)
