import json
from pathlib import Path

from betterself.main import app


"""
Script pour exporter la documentation OpenAPI de l'application FastAPI.
Le fichier généré sera placé à la racine du backend sous le nom "openapi.json".
"""
output_path = Path(__file__).resolve().parent.parent / "openapi.json"

with output_path.open("w", encoding="utf-8") as file:
    json.dump(app.openapi(), file, indent=2, ensure_ascii=False)

print(f"OpenAPI exporté vers : {output_path}")