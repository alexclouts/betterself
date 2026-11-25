import { useEffect, useRef, useState } from "react";
import { firstProductBarcode, getBarcodeDetector } from "../../lib/barcode";

/*
 * Lecteur de code-barres par la caméra arrière.
 * Analyse l'image à intervalle régulier ; au premier code de produit valide,
 * fait vibrer l'appareil, éteint la caméra et transmet le code.
 * La caméra exige un contexte sécurisé (HTTPS ou localhost).
 */

// Intervalle entre deux analyses : assez court pour être réactif, sans surcharger le téléphone.
const SCAN_INTERVAL_MS = 200;

type ScannerState =
  | { status: "starting" }
  | { status: "scanning" }
  | { status: "error"; message: string };

// Message compréhensible pour chaque cause d'échec de la caméra.
function cameraErrorMessage(error: unknown): string {
  const name = error instanceof DOMException ? error.name : "";
  if (name === "NotAllowedError" || name === "SecurityError")
    return "L’accès à la caméra a été refusé. Autorisez la caméra dans les réglages du navigateur, ou saisissez le code ci-dessous.";
  if (name === "NotFoundError" || name === "OverconstrainedError")
    return "Aucune caméra n’a été trouvée sur cet appareil. Saisissez le code ci-dessous.";
  if (name === "NotReadableError")
    return "La caméra est utilisée par une autre application. Fermez-la, puis réessayez.";
  return "Impossible de démarrer la caméra. Saisissez le code ci-dessous.";
}

type BarcodeScannerProps = {
  onDetected: (code: string) => void;
};

export function BarcodeScanner({ onDetected }: BarcodeScannerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [state, setState] = useState<ScannerState>({ status: "starting" });
  // Toujours la dernière fonction reçue, sans redémarrer la caméra à chaque rendu.
  const onDetectedRef = useRef(onDetected);
  useEffect(() => {
    onDetectedRef.current = onDetected;
  }, [onDetected]);

  useEffect(() => {
    let stream: MediaStream | null = null;
    let timer: number | undefined;
    let stopped = false;

    function stop() {
      stopped = true;
      window.clearTimeout(timer);
      stream?.getTracks().forEach((track) => track.stop());
    }

    async function start() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setState({
          status: "error",
          message: window.isSecureContext
            ? "Ce navigateur ne permet pas d’utiliser la caméra. Saisissez le code ci-dessous."
            : "La caméra nécessite une connexion sécurisée (HTTPS). Saisissez le code ci-dessous.",
        });
        return;
      }

      try {
        // Caméra et lecteur en parallèle : le polyfill se charge pendant l'autorisation.
        const [mediaStream, detector] = await Promise.all([
          navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 } },
            audio: false,
          }).then((mediaStream) => {
            stream = mediaStream;
            if (stopped) stop();
            return mediaStream;
          }),
          getBarcodeDetector(),
        ]);
        stream = mediaStream;
        if (stopped) return stop();

        const video = videoRef.current;
        if (!video) return stop();
        video.srcObject = mediaStream;
        await video.play();
        setState({ status: "scanning" });

        const scan = async () => {
          if (stopped) return;
          try {
            if (video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
              const code = firstProductBarcode(await detector.detect(video));
              if (code && !stopped) {
                navigator.vibrate?.(80);
                stop();
                onDetectedRef.current(code);
                return;
              }
            }
          } catch {
            // Une image illisible n'arrête pas la lecture : on passe à la suivante.
          }
          timer = window.setTimeout(scan, SCAN_INTERVAL_MS);
        };
        void scan();
      } catch (error) {
        stop();
        setState({
          status: "error",
          message:
            error instanceof DOMException
              ? cameraErrorMessage(error)
              : "Le lecteur de code-barres n’a pas pu être chargé. Vérifiez votre connexion ou saisissez le code ci-dessous.",
        });
      }
    }

    void start();
    return stop;
  }, []);

  if (state.status === "error") {
    return (
      <p className="rounded-2xl bg-surface p-4 text-left text-danger" role="alert">
        {state.message}
      </p>
    );
  }

  return (
    <div className="relative aspect-[3/4] w-full overflow-hidden rounded-2xl bg-black">
      <video
        ref={videoRef}
        className="h-full w-full object-cover"
        playsInline
        muted
        aria-label="Image de la caméra"
      />

      {/* Cadre de visée : indique où placer le code-barres. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-8 top-1/2 h-32 -translate-y-1/2 rounded-xl border-2 border-white/90 shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]"
      />

      <p className="absolute inset-x-0 bottom-4 px-4 text-center text-sm text-white" role="status">
        {state.status === "starting"
          ? "Démarrage de la caméra…"
          : "Placez le code-barres dans le cadre."}
      </p>
    </div>
  );
}
