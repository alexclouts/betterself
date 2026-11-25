import type { BarcodeDetector as BarcodeDetectorPonyfill, DetectedBarcode } from "barcode-detector/ponyfill";

/*
 * Lecture des codes-barres des produits alimentaires (EAN-13, EAN-8, UPC-A, UPC-E).
 *
 * Le polyfill `barcode-detector`, basé sur ZXing en WebAssembly, est utilisé sur tous
 * les appareils, même là où l'API native BarcodeDetector existe (Chrome sur Android) :
 * un seul lecteur se comporte pareil partout, et le lecteur natif d'Android a échoué
 * sur des codes que ZXing lit sans peine. Il est chargé seulement à l'ouverture du
 * lecteur, et son fichier .wasm est servi par l'application plutôt que par un CDN.
 */

export const BARCODE_FORMATS = ["ean_13", "ean_8", "upc_a", "upc_e"] as const;

type Detector = Pick<BarcodeDetectorPonyfill, "detect">;

async function createDetector(): Promise<Detector> {
  const [{ BarcodeDetector, prepareZXingModule }, { default: wasmUrl }] = await Promise.all([
    import("barcode-detector/ponyfill"),
    import("zxing-wasm/reader/zxing_reader.wasm?url"),
  ]);

  // Charge le .wasm depuis l'application (aucune requête vers un site tiers).
  await prepareZXingModule({
    overrides: {
      locateFile: (path: string, prefix: string) => (path.endsWith(".wasm") ? wasmUrl : prefix + path),
    },
    fireImmediately: true,
  });
  return new BarcodeDetector({ formats: [...BARCODE_FORMATS] });
}

let detectorPromise: Promise<Detector> | null = null;

// Lecteur partagé entre les ouvertures du scanner ; un échec permet de réessayer.
export function getBarcodeDetector(): Promise<Detector> {
  detectorPromise ??= createDetector().catch((error: unknown) => {
    detectorPromise = null;
    throw error;
  });
  return detectorPromise;
}

// Clé de contrôle GTIN (EAN-8, UPC-A, EAN-13, GTIN-14) : écarte les lectures erronées.
export function hasValidCheckDigit(code: string): boolean {
  const digits = [...code].map(Number);
  const check = digits.pop();
  const sum = digits
    .reverse()
    .reduce((total, digit, index) => total + digit * (index % 2 === 0 ? 3 : 1), 0);
  return (10 - (sum % 10)) % 10 === check;
}

// Développe un UPC-E (8 chiffres) en UPC-A (12 chiffres), la forme enregistrée dans le catalogue.
export function expandUpcE(code: string): string | null {
  if (!/^[01]\d{7}$/.test(code)) return null;
  const [system, d1, d2, d3, d4, d5, d6, check] = code;

  let body: string;
  if (d6 <= "2") body = `${d1}${d2}${d6}0000${d3}${d4}${d5}`;
  else if (d6 === "3") body = `${d1}${d2}${d3}00000${d4}${d5}`;
  else if (d6 === "4") body = `${d1}${d2}${d3}${d4}00000${d5}`;
  else body = `${d1}${d2}${d3}${d4}${d5}0000${d6}`;

  return `${system}${body}${check}`;
}

/*
 * Code-barres d'un produit, prêt à chercher (8 à 14 chiffres, clé de contrôle valide),
 * ou null. Un UPC-E est développé en UPC-A.
 */
export function normalizeBarcode(raw: string, format?: string): string | null {
  const digits = raw.replace(/\s/g, "");
  if (!/^\d{8,14}$/.test(digits)) return null;

  const code = format === "upc_e" ? expandUpcE(digits) : digits;
  return code !== null && hasValidCheckDigit(code) ? code : null;
}

// Premier code-barres de produit valide parmi ceux détectés dans une image.
export function firstProductBarcode(barcodes: DetectedBarcode[]): string | null {
  for (const barcode of barcodes) {
    const code = normalizeBarcode(barcode.rawValue, barcode.format);
    if (code) return code;
  }
  return null;
}
