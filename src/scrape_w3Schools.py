import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os


def extraer_informacion_w3schools():
    """
    Extrae información del tutorial de Python de W3Schools
    y la guarda en un CSV estructurado para crear un curso interactivo
    """
    
    # URL base del tutorial de Python
    base_url = "https://www.w3schools.com"
    tutorial_url = f"{base_url}/python/default.asp"
    
    # Lista para almacenar la información
    datos_curso = []
    
    try:
        # Obtener la página principal del tutorial
        response = requests.get(tutorial_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar el menú de navegación con todos los temas
        menu = soup.find('div', {'id': 'leftmenuinnerinner'})
        
        if not menu:
            print("No se encontró el menú de navegación")
            return None
        
        # Obtener todos los enlaces del tutorial
        enlaces = menu.find_all('a')
        
        print(f"Se encontraron {len(enlaces)} lecciones")
        
        # Procesar cada enlace
        for idx, enlace in enumerate(enlaces, 1):
            titulo = enlace.get_text(strip=True)
            href = enlace.get('href')
            
            if not href:
                continue
                
            # Construir URL completa
            if href.startswith('http'):
                url_completa = href
            elif href.startswith('/'):
                url_completa = base_url + href
            else:
                # URL relativa sin /
                url_completa = f"{base_url}/python/{href}"
            
            print(f"Procesando {idx}/{len(enlaces)}: {titulo}")
            
            # Obtener el contenido de cada lección
            try:
                leccion_response = requests.get(url_completa)
                leccion_response.raise_for_status()
                leccion_soup = BeautifulSoup(leccion_response.content, 'html.parser')
                
                # Extraer el contenido principal
                contenido_div = leccion_soup.find('div', {'id': 'main'})
                
                if contenido_div:
                    # Extraer párrafos
                    parrafos = contenido_div.find_all(['p', 'h1', 'h2', 'h3'])
                    contenido_texto = '\n'.join([p.get_text(strip=True) for p in parrafos[:5]])  
                    
                    # Extraer ejemplos de código
                    ejemplos_codigo = contenido_div.find_all('div', class_='w3-code')
                    codigo = '\n---\n'.join([ej.get_text(strip=True) for ej in ejemplos_codigo[:3]])  
                    
                    # Guardar información
                    datos_curso.append({
                        'numero_leccion': idx,
                        'titulo': titulo,
                        'url': url_completa,
                        'descripcion': contenido_texto[:500],  # Limitar a 500 caracteres
                        'ejemplos_codigo': codigo[:1000] if codigo else '',  # Limitar a 1000 caracteres
                        'categoria': 'Python Básico' if idx <= 20 else 'Python Intermedio' if idx <= 50 else 'Python Avanzado'
                    })
                
                # Pausa para no sobrecargar el servidor
                time.sleep(1)
                
            except Exception as e:
                print(f"Error al procesar {titulo}: {str(e)}")
                continue
        
        # Crear DataFrame y guardar en CSV
        df = pd.DataFrame(datos_curso)
        
        # Crear directorio si no existe
        os.makedirs('datos_curso', exist_ok=True)
        
        # Guardar CSV
        archivo_csv = 'datos_curso/python_w3schools.csv'
        df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
        
        print(f"\n✓ Datos guardados exitosamente en: {archivo_csv}")
        print(f"✓ Total de lecciones extraídas: {len(datos_curso)}")
        
        # Mostrar resumen
        print("\n--- RESUMEN DEL CURSO ---")
        print(df[['numero_leccion', 'titulo', 'categoria']].head(10))
        
        return df
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        return None


def crear_estructura_curso(df):
    """
    Crea una estructura de curso más organizada a partir de los datos extraídos
    """
    if df is None or df.empty:
        print("No hay datos para procesar")
        return
    
    # Agrupar por categoría
    resumen = df.groupby('categoria').agg({
        'titulo': 'count',
        'numero_leccion': ['min', 'max']
    })
    
    print("\n--- ESTRUCTURA DEL CURSO ---")
    print(resumen)
    
    # Guardar estructura por categorías
    for categoria in df['categoria'].unique():
        df_categoria = df[df['categoria'] == categoria]
        nombre_archivo = f"datos_curso/python_{categoria.replace(' ', '_').lower()}.csv"
        df_categoria.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
        print(f"✓ Guardado: {nombre_archivo}")


if __name__ == "__main__":
    print("=== SCRAPER W3SCHOOLS - TUTORIAL PYTHON ===\n")
    
    # Extraer información
    df = extraer_informacion_w3schools()
    
    # Crear estructura del curso
    if df is not None:
        crear_estructura_curso(df)
        
        print("\n¡Proceso completado! Los archivos CSV están listos para tu curso interactivo.")