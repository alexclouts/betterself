---
title: "Déploiement de FastAPI"
header: ""
date: 2026-10-18T00:04:00.000Z
description: "Établir une connexion API entre le frontend et le backend, politique CORS."
tags:
  - FastAPI
  - Problème
  - CORS
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Déploiement du projet

Je vous invite à consulter la [Vidéo 2: Données et début de conception](https://youtu.be/KnhiKsN72_A). Celle-ci vous présente brièvement la progression réalisée au cours des dernières semaines. Bon visionnement.

## Un premier problème

J'ai commencé en suivant les instructions données par l'IA pour déployer le frontend et le backend. J'ai utilisé `npm` pour installer les environnements nécessaires. J'utilise le framework `Vite` pour ensuite avoir la possibilité de le déployer sur un appareil mobile.

À ma première tentative de tester le déploiement de FastAPI, je constate que je reçois un message d'erreur.

```
function App() {
  const [status, setStatus] = useState<string>("Connexion au backend...");

  useEffect(() => {
    checkApiHealth()
      .then((data) => setStatus(`Backend : ${data.status}`))
      .catch(() => setStatus("Backend indisponible."));
  }, []);

  return (
    <main>
      <h1>BetterSelf</h1>
      <p>{status}</p>
    </main>
  );
}

export default App;
```

{{< img
src="snap_indisponible.png"
alt="Capture d'écran"
caption=""
width="800">}}

Pour obtenir plus d'informations sur ce problème, j'ai décidé de concevoir l'infrastructure autour des tests unitaires pour tenter de comprendre ce qui ne fonctionne pas. J'ai finalement compris, avec un peu d'aide, quel était le problème: j'ai 2 projets Python dans le même projet, soit un dans le répertoire mère et un dans `/betterself/backend/`.

J'ai oublié que j'avais déjà créer un projet Python en configurant mes premiers tests unitaires. Cela fait en sorte que le module `uv` peut remonter et détecter le **pyproject.toml** de la racine. Il utilise alors le .venv de la racine, qui ne contient pas FastAPI, httpx ou pytest. Cela causait un `ModuleNotFoundError`, qui expliquait pourquoi mes tests échouaient.

{{< img
src="snap_test_erreur.png"
alt="Capture d'écran 2"
caption=""
width="700">}}

En vérifiant de nouveau sur le serveur à partir d'un navigateur Web, je vois toujours le même message d'erreur à l'écran. Puisque le test a réussi, je comprends que le problème n'est pas situé du côté API. Pour m'assurer qu'il ne provient pas du backend, je vérifie sur mon navigateur, qui m'affiche la réponse que je veux voir:

```
{"status":"ok"}
```

## Bloqué par la politique CORS

Je continue d'investiguer pour me rendre compte que je n'ai pas configuré CORS. Une politique CORS permettrait à mon frontend de communiquer avec mon backend. La meilleure pratique qui m'est suggéré est de définir une configuration contrôlée par environnement.

{{< img
src="snap_cors_blocked.png"
alt="Capture d'écran 3"
caption=""
width="700">}}

### Bonnes pratiques à adopter

Il faut que je fasse attention à ne pas utiliser `allow_origins=["*"]` avec `allow_credentials=True`. De plus, il faut autoriser uniquement dans CORS les origines précises dans mon frontend. Je conserve cette liste dans une variable d'environnement.

Après avoir apporté les modifications à mon projet, je reçois finalement un réponse `Backend: ok`.
