---
title: "Validation et gestion des erreurs"
header: ""
date: 2026-10-30T00:10:15.000Z
description: "Comment valider les données d'un modèle et choix du code d'erreur (404, 403) associé à la mise à jour d'un enregistrement."
tags:
  - Architecture
  - FastAPI
  - Pydantic
  - IA
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Validation des données du modèle

Alors que je configurais les fonctions associées à la table `measurements`, j'ai réalisé que je devais mettre en place des balises pour distinguer les valeurs considérées comme étant **valides**, de celles que l'application devait interdire. Par exemple, lorsque l'utilisateur veut enregistrer une nouvelle mesure de poids dans l'application, je devais trancher pour décider si c'était possible de sauvegarder une mesure à une date antérieure à aujourd'hui. Le même genre de validation doit se faire également pour le poids de l'utilisateur. Il ne fait aucun sens qu'un utilisateur sauvegarde un poids de 1000 kg, puisque cette valeur va à l'encontre de l'objectif visé par cette application. Par contre, où se trouve les limites entre une mesure valide ou non? De plus, où devrait se situer cette logique au sein de l'application. Ce sont les problèmes que j'ai rencontré cette semaine.

### Date antérieure permise, mais limitée

Pour le moment, j'ai décidé de permettre à l'utilisateur de sauvegarder un poids à une date antérieure à partir de 2020. Cela permet à un nouvel utilisateur d'ajouter l'historique de son poids si ces données sont déjà sauvegardées dans une autre application, par exemple. Je considère que cet intervalle est assez grand pour offrir une portée intéressante et non restrictive.

Une autre vérification doit être fait pour empêcher l'utilisateur de sauvegarder un poids dans le futur, bien que l'interface utilisateur sera conçue de manière à l'empêcher de le faire.

### Intervalle de poids humainement possible

La validation du poids doit être assez inclusive pour permettre à n'importe qui d'utiliser l'application, à condition qu'il ne s'agit pas d'un bébé ou d'un enfant en bas âge. Pour cette raison, j'ai décidé d'imposer une limite minimale de _30 kg_ et une limite maximale de _500 kg_. On s'assure ainsi que les valeurs inscrites ne soient pas négatives (-) ou extrêmement grandes.

## Où organiser cette validation

Ma première intuition a été de placé le code de validation dans les fonctions de `service.py`. Au moment où la requête est fait par l'utilisateur, l'application vérifiera que les données saisies sont valides avant d'apporter la modification.

```python
   def update_measurement_by_id(self, user: User, measurement_id: int, data: MeasurementUpdate) -> Measurement | None:
        query = select(Measurement).where(
            Measurement.user_id == user.id,
            Measurement.id == measurement_id
        )
        measurement = self.db.scalar(query)

        if measurement is None:
            return None

        if data.date is not None:
            # Vérifie que la date est bien un objet date
            if not isinstance(data.date, date):
                raise ValueError("Date invalide.")

            if data.date > date.today() or data.date < date(2020, 1, 1):
                raise ValueError("Date invalide.")

            measurement.date = data.date

        if data.weight_kg is not None:
            # Vérifie que le poids est dans une plage valide
            if not isinstance(data.weight_kg, (int, float)):
                raise ValueError("Poids invalide")

            if data.weight_kg <= 30 or data.weight_kg > 500:
                raise ValueError("Poids invalide")

            measurement.weight_kg = data.weight_kg

        self.db.commit()
        self.db.refresh(measurement)
        return measurement
```

Par contre, en discutant avec l'IA, celle-ci m'a suggéré une approche que je préfère davantage, soit de laisser _Pydantic_ s'occuper intégralement de la validation des données.

{{< img
src="troubleshooting-1.png"
alt="Preview"
caption=""
width="500">}}

À la suite de ce message d'erreur, j'essayais de comprendre l'origine de l'erreur 422 dans mon test unitaire portant sur la validation de mes données, voici notre échange :

## Discussion avec l'IA

#### _Ma question:_ Quel type d'erreur Python génère une erreur de statut 422?

Un `422` dans FastAPI est généré par une **erreur de validation de la requête** : en interne, Pydantic lève une `ValidationError`, FastAPI la convertit en `RequestValidationError`, puis renvoie automatiquement `422 Unprocessable Entity`. Cela concerne les données entrantes : corps JSON, paramètres de chemin, query params, en-têtes ou cookies.

### Erreurs qui produisent un 422

FastAPI valide les données **avant** d’exécuter ta fonction de route. Donc si tu reçois un `422`, ton code dans `create_measurement`, `update_measurement`, etc. n’a généralement pas encore été exécuté.

### Bonne option 1 : lever une HTTPException 422

Si la validation dépend d’une règle métier et que tu veux la faire dans le routeur ou le service, lève explicitement une `HTTPException` :

```python
from fastapi import HTTPException, status

if data.date > DateType.today() or data.date < DateType(2020, 1, 1):
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="La date doit être comprise entre le 1er janvier 2020 et aujourd’hui.",
    )
```

Alors ta requête retournera bien :

```json
{
  "detail": "La date doit être comprise entre le 1er janvier 2020 et aujourd’hui."
}
```

avec le statut `422`.

### Bonne option 2 : valider dans Pydantic

C’est la solution la plus propre : la règle appartient au schéma, donc FastAPI retournera automatiquement `422` sans code spécial dans la route.

## Analyse

Cette discussion m'a permis de mieux comprendre le rôle de Pydantic au sein de mon application. Dans les classes _MeasurementUpdate_ et _MeasurementCreate_, il me suffit d'ajouter des fonctions annotés avec `@field_validator` pour indiquer les règles que je veux imposer aux données. C'est donc cette méthode que je vais privilégier à l'avenir.

```python

class MeasurementCreate(BaseModel):
    date: DateType
    weight_kg: float = Field(gt=0)

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, value):
        if value <= 30 or value > 500:
            raise ValueError("Poids invalide")
        return value

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        if value > DateType.today() or value < DateType(2020, 1, 1):
            raise ValueError("Date invalide")
        return value

```

# Mise à jour d'un enregistrement

Une autre situation que j'ai rencontré s'est produite avec le test unitaire `test_update_measurement_for_another_user`. Celui-ci teste la récupération d'une mesure de poids par un utilisateur à qui il n'appartient pas. Je m'attendais à ce qu'il génère une erreur 403 pour l'accès interdit à une ressource, mais j'obtenais plutôt l'erreur suivante :

{{< img
src="troubleshooting-2.png"
alt="Preview"
caption=""
width="500">}}

## Conversation avec l'IA

#### _Ma question:_ Pourquoi ai-je une erreur 404 sur ce code plutot que 403?

Tu obtiens `404` parce que ton service applique volontairement la règle : **une mesure qui n’appartient pas à l’utilisateur courant est traitée comme inexistante**.

Dans `update_measurement_by_id`, ta requête filtre à la fois sur :

```python
Measurement.user_id == user.id,
Measurement.id == measurement_id
```

Donc, pour l’utilisateur 2, la mesure de l’utilisateur 1 n’est tout simplement pas trouvée. La méthode retourne `None`, puis ton routeur lève :

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Mesure introuvable.",
)
```

### 404 ou 403 ?

Les deux sont défendables, mais ils n’ont pas la même signification :

| Statut          | Signification                                                           | Quand l’utiliser                                             |
| :-------------- | :---------------------------------------------------------------------- | :----------------------------------------------------------- |
| `404 Not Found` | La ressource n’existe pas **pour cet utilisateur**                      | Recommandé pour protéger l’existence des ressources privées  |
| `403 Forbidden` | La ressource existe, mais l’utilisateur n’a pas le droit de la modifier | Utilisé quand l’existence de la ressource n’est pas sensible |

Pour une API de santé comme BetterSelf, `404` est généralement le meilleur choix : il évite de révéler à un utilisateur qu’une mesure avec cet ID existe chez quelqu’un d’autre.

## Analyse

En lisant la réponse offerte par l'IA, j'ai rapidement compris que la raison de cette erreur était dû à ma requête, qui vérifie également que la valeur de `user_id` correspond à celle de l'utilisateur qui effectue la requête. Les explications offertes m'ont aussi fait prendre conscience que cette approche était préférable, puisque, de cette manière, un utilisateur ne verra jamais la différence entre une mesure avec un `ID` existant qui ne lui appartient pas, et un identifiant simplement inexistant.
