from typing import Any

from piccolo.utils.pydantic import create_pydantic_model

from src.apps.tasks.models import Task

TaskIn: Any = create_pydantic_model(
    Task, exclude_columns=(Task.created_at,), model_name="TaskIn"
)
TaskOut: Any = create_pydantic_model(
    Task, include_default_columns=True, model_name="TaskOut"
)
