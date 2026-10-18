import { useEffect, useState } from "react";
import { checkApiHealth } from "./services/apiClient";

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