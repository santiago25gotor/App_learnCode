"""
import_lessons.py  ·  tools/
Importa las lecciones desde pylearn_lecciones.csv a Firestore.
Uso: python tools/import_lessons.py
"""

import pandas as pd
import os
import sys

# Subir hasta la raíz del proyecto (App_learnCode/)
# __file__ = backend/tools/import_lessons.py
# dirname x1 = backend/tools/
# dirname x2 = backend/
# dirname x3 = App_learnCode/  ← raíz
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz)

from backend.core.firebase import firebase_service
from config import Config


CSV_PATH = os.path.join('data', 'pylearn_lecciones.csv')


def borrar_lecciones_existentes():
    """Elimina todas las lecciones actuales de Firestore."""
    print("🗑️  Borrando lecciones existentes...")
    lecciones = firebase_service.db.collection(Config.LESSONS_COLLECTION).stream()
    batch = firebase_service.db.batch()
    count = 0
    for doc in lecciones:
        batch.delete(doc.reference)
        count += 1
        if count % 400 == 0:          # Firestore limita a 500 por batch
            batch.commit()
            batch = firebase_service.db.batch()
    if count % 400 != 0:
        batch.commit()
    print(f"   ✅ {count} lecciones eliminadas")


def importar_lecciones():
    print("\n" + "=" * 60)
    print("📚 IMPORTADOR DE LECCIONES — PYLEARN")
    print("=" * 60)

    if not os.path.exists(CSV_PATH):
        print(f"❌ No se encontró el archivo: {CSV_PATH}")
        print("   Copia 'pylearn_lecciones.csv' dentro de la carpeta 'data/'")
        return

    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    print(f"\n📂 Lecciones encontradas en el CSV: {len(df)}")

    # Distribución por categoría
    for cat, n in df['categoria'].value_counts().items():
        print(f"   • {cat}: {n}")

    confirmar = input("\n¿Borrar las lecciones actuales e importar? (s/N): ").strip().lower()
    if confirmar != 's':
        print("❌ Cancelado")
        return

    borrar_lecciones_existentes()

    print("\n📥 Importando lecciones...")
    ok = 0
    errores = 0

    for _, row in df.iterrows():
        lesson_data = {
            'numero_leccion': int(row['numero_leccion']),
            'titulo':         str(row['titulo']),
            'descripcion':    str(row['descripcion']),
            'ejemplos_codigo': str(row['ejemplos_codigo']),
            'categoria':      str(row['categoria']),
            'url':            str(row.get('url', '')),
        }
        success, message, _ = firebase_service.add_lesson(lesson_data)
        if success:
            ok += 1
            if ok % 5 == 0:
                print(f"   ✅ {ok}/{len(df)} importadas...")
        else:
            errores += 1
            print(f"   ❌ Error en lección {row['numero_leccion']}: {message}")

    print("\n" + "=" * 60)
    print(f"✅ Importación completada: {ok} lecciones")
    if errores:
        print(f"⚠️  Errores: {errores}")
    print("=" * 60)


def verificar():
    print("\n🔍 Verificando Firestore...")
    lecciones = firebase_service.get_all_lessons()
    print(f"Total en Firestore: {len(lecciones)}")
    from collections import Counter
    cats = Counter(l.get('categoria') for l in lecciones)
    for cat, n in cats.items():
        print(f"  • {cat}: {n}")
    print("\nPrimeras 5:")
    for l in lecciones[:5]:
        print(f"  [{l.get('categoria')}] L{l.get('numero_leccion')}: {l.get('titulo')}")


if __name__ == "__main__":
    print("\n1. Importar lecciones")
    print("2. Verificar Firestore")
    print("3. Salir")
    op = input("Opción: ").strip()

    if op == "1":
        importar_lecciones()
        verificar()
    elif op == "2":
        verificar()
    else:
        print("👋 Hasta pronto")