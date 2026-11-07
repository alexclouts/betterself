---
title: "Conception des modèles de données SQL"
header: ""
date: 2026-11-06T00:09:02.000Z
description: "Défis et apprentissages rencontrés lors de la conception des modèles de données."
tags:
  - FastAPI
  - IA
  - Backend
  - Vidéo
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Développer les tables SQLAlchemy

Cet article porte sur les apprentissages et les défis que j'ai rencontré lors de la conception des tables de ma base de données. Au total, 9 tables ont été construites et chacune d'elle respecte la même architecture globale. Elle est décrite dans la dernière [publication](https://alexclouts.github.io/betterself/posts/conception_projet/principes_dry_kiss/).

J'aborderai ici **3 sujets** qui ont suscité une réflexion inattendue lors du développement. J'aborderai la façon de faire que j'ai adopté pour gérer les fonctions dupliquées entre plusieurs services, l'ajout de la librairie `jscpd` pour m'aider à détecter le code _copier/coller_ entre mes fichiers, ainsi que la découverte des relations (`relationship`) inter-modèles et mes considérations en matière de sécurité.

Vous pouvez également consulter la [vidéo explicative](https://youtu.be/xKFyHWf_j0A) où je décris certains enjeux abordés ci-dessous.

# La gestion des fonctions dupliquées

Dans l'implémentation initiale de mon projet, chaque table est déclarée de manière indépendante. Il n'y avait donc aucune logique partagée entre deux modèles. Cependant, je me suis rapidement aperçu que certaines fonctions se dupliquaient dans mon code. Par exemple, la table `recipe_ingredients` doit s'assurer que la recette en question existe bel et bien dans la base de données avant que l'utilisateur puisse ajouter un ingrédient. Un ingrédient est d'ailleurs un aliment, donc cette classe doit aussi récupérer l'aliment pour créer une nouvelle entrée.

J'ai donc souligné ce problème à l'IA pour explorer mes options.

## Conversation avec l'IA

#### _Question :_ Actuellement, la fonction \_get_food_or_404 est présente dans trois classes différentes, soit RecipeIngredientService, FoodService et FoodConsumptionService. Je me demandais si, pour respecter DRY, je ne devrais pas plutôt consigner cette fonction dans un fichier distinct pour éviter les duplicats. Est-ce une bonne pratique ou non?

La meilleure option est généralement un petit **repository** ou un module `foods/repository.py`, parce que la fonction dépend d’une session SQLAlchemy et représente une règle d’accès aux données, pas une utilité générique.

```python
class RecipeIngredientService:
    def __init__(self, db: Session):
        self.db = db
        self.food_repository = FoodRepository(db)
```

### Alternative simple : fonction de module

Si tu ne veux pas introduire un repository maintenant, tu peux créer `foods/queries.py`

```python
from betterself.foods.queries import get_food_or_404


food = get_food_or_404(
    db=self.db,
    food_id=data.food_id,
)
```

| Approche                                       | Avantage                                           | Inconvénient                        |
| ---------------------------------------------- | -------------------------------------------------- | ----------------------------------- |
| Méthode `_get_food_or_404` dans chaque service | Simple, explicite                                  | Duplication                         |
| Fonction dans `foods/queries.py`               | DRY, facile à tester                               | La session est passée explicitement |
| `FoodRepository`                               | DRY, séparation claire service/données, extensible | Un peu plus de structure            |

### Ma recommandation

Pour ton projet actuel, commence par `foods/queries.py`. C’est le meilleur compromis entre DRY, lisibilité et simplicité.

Plus tard, si tu ajoutes plusieurs requêtes partagées — recherche d’aliments, filtrage par catégorie, pagination, vérification d’existence — transforme `queries.py` en `FoodRepository`.

## Analyse

La création d'un fichier `repository.py` figure dans mon [ADR adressant l'organisation du code](https://github.com/alexclouts/betterself/blob/main/docs/adr/code-organisation/index.md). Cependant, mon implémentation imbrique les opérations CRUD à même les services des modèles, ce qui est selon moi un compromis acceptable entre simplicité et séparation des responsabilités. Ce changement diffère de ma conception initiale. L'ajout d'un fichier `repository.py` se fera si les opérations CRUD partagées entre les classes deviennent plus nombreuses lors du développement.

# L'ajout de jscpd

Pour faciliter la détection des duplicats, j'ai décidé de faire appel à la librairie `jscpd`, qui a d'ailleurs été ajoutée au _workflow_ du projet. GitHub Actions génèrera un message d'erreur s'il détecte trop d'erreurs de ce type lors d'un _PUSH_ ou d'un _PULL_ du commit.

### Le problème solutionné : La mémoire de l'IA

Je crois que cet outil est nécessaire puisque l'IA, bien qu'elle offre des perspectives nouvelles, comprend également des limitations majeures en terme de mémoire. En effet, elle ne se souvient pas des fonctions proposées précédemment dans le fil de conversation, ce qui augmente le risque de retrouver du code _copier-coller_ un peu partout au sein du projet. J'ai rencontré ce problème à plusieurs reprises jusqu'à présent. Cela réitère l'importance de ne pas accorder une confiance aveugle aux réponses qu'elle nous donne. L'ajout de cette bibliothèqu cherche à offrir une solution à cette problématique.

## Création d'un rapport

Une simple commande dans le terminal permet de générer un rapport du code dupliqué. Voici un exemple que j'ai produit avec Betterself :

```
uvx jscpd src --reporters console,html --output reports/duplication
```

{{< img
src="screenshot1.png"
alt="Screenshot 1"
caption=""
width="800">}}

Je peux donc voir que j'ai 5 clônes au sein du projet. Le rapport me permet également de voir que ces lignes portent sur :

1. La déclaration des paramètres de modèle :

```python
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
```

2. La gestion des exceptions au sein des routeurs :

```python
           user=current_user,
            data=data,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
```

Il existe bien une manière d'appliquer le principe **DRY** à ces lignes de code, mais cela apporterait une complexité supplémentaire qui ne vaudrait pas la peine.

# Les relationships entre modèles

Le code suggéré par l'IA déclare des `relationship` entre les modèles. J'ai appris que ces paramètres servent à créer un attribut Python au sein d'un objet afin d'accéder à l'objet mis en relation grâce à sa clé étrangère. Autrement dit, dans l'exemple ci-dessous, il sera possible d'accéder à la liste de recettes appartenant à un utilisateur en faisant `user.recipes`.

```python
class User(Base):
    __tablename__ = "users"
    # Relation vers les recettes associées à l'utilisateur. Un utilisateur peut avoir plusieurs recettes.
    recipes: Mapped[list["Recipe"]] = relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan",
    )
```

L'IA m'a appris que c'était possible grâce à SQLAlchemy. De plus, `back_populates` relie les deux côtés de cette relation afin qu’ils restent synchronisés dans les deux sens et `cascade="all, delete-orphan"` détermine que la suppression d'un utilisateur entraînera aussi la suppression de ses recettes (ses orphelins).

### Enjeu de sécurité ?

Dans mon code, plusieurs objets ont une relation avec la table `User`. Comme c'était le cas pour `user_profiles`, je me suis demandé si le recours répétitif à l'objet _User_ était une bonne chose, considérant qu'elle contient plusieurs données sensibles. J'ai questionné l'IA à ce sujet.

## Conversation avec l'IA

#### _Question :_ Dans mon cas, User est une table qui gère principalement les paramètres de sécurité (pwd_hash, email, is_active, etc) est-ce une bonne idée de mettre cet objet en relation avec d'autres tables, ce qui fera que son utilisation sera plus courante au sein du backend?

Oui — c’est même l’approche recommandée. `User` est l’**agrégat racine** de ton domaine : il représente l’identité du compte, et les autres tables métier doivent référencer son `id`. Le fait qu’il contienne aussi des champs de sécurité ne change pas ce rôle.

### Pourquoi relier les tables à `User`

Tes données appartiennent toutes à un utilisateur :

```text
User
├── UserProfile
├── NutritionGoal
├── GoalTarget
├── Recipe
└── FoodConsumption
```

Les clés étrangères doivent donc pointer vers `users.id` :

```python
user_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
)
```

Cela garantit l’isolation des données, la suppression en cascade et la possibilité de filtrer efficacement par utilisateur. Ce n’est pas un problème de conception. Séparer `User` en deux tables — par exemple `users` et `user_identities` — **ajouterait de la complexité sans bénéfice clair à ce stade.**

## Analyse

Plus le projet avance, plus je réalise qu'il n'existe pas **une seule manière cohérente** de développer une application.
La plupart des questions que je me pose relève du _cas par cas_ qui dépendent de l'envergure du projet et de son développement futur. Je crois que l'implémentation actuelle est bien adapté à mes besoins pour le MVP.
