import sqlite3
import sys
from pathlib import Path

import duckdb

from betterself.core.serving_units import parse_serving, unit_for_product

"""
Construit le catalogue Open Food Facts (off.sqlite) à partir de l'export CSV.

Garde les produits vendus au Canada dont les valeurs nutritives sont complètes
et plausibles, et tire de `serving_size` l'unité propre à l'aliment (tranche,
barre, tasse…) avec son poids. Une portion en volume reçoit la mesure de
cuisine correspondante, et un liquide sans unité une tasse (250 ml ≈ 250 g).
Le catalogue précédent est conservé si l'export contient trop peu de produits.

Usage (depuis backend/) :
    uv run --group catalog python -m betterself.scripts.build_catalog <dossier> [minimum]
où <dossier> contient raw/products.csv.gz et catalog/.
"""

root = Path(sys.argv[1])
src = root / "raw" / "products.csv.gz"
tmp = root / "catalog" / "off.sqlite.tmp"
final = root / "catalog" / "off.sqlite"
MIN_PRODUCTS = int(sys.argv[2]) if len(sys.argv) > 2 else 10_000

QUERY = r"""
WITH p AS (
  SELECT code, trim(product_name) AS name, brands, categories_tags,
         serving_size,
         TRY_CAST(serving_quantity AS DOUBLE) AS serving_g,
         COALESCE(TRY_CAST("energy-kcal_100g" AS DOUBLE),
                  TRY_CAST("energy-kj_100g" AS DOUBLE) / 4.184) AS kcal,
         TRY_CAST(proteins_100g AS DOUBLE) AS protein,
         TRY_CAST(carbohydrates_100g AS DOUBLE) AS carbs,
         TRY_CAST(fat_100g AS DOUBLE) AS fat,
         COALESCE(TRY_CAST(unique_scans_n AS INTEGER), 0) AS scans,
         TRY_CAST(last_modified_t AS BIGINT) AS modified
  FROM read_csv(?, delim='\t', header=true, quote='', escape='',
                all_varchar=true, null_padding=true, ignore_errors=true,
                max_line_size=1000000)
  WHERE list_contains(string_split(countries_tags, ','), 'en:canada')
)
SELECT code, name, brands, categories_tags, serving_size, serving_g,
       kcal, protein, carbs, fat, scans, modified
FROM p
WHERE name <> '' AND kcal BETWEEN 0 AND 900
  AND protein BETWEEN 0 AND 100 AND carbs BETWEEN 0 AND 100
  AND fat BETWEEN 0 AND 100 AND protein + carbs + fat <= 105
"""


# Remplace `serving_size` par l'unité, son poids et l'indicateur de poids estimé.
def to_catalog_row(row: tuple) -> tuple:
    code, name, brands, categories, serving_size, serving_g, *nutrition = row
    info = parse_serving(serving_size)
    unit = unit_for_product(info, categories, serving_g)
    weight_is_estimated = info.serving_is_volume or (unit is not None and unit.is_estimated)
    return (
        code, name, brands, categories, serving_g,
        unit.singular if unit else None,
        unit.plural if unit else None,
        unit.grams if unit else None,
        int(weight_is_estimated),
        *nutrition,
    )


con = duckdb.connect()
con.execute("SET memory_limit='1GB'")
con.execute("SET preserve_insertion_order=false")
con.execute("SET threads=2")
rows = [to_catalog_row(row) for row in con.execute(QUERY, [str(src)]).fetchall()]
if len(rows) < MIN_PRODUCTS:
    sys.exit(f"Seulement {len(rows)} produits : ancien catalogue conservé.")

tmp.unlink(missing_ok=True)
db = sqlite3.connect(tmp)
db.executescript("""
CREATE TABLE products (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, brands TEXT, categories_tags TEXT,
  serving_g REAL, unit_name TEXT, unit_name_plural TEXT, unit_g REAL,
  weight_is_estimated INTEGER NOT NULL DEFAULT 0,
  kcal_100g REAL, protein_100g REAL, carbs_100g REAL,
  fat_100g REAL, scans INTEGER, modified INTEGER);
CREATE VIRTUAL TABLE products_fts USING fts5(
  name, brands, content='products', tokenize='unicode61 remove_diacritics 2');
""")
db.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
db.execute("INSERT INTO products_fts(products_fts) VALUES ('rebuild')")
db.commit()
db.close()
tmp.replace(final)

with_unit = sum(1 for row in rows if row[5])
estimated = sum(row[8] for row in rows)
print(f"{len(rows)} produits dans {final} ({with_unit} avec une unité, {estimated} à poids estimé)")
