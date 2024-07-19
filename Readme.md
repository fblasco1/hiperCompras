# Herramienta de compras optimizadas.

Este proyecto consiste en desarrollar una herramienta que permita a organizaciones sociales reducir los costos de los alimentos que compran para los espacios comunitarios donde brindan alimentos de forma gratuita. Esto requiere poder comparar precios del mismo producto en distintas presentaciones, marcas y proveedores. Para eso es necesario procesar información que no se encuentra estructurada y está en dos grandes fuentes de datos que son los presupestos generados por los proveedores y por otro la información disponible en la web. Una vez sistematizada la información queda el desafío de realizar la comparación y selección de la compra.

# Proyecto OCR para procesar presupuestos. 

# Proyecto de Web Scraping de Ofertas de Hipermercados

Este proyecto consiste en un script de web scraping desarrollado en Python utilizando Selenium para obtener las ofertas de productos de la cadena de supermercados Diarco y realizar análisis de los datos obtenidos.

## Instalación

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias necesarias utilizando pip:

    'pip install -r requirements.txt'


## Inicialización del Proyecto

1. Ejecuta el script `scrape_diarco_offers.py` para obtener las ofertas de productos de Diarco.

    'python scrape_diarco_offers.py'

## Acerca del Proyecto

Este proyecto tiene como objetivo proporcionar una herramienta para obtener información sobre las ofertas de productos en supermercados y realizar análisis sobre los datos recopilados. Actualmente se enfoca en la cadena de supermercados Diarco, pero se planea expandir para incluir otras cadenas.

## Cosas a Desarrollar

A continuación se presenta una lista de tareas pendientes y mejoras sugeridas para el proyecto:

- [ ] Almacenar los productos en un archivo CSV.
- [ ] Crear una parte del código que recorra todas las sucursales de Diarco.
- [ ] Explorar las webs de otros supermercados y desarrollar sus respectivos scrapers.
- [ ] Generar una optimización matemática que permita elegir dónde comprar una determinada canasta de artículos.
- [ ] Almacenar los productos en una base de datos para un acceso más eficiente y una mejor gestión de los datos.
