import sys
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
sys.path.insert(0, PROJECT_ROOT)

import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag, NavigableString


BASE_URL     = "https://www.w3schools.com"
TUTORIAL_URL = f"{BASE_URL}/python/default.asp"


OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "python_w3schools.csv")


NOISE_IDS = {
    "topnav", "w3-top", "w3-bar", "sidebar", "right-side",
    "tnb-button", "tnb-form", "cookiebar", "adngin",
}


NOISE_CLASSES = {
    "w3-bar", "w3-bar-item", "prevnext", "w3-right", "w3-left",
    "w3-btn", "w3-green", "googlead", "adsbygoogle", "cookiebar",
    "feedbackbtn", "w3-padding-64",
}


NOISE_PHRASES = re.compile(
    r"^(Try it Yourself|❮\s*Previous|Next\s*❯|"
    r"W3Schools is optimized|COLOR PICKER|Get Certified|"
    r"Top Tutorials|Top References|Top Examples|"
    r"Report Error|Forum|About|Spaces).*",
    re.IGNORECASE,
)


TEXT_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "li", "td", "th", "dt", "dd"}


CODE_CONTAINERS = {"pre", "code"}


def _is_real_tag(node) -> bool:
    """Return True only for actual HTML element nodes (not text/comment nodes)."""
    return isinstance(node, Tag)


def _has_noise_class(tag: Tag) -> bool:
    """Return True if any of the tag's CSS classes are in NOISE_CLASSES."""
    return bool(set(tag.get("class") or []) & NOISE_CLASSES)


def _clean_main(main_div: Tag) -> Tag:
    
    
    to_remove = []

    for node in main_div.find_all(True):
        if not _is_real_tag(node):
            continue

       
        if node.get("id") in NOISE_IDS:
            to_remove.append(node)
            continue

       
        if _has_noise_class(node):
            to_remove.append(node)
            continue

        
        if node.name == "a" and NOISE_PHRASES.match(node.get_text(strip=True)):
            to_remove.append(node)
            continue

        
        if node.name in {"script", "style", "noscript", "iframe", "ins", "hr"}:
            to_remove.append(node)
            continue

    
    for node in to_remove:
        try:
            node.decompose()
        except Exception:
            pass  

    return main_div


def _is_inside_code(tag: Tag) -> bool:
   
    for parent in tag.parents:
        if not _is_real_tag(parent):
            continue
        if parent.name in CODE_CONTAINERS:
            return True
        if "w3-code" in (parent.get("class") or []):
            return True
    return False


def _extract_explanation(main_div: Tag) -> str:
    
    lines = []

    for tag in main_div.find_all(TEXT_TAGS):
        if not _is_real_tag(tag):
            continue
        if _is_inside_code(tag):
            continue

        text = tag.get_text(separator=" ", strip=True)

        if not text:
            continue
        if NOISE_PHRASES.match(text):
            continue

        lines.append(text)

    full_text = "\n".join(lines)
    
    return re.sub(r"\n{3,}", "\n\n", full_text).strip()


def _extract_code_examples(main_div: Tag) -> str:
    
    seen   = set()
    blocks = []

    def _add(raw_text: str) -> None:
        # Normalise: strip trailing whitespace from every line, then strip whole block
        code = "\n".join(line.rstrip() for line in raw_text.splitlines()).strip()
        if code and code not in seen:
            seen.add(code)
            blocks.append(code)

    for div in main_div.find_all("div", class_="w3-code"):
        _add(div.get_text(separator="\n"))

    for pre in main_div.find_all("pre"):
        _add(pre.get_text(separator="\n"))

    return "\n---\n".join(blocks)


def _assign_category(idx: int, total: int) -> str:
    """Split lessons into three equal thirds."""
    third = total / 3
    if idx <= third:
        return "Python Básico"
    elif idx <= 2 * third:
        return "Python Intermedio"
    else:
        return "Python Avanzado"



def extraer_informacion_w3schools():
    print("\n" + "=" * 60)
    print("🐍  SCRAPER W3SCHOOLS — PYTHON TUTORIAL")
    print("=" * 60 + "\n")

    # 1. Fetch the index page
    try:
        resp = requests.get(TUTORIAL_URL, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        print(f"❌  No se pudo cargar la página de índice: {exc}")
        return None

    soup = BeautifulSoup(resp.content, "html.parser")
    menu = soup.find("div", {"id": "leftmenuinnerinner"})

    if not menu:
        print("❌  No se encontró el menú de navegación (id='leftmenuinnerinner')")
        return None

    enlaces = [a for a in menu.find_all("a") if a.get("href")]
    total   = len(enlaces)
    print(f"📋  Lecciones encontradas en el índice: {total}\n")

    datos_curso = []

    # 2. Scrape each lesson page
    for idx, enlace in enumerate(enlaces, 1):
        titulo = enlace.get_text(strip=True)
        href   = enlace["href"]

        if href.startswith("http"):
            url = href
        elif href.startswith("/"):
            url = BASE_URL + href
        else:
            url = f"{BASE_URL}/python/{href}"

        print(f"  [{idx:>3}/{total}]  {titulo}")

        try:
            page_resp = requests.get(url, timeout=15)
            page_resp.raise_for_status()
        except Exception as exc:
            print(f"           ⚠️  Error al cargar: {exc}")
            continue

        page_soup = BeautifulSoup(page_resp.content, "html.parser")
        main_div  = page_soup.find("div", {"id": "main"})

        if not main_div:
            print("           ⚠️  No se encontró #main en esta página")
            continue

        
        main_clean = BeautifulSoup(str(main_div), "html.parser").find("div", {"id": "main"})
        _clean_main(main_clean)

        datos_curso.append({
            "numero_leccion":   idx,
            "titulo":           titulo,
            "url":              url,
            "descripcion":      _extract_explanation(main_clean),
            "ejemplos_codigo":  _extract_code_examples(main_clean),
            "categoria":        _assign_category(idx, total),
        })

        time.sleep(1.2)  # Polite delay — do not remove

    if not datos_curso:
        print("\n❌  No se extrajo ningún dato.")
        return None

    df = pd.DataFrame(datos_curso)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n✅  CSV guardado en: {OUTPUT_CSV}")
    print(f"📊  Total de lecciones extraídas: {len(datos_curso)}")
    return df


def crear_estructura_curso(df):
    if df is None or df.empty:
        print("No hay datos para procesar.")
        return

    print("\n--- ESTRUCTURA DEL CURSO ---")
    print(df.groupby("categoria")["titulo"].count().to_string())
    print()

    for categoria in df["categoria"].unique():
        df_cat      = df[df["categoria"] == categoria]
        nombre_arch = os.path.join(
            OUTPUT_DIR,
            f"python_{categoria.replace(' ', '_').lower()}.csv"
        )
        df_cat.to_csv(nombre_arch, index=False, encoding="utf-8-sig")
        print(f"  ✅  {nombre_arch}  ({len(df_cat)} lecciones)")


if __name__ == "__main__":
    df = extraer_informacion_w3schools()
    if df is not None:
        crear_estructura_curso(df)
        print("\n🎉  ¡Proceso completado! Los CSV están listos para importar a Firebase.\n")