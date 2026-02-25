import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from backend.core.firebase import firebase_service
from config import Config

DATA_DIR  = os.path.join(PROJECT_ROOT, "data")
CSV_FILE  = os.path.join(DATA_DIR, "python_w3schools.csv")

def import_lessons_from_csv():
    print("\n" + "=" * 60)
    print("📚 IMPORTADOR DE LECCIONES A FIREBASE")
    print("=" * 60 + "\n")

    if not os.path.exists(CSV_FILE):
        print(f"❌  No se encontró el archivo CSV en: {CSV_FILE}")
        print("    Ejecuta primero el scraper:")
        print("    python backend/scraping/scrape_w3Schools.py")
        return

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    print(f"📂  Archivo: {CSV_FILE}")
    print(f"    Lecciones en CSV: {len(df)}\n")

    
    print("🔍  Consultando lecciones existentes en Firestore...")
    existing_lessons = firebase_service.get_all_lessons()
    existing_titulos = {l.get("titulo", "").strip().lower() for l in existing_lessons}
    print(f"    Lecciones ya en Firestore: {len(existing_titulos)}\n")

    total_imported = 0
    skipped        = 0

    for index, row in df.iterrows():
        titulo = str(row.get("titulo", "Sin título")).strip()

        
        if titulo.lower() in existing_titulos:
            skipped += 1
            continue

        descripcion     = row.get("descripcion", "")
        ejemplos_codigo = row.get("ejemplos_codigo", "")

        lesson_data = {
            "numero_leccion":  int(row.get("numero_leccion", index + 1)),
            "titulo":          titulo,
            "descripcion":     str(descripcion)      if pd.notna(descripcion)     else "",
            "ejemplos_codigo": str(ejemplos_codigo)  if pd.notna(ejemplos_codigo) else "",
            "categoria":       str(row.get("categoria", "Python Básico")),
            "url":             str(row.get("url", "")) if pd.notna(row.get("url")) else "",
        }

        success, message, lesson_id = firebase_service.add_lesson(lesson_data)

        if success:
            total_imported += 1
            existing_titulos.add(titulo.lower())
            if total_imported % 10 == 0:
                print(f"   ✅  {total_imported} lecciones importadas...")
        else:
            print(f"   ❌  Error en '{titulo}': {message}")

    print(f"\n{'=' * 60}")
    print(f"✅  IMPORTACIÓN COMPLETADA")
    print(f"📊  Importadas : {total_imported}")
    print(f"⏭️   Omitidas   : {skipped}  (ya existían en Firestore)")
    print(f"{'=' * 60}\n")



def verify_import():
    print("\n🔍  Verificando importación...")
    print("-" * 60)

    lessons = firebase_service.get_all_lessons()
    print(f"Total de lecciones en Firestore: {len(lessons)}")

    categories = {}
    for lesson in lessons:
        cat = lesson.get("categoria", "Sin categoría")
        categories[cat] = categories.get(cat, 0) + 1

    print("\nLecciones por categoría:")
    for cat, count in sorted(categories.items()):
        print(f"  • {cat}: {count} lecciones")

    # Estadísticas de longitud para confirmar que el contenido llegó completo
    desc_lens = [len(str(l.get("descripcion", "")))     for l in lessons]
    code_lens = [len(str(l.get("ejemplos_codigo", ""))) for l in lessons]
    if desc_lens:
        print(f"\nDescripción  — min: {min(desc_lens)}c  |  max: {max(desc_lens)}c  |  media: {sum(desc_lens) // len(desc_lens)}c")
        print(f"Código       — min: {min(code_lens)}c  |  max: {max(code_lens)}c  |  media: {sum(code_lens) // len(code_lens)}c")

    # Primeras 5 lecciones ordenadas
    lessons_sorted = sorted(lessons, key=lambda x: x.get("numero_leccion", 0))
    print("\n📚  Primeras 5 lecciones:")
    for i, lesson in enumerate(lessons_sorted[:5], 1):
        print(f"  {i}. [{lesson.get('categoria')}] {lesson.get('titulo')}")

    print("-" * 60)

def clear_all_lessons():
    print("\n⚠️   ADVERTENCIA: Esto eliminará TODAS las lecciones de Firestore")
    confirm = input("¿Estás seguro? (escribe 'SI' para confirmar): ")

    if confirm != "SI":
        print("❌  Operación cancelada")
        return

    print("\n🗑️   Eliminando lecciones...")

    try:
        lessons = firebase_service.get_all_lessons()
        for lesson in lessons:
            firebase_service.db.collection(Config.LESSONS_COLLECTION).document(
                lesson["id"]
            ).delete()
        print(f"✅  {len(lessons)} lecciones eliminadas")
    except Exception as e:
        print(f"❌  Error al eliminar: {str(e)}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔥  FIREBASE - GESTIÓN DE LECCIONES")
    print("=" * 60)
    print("\nOpciones:")
    print("  1. Importar lecciones desde CSV")
    print("  2. Verificar lecciones importadas")
    print("  3. Eliminar todas las lecciones  ⚠️  CUIDADO")
    print("  4. Salir")
    print("=" * 60)

    opcion = input("\nSelecciona una opción (1-4): ").strip()

    if opcion == "1":
        import_lessons_from_csv()
        verify_import()
    elif opcion == "2":
        verify_import()
    elif opcion == "3":
        clear_all_lessons()
    elif opcion == "4":
        print("\n👋  ¡Hasta pronto!")
    else:
        print("\n❌  Opción inválida")