import re
import unicodedata

from sqlalchemy import ColumnElement, func

"""
Module pour la recherche textuelle et la manipulation de codes-barres.
Fournit des fonctions pour normaliser le texte, tokeniser les mots,
calculer le rang d'un nom selon les mots cherchés, et générer des candidats
de codes-barres à partir d'une requête.
"""


# Longueur d'un code EAN-13, format utilisé par Open Food Facts.
EAN13_LENGTH = 13

# Lettres accentuées et leur équivalent, pour comparer du texte dans PostgreSQL.
ACCENTED_LETTERS = "àâäáãåçèéêëìíîïñòóôöõùúûüýÿ"
PLAIN_LETTERS = "aaaaaaceeeeiiiinooooouuuuyy"


# Retire les accents et les majuscules.
def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


# Équivalent de `fold` pour une colonne SQL.
def folded_column(column) -> ColumnElement[str]:
    return func.translate(func.lower(func.coalesce(column, "")), ACCENTED_LETTERS, PLAIN_LETTERS)


# Découpe un texte en mots, sans ponctuation.
def tokenize(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", fold(text))


# Rang d'un nom selon les mots cherchés : plus il est petit, plus il est pertinent.
def name_rank(name: str, words: list[str]) -> int:
    name_words = tokenize(name)
    if name_words == words:
        return 0  # nom exact
    if name_words[:len(words)] == words:
        return 1  # commence par les mots cherchés
    if set(words) <= set(name_words):
        return 2  # contient tous les mots cherchés
    return 3      # partie d'un mot, ou marque


# Codes-barres possibles pour un terme, ou une liste vide si ce n'en est pas un.
# Les codes UPC (12 chiffres) sont complétés par des zéros chez Open Food Facts.
def barcode_candidates(query: str) -> list[str]:
    code = query.strip()
    if not (code.isascii() and code.isdigit() and 8 <= len(code) <= 14):
        return []
    return list(dict.fromkeys([code, code.zfill(EAN13_LENGTH)]))
