"""
Script para importar lecciones desde archivos CSV a Firebase Firestore
"""
import pandas as pd
import os
from backend.firebase_service import firebase_service
from config import Config


def import_lessons_from_csv():
    """
    Importa todas las lecciones desde los archivos CSV a Firestore
    """
    print("\n" + "="*60)
    print("📚 IMPORTADOR DE LECCIONES A FIREBASE")
    print("="*60 + "\n")
    
    # Directorio donde están los CSV
    data_dir = 'data'
    
    # Lista de archivos CSV - Solo importar el archivo completo para evitar duplicados
    csv_files = [
        'python_w3schools.csv'  # Este contiene todas las lecciones
    ]
    
    total_imported = 0
    
    # Verificar si el directorio existe
    if not os.path.exists(data_dir):
        print(f"❌ No se encontró el directorio '{data_dir}'")
        print("   Copiando archivos CSV desde uploads...")
        
        # Crear directorio
        os.makedirs(data_dir, exist_ok=True)
        
        # Copiar archivos desde uploads
        import shutil
        for csv_file in csv_files:
            src = f'/mnt/user-data/uploads/{csv_file}'
            dst = f'{data_dir}/{csv_file}'
            if os.path.exists(src):
                shutil.copy(src, dst)
                print(f"   ✅ Copiado: {csv_file}")
    
    # Procesar cada archivo CSV
    for csv_file in csv_files:
        filepath = os.path.join(data_dir, csv_file)
        
        if not os.path.exists(filepath):
            print(f"⚠️  Archivo no encontrado: {csv_file}")
            continue
        
        print(f"\n📂 Procesando: {csv_file}")
        print("-" * 60)
        
        try:
            # Leer CSV
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            print(f"   Lecciones encontradas: {len(df)}")
            
            # Importar cada lección
            for index, row in df.iterrows():
                lesson_data = {
                    'numero_leccion': int(row.get('numero_leccion', index + 1)),
                    'titulo': str(row.get('titulo', 'Sin título')),
                    'descripcion': str(row.get('descripcion', ''))[:500],  # Limitar a 500 chars
                    'ejemplos_codigo': str(row.get('ejemplos_codigo', ''))[:1000],  # Limitar a 1000 chars
                    'categoria': str(row.get('categoria', 'Python Básico')),
                    'url': str(row.get('url', '')) if pd.notna(row.get('url')) else ''
                }
                
                # Agregar a Firestore
                success, message, lesson_id = firebase_service.add_lesson(lesson_data)
                
                if success:
                    total_imported += 1
                    if (index + 1) % 10 == 0:  # Mostrar progreso cada 10 lecciones
                        print(f"   ✅ {index + 1}/{len(df)} lecciones importadas...")
                else:
                    print(f"   ❌ Error en lección {index + 1}: {message}")
            
            print(f"   ✅ Completado: {len(df)} lecciones de {csv_file}")
            
        except Exception as e:
            print(f"   ❌ Error al procesar {csv_file}: {str(e)}")
            continue
    
    print("\n" + "="*60)
    print(f"✅ IMPORTACIÓN COMPLETADA")
    print(f"📊 Total de lecciones importadas: {total_imported}")
    print("="*60 + "\n")


def verify_import():
    """
    Verificar que las lecciones se importaron correctamente
    """
    print("\n🔍 Verificando importación...")
    print("-" * 60)
    
    # Obtener todas las lecciones
    lessons = firebase_service.get_all_lessons()
    
    print(f"Total de lecciones en Firestore: {len(lessons)}")
    
    # Contar por categoría
    categories = {}
    for lesson in lessons:
        cat = lesson.get('categoria', 'Sin categoría')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nLecciones por categoría:")
    for cat, count in categories.items():
        print(f"  • {cat}: {count} lecciones")
    
    # Mostrar primeras 5 lecciones
    print("\n📚 Primeras 5 lecciones:")
    for i, lesson in enumerate(lessons[:5], 1):
        print(f"  {i}. [{lesson.get('categoria')}] {lesson.get('titulo')}")
    
    print("-" * 60)


def clear_all_lessons():
    """
    Eliminar todas las lecciones de Firestore (usar con precaución)
    """
    print("\n⚠️  ADVERTENCIA: Esto eliminará TODAS las lecciones de Firestore")
    confirm = input("¿Estás seguro? (escribe 'SI' para confirmar): ")
    
    if confirm != 'SI':
        print("❌ Operación cancelada")
        return
    
    print("\n🗑️  Eliminando lecciones...")
    
    try:
        # Obtener todas las lecciones
        lessons = firebase_service.get_all_lessons()
        
        # Eliminar cada una
        for lesson in lessons:
            firebase_service.db.collection(Config.LESSONS_COLLECTION).document(
                lesson['id']
            ).delete()
        
        print(f"✅ {len(lessons)} lecciones eliminadas")
        
    except Exception as e:
        print(f"❌ Error al eliminar: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🔥 FIREBASE - GESTIÓN DE LECCIONES")
    print("="*60)
    print("\nOpciones:")
    print("1. Importar lecciones desde CSV")
    print("2. Verificar lecciones importadas")
    print("3. Eliminar todas las lecciones (¡CUIDADO!)")
    print("4. Salir")
    print("="*60)
    
    opcion = input("\nSelecciona una opción (1-4): ").strip()
    
    if opcion == "1":
        import_lessons_from_csv()
        verify_import()
    elif opcion == "2":
        verify_import()
    elif opcion == "3":
        clear_all_lessons()
    elif opcion == "4":
        print("\n👋 ¡Hasta pronto!")
    else:
        print("\n❌ Opción inválida")