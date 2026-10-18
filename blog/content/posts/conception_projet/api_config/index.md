# Déploiement du projet

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
width="500">}}

Pour obtenir plus d'informations sur ce prblème, j'ai décidé de concevoir l'infrastructure autour des tests unitaires pour tenter de comprendre ce qui ne fonctionne pas. J'ai finalement compris, avec un peu d'aide, que le problème était que j'ai 2 projets Python dans le répertoire mère. J'ai oublié que j'avais déjà créer un projet Python en configurant mes premiers tests unitaires. Cela fait en sorte que le module `uv` peut remonter et détecter le **pyproject.toml** de la racine. Il utilise alors le .venv de la racine, qui ne contient pas FastAPI, httpx ou pytest. Cela causait un `ModuleNotFoundError`, qui expliquait pourquoi mes tests échouaient.

{{< img
src="snap_test_erreur.png"
alt="Capture d'écran 2"
caption=""
width="500">}}

En vérifiant de nouveau sur le serveur, je vois toujours le même message d'erreur à l'écran. Puisque le test a passé, je comprends que le problème n'est pas situé du côté API.
