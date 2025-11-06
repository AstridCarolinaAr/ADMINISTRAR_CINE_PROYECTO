`# Administrar Cine`

Descripción
- Aplicación en Python para administrar películas en cartelera, funciones (horarios y salas) y reservas de boletos con selección simple de asientos.

Archivos de datos
- `peliculas.csv` — lista de películas.
- `funciones.csv` — funciones / proyecciones.
- `reservas.json` — lista de reservas (array de objetos JSON).

Formato de los archivos

- `peliculas.csv` (encabezado):  Ejemplo:  Ejemplo:  Ejemplo:- `funciones.csv` (encabezado):
  Ejemplo:
- `funciones.csv` (encabezado):
-   `asientos_disponibles` puede ser un número total o una representación (p. ej. 50). Ejemplo:
- - `reservas.json` (array de objetos). Cada reserva incluye selección de asientos:
  ```json
  {
    "id_reserva": 1,
    "nombre_cliente": "Ana Perez",
    "id_funcion": 1,
    "cantidad_boletos": 2,
    "asientos": ["A1","A2"],
    "fecha_reserva": "2025-10-31T15:20:00"
  }
  

# Crear y Activar entorno Virtual

python -m venv .venv
.venv\Scripts\activate
# Instalar dependencias
pip install -r requirements.txt
# Instalar dependencias
python main.py --help
   Agregar pelicula
python main.py add-movie --titulo "Nueva" --genero "Accion" --duracion 110
    Agregar funcion
python main.py add-function --id_pelicula 1 --sala 1 --horario "2025-11-01T19:00:00" --asientos 50
    Crear reserva con asientos
python main.py reserve --nombre "Luis" --id_funcion 1 --asientos A1 A2
   Ver reserva por funcion
python main.py list-reservations --id_funcion 1
    Buscar peliculas por genero
python main.py search-movies --genero Comedia
# Ejecutar pruebas
  pip install -r requirements-dev.txt
  pytest

# Configuracion pyproject.toml con ruff

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "C", "B", "D"]
ignore = ["E203", "W503"]

# Ejecutar ruff en todo el proyecto
ruff .

# Ejecutar con autocorrección 
ruff . --fix

  Integrantes

- Carolina Araque
- Valentina Chaparro
- Mateo Becerra
- Zharith Bedoya

