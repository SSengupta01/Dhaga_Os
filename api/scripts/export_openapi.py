"""Export the FastAPI contract consumed by the frontend type generator."""
import json
from pathlib import Path

from dhaga.main import app

target = Path(__file__).parents[1] / "openapi.json"
target.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
print(target)
