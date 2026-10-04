---
title: "Résumé de mes choix"
header: ""
date: 2026-09-25T08:55:00.000Z
description: "Résumé des choix techniques actuels et présentation de l'architecture globale."
tags:
  - Architecture
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="600">}}

## L'architecture actuelle

Après avoir comparé différentes possibilités, on peut établir un tableau décrivant la première architecture technique du projet.

Ces choix ne sont pas tous définitifs. Le développement du prototype permettra de valider ou de remettre en question certaines des décisions prises au départ.

### Les choix

| Composant                     | Technologie         |
| ----------------------------- | ------------------- |
| Frontend                      | React               |
| Interface mobile              | Progressive Web App |
| Backend                       | Python + FastAPI    |
| Validation                    | Pydantic            |
| Accès aux données             | SQLAlchemy          |
| Base de données initiale      | SQLite              |
| Base de données potentielle   | PostgreSQL          |
| Conteneurisation              | Docker              |
| Hébergement backend envisagé  | Railway             |
| Hébergement frontend envisagé | GitHub Pages        |
| API alimentaire               | Open Food Facts     |

### Architecture logique

L'application devrait suivre une architecture séparant clairement le frontend, le backend et la base de données.

```text
                    ┌──────────────────┐
                    │     Utilisateur  │
                    │ Mobile / Desktop │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   React / PWA   │
                    └────────┬─────────┘
                             │ HTTP
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │     Backend      │
                    └──────┬─────┬─────┘
                           │     │
                     SQL   │     │ HTTP
                           │     ▼
                           │  Open Food
                           │    Facts
                           ▼
                    ┌──────────────────┐
                    │      SQLite      │
                    │  → PostgreSQL    │
                    └──────────────────┘
```

Cette séparation permettra au frontend de rester indépendant de la technologie utilisée pour stocker les données. Elle devrait également faciliter l'évolution de l'application. Par exemple, une migration de SQLite vers PostgreSQL ne devrait pas nécessiter de réécrire l'interface React.

[Retour](http://localhost:1313/posts/)
