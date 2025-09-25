# Data_Bigtelligent

## Descripción

Este proyecto permite comparar dos archivos CSV de stock (por ejemplo, vistas de inventario de un sistema) y genera un informe detallado de las diferencias y coincidencias entre ambos archivos. Es útil para validar migraciones, integraciones o cambios en sistemas de inventario.

## Uso

El script principal es `comparacion_stock.py`. Compara dos archivos CSV utilizando una o más columnas como clave compuesta y genera cuatro archivos de salida:

- **<prefix>_coinciden_completamente.csv**: Filas que existen en ambos archivos y son idénticas en todas las columnas.
- **<prefix>_difieren.csv**: Filas que existen en ambos archivos (por clave) pero difieren en alguna columna. Incluye una columna `diff_cols` con los nombres de las columnas que difieren.
- **<prefix>_solo_en_v2.csv**: Filas que existen solo en el archivo nuevo (v2).
- **<prefix>_solo_en_v1.csv**: Filas que existen solo en el archivo original (v1).

Además, imprime un resumen por consola con el conteo de cada tipo de fila y las rutas de los archivos generados.

### Ejemplo de ejecución

En Windows (cmd.exe):

```
python comparacion_stock.py "v_Item Availability View.csv" "v_Item Availability View_V2.csv" --outdir ./salida --prefix resultado --keys ItemNo LocationCode
```

### Argumentos

- `csv_v1`: Ruta al archivo CSV original (v1).
- `csv_v2`: Ruta al archivo CSV nuevo (v2).
- `--keys`: Lista de columnas que forman la clave compuesta para comparar filas (por defecto: `ItemNo LocationCode`).
- `--outdir`: Carpeta donde se guardarán los resultados (por defecto: carpeta actual).
- `--prefix`: Prefijo para los archivos de salida (opcional).

## Requisitos

- Python 3.7+
- pandas

Instalación de dependencias:

```
pip install pandas
```

## Estructura del proyecto

- `comparacion_stock.py`: Script principal de comparación.
- `salida/`: Carpeta donde se generan los resultados.
- `v_Item Availability View.csv`, `v_Item Availability View_V2.csv`: Ejemplo de archivos de entrada.

## Autor

Desarrollado para el equipo de Data Bigtelligent.
