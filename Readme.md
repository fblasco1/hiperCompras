# Herramienta de Compras Optimizadas

## Objetivo del Proyecto  
Desarrollar una herramienta integral para que organizaciones sociales optimicen sus compras de alimentos, reduciendo costos en los comedores populares donde brindan alimentos de manera gratuita. Esta herramienta permitirá:  
1. **Procesar presupuestos de proveedores**, incluso si están en formatos no estructurados.  
2. **Extraer información de ofertas disponibles en la web** para obtener precios actualizados y comparables.  
3. **Realizar análisis y optimización** para seleccionar la mejor combinación de productos, marcas y presentaciones según precio, calidad y disponibilidad.  

El proyecto se estructura en dos grandes módulos: **Procesamiento de Presupuestos (OCR)** y **Extracción de Datos Web (Web Scraping)**, con la posibilidad de disponibilizar la información a través de una API.  

---

## Módulo 1: Procesamiento de Presupuestos (OCR)  

### Objetivo  
Permitir que presupuestos en formatos variados (PDFs, imágenes escaneadas, etc.) puedan ser sistematizados y utilizados para comparar precios y optimizar decisiones de compra.

### Estado Actual  
- Investigación inicial sobre herramientas OCR.  
- Identificación de casos de uso comunes y formatos de presupuesto.  

### Próximos Pasos  
1. **Selección de tecnología OCR:** Evaluar herramientas como Tesseract, AWS Textract, u otras alternativas.  
2. **Estandarización de datos:** Diseñar un esquema de datos que permita estructurar la información extraída.  
3. **Desarrollo del pipeline OCR:** Crear un script que automatice la extracción, limpieza y almacenamiento de datos de presupuestos.  
4. **Pruebas y ajuste iterativo:** Realizar pruebas con presupuestos reales y ajustar el procesamiento según los formatos comunes.  

---

## Módulo 2: Extracción de Datos Web (Web Scraping)  

### Objetivo  
Automatizar la extracción de ofertas de productos desde sitios web de supermercados para comparar precios y mantener información actualizada.  

### Estado Actual  
- **Desarrollado:**  
  - Script de web scraping para la cadena de supermercados **Diarco** utilizando Selenium.  
  - Obtención de datos básicos de ofertas de productos.  

### Próximos Pasos  
1. **Ampliación del scraping actual:**  
   - Crear un sistema para recorrer automáticamente las sucursales de Diarco.  
   - Guardar los datos obtenidos en un archivo CSV como primer paso hacia la estructuración.  
2. **Exploración de nuevas fuentes:**  
   - Identificar y mapear otras cadenas de supermercados con información de ofertas disponibles en la web.  
   - Desarrollar scripts para estas nuevas cadenas y unificar la estructura de datos obtenidos.  
3. **Integración con una base de datos:**  
   - Evaluar si es más adecuado utilizar PostgreSQL o una base de datos NoSQL, dependiendo de la naturaleza de los datos y el volumen esperado.  
   - Diseñar y configurar la base de datos seleccionada para un acceso más eficiente y organizado.  
4. **Optimización matemática:**  
   - Implementar un algoritmo que permita comparar precios de distintos supermercados y optimizar la elección de compras para una canasta específica de productos.  

---

## Disponibilización de la Información mediante una API  

### Tecnología Propuesta  
- **Framework:** FastAPI para desarrollar la API de manera eficiente y escalable.  
- **Base de Datos:** Por evaluar, considerando PostgreSQL como una opción relacional o una alternativa NoSQL en función del rendimiento y la flexibilidad requeridos.  

### Pasos a Seguir  
1. Definir las rutas y endpoints necesarios para acceder a los datos procesados (ofertas, presupuestos y análisis de optimización).  
2. Implementar los endpoints para realizar consultas filtradas según parámetros específicos (producto, marca, proveedor, entre otros).  
3. Asegurar la correcta integración entre los módulos OCR y Web Scraping con la API.  
4. Documentar la API utilizando herramientas como Swagger para facilitar su uso por parte de terceros.  

---

## Tecnologías Utilizadas  

- **Lenguaje:** Python.  
- **Librerías para OCR y Web Scraping:** Selenium, BeautifulSoup, Tesseract (o alternativa seleccionada).  
- **Framework de API:** FastAPI.  
- **Base de Datos:** Por definir entre PostgreSQL o una base NoSQL.  

---

Con esta estructura, buscamos construir una herramienta eficiente y escalable que optimice el impacto de los comedores populares en sus comunidades. ¡Manos a la obra!  
