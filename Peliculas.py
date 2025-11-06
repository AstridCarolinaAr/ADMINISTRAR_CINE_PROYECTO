import csv
import os

import readchar
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def validar_texto(valor: str, campo: str, max_len: int = 120) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ValueError(f"{campo} no puede estar vacío.")
    if len(valor) > max_len:
        raise ValueError(f"{campo} demasiado largo (máx {max_len} caracteres).")
    # permitimos letras, números, espacios, guiones, comas y puntos
    import re

    patron = r"^[A-Za-zÁÉÍÓÚáéíóú0-9\s\-\.,]+$"
    if not re.match(patron, valor):
        raise ValueError(f"{campo} contiene caracteres inválidos.")
    return valor


def validar_duracion(
    valor: str, campo: str = "Duración", minimo: int = 1, maximo: int = 600
) -> int:
    valor = (valor or "").strip()
    if not valor.isdigit():
        raise ValueError(f"{campo} debe ser un número entero positivo.")
    n = int(valor)
    if n < minimo or n > maximo:
        raise ValueError(f"{campo} debe estar entre {minimo} y {maximo} minutos.")
    return n


def verificar_encabezados_csv(ruta: str, expected):
    if not os.path.exists(ruta):
        return False, f"El archivo {ruta} no existe."
    try:
        with open(ruta, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return False, f"El archivo {ruta} está vacío o malformado."
            headers = [h.strip() for h in reader.fieldnames]
            if [h.lower() for h in headers] != [e.lower() for e in expected]:
                return False, f"Encabezados inesperados en {ruta}: {headers}"
    except Exception as e:
        return False, str(e)
    return True, None


def safe_write_csv(ruta: str, fieldnames: list, rows: list):
    temp = ruta + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp, ruta)
    except Exception:
        if os.path.exists(temp):
            os.remove(temp)
        raise


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    console.print("\n[dim]Presiona Enter para continuar...[/dim]")
    input()


# Funciones del CRUD


def inicializar_csv():
    """se Crea el archivo CSV si no existe."""
    if not os.path.exists("peliculas.csv"):
        with open("peliculas.csv", mode="w", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["ID", "Titulo", "Genero", "Duracion_min"])
        console.print(
            "[yellow]Archivo 'peliculas.csv' se ha creado con éxito.[/yellow]"
        )


def agregar_pelicula():
    limpiar_pantalla()
    console.print(
        Panel("[bold cyan]Agregar nueva película[/bold cyan]", border_style="cyan")
    )

    try:
        # ID
        if os.path.exists("peliculas.csv"):
            with open(
                "peliculas.csv", mode="r", newline="", encoding="utf-8"
            ) as archivo:
                reader = csv.DictReader(archivo)
                ids = [int(fila["ID"]) for fila in reader if fila["ID"].isdigit()]
                if ids:
                    id_ = str(max(ids) + 1)
                else:
                    id_ = "1"
        else:
            id_ = "1"
        console.print(f"[cyan]ID de película asignado automáticamente: {id_}[/cyan]")

        titulo_input = input("Título de la película (o '-' para salir): ")
        if titulo_input == "-":
            return
        titulo = validar_texto(titulo_input, "Título", max_len=120)

        genero_input = input("Género de la película (o '-' para salir): ")
        if genero_input == "-":
            return
        genero = validar_texto(genero_input, "Género", max_len=60)

        duracion_input = input("Duración (min) (o '-' para salir): ")
        if duracion_input == "-":
            return
        duracion = validar_duracion(duracion_input, "Duración", 1, 600)

        # Guardar (usar dict para safe write)
        row = {
            "ID": id_.strip(),
            "Titulo": titulo,
            "Genero": genero,
            "Duracion_min": str(duracion),
        }
        rows = []
        if os.path.exists("peliculas.csv"):
            with open(
                "peliculas.csv", mode="r", newline="", encoding="utf-8"
            ) as archivo:
                reader = csv.DictReader(archivo)
                rows = list(reader)
        rows.append(row)
        safe_write_csv(
            "peliculas.csv", ["ID", "Titulo", "Genero", "Duracion_min"], rows
        )

        console.print(
            f"[bold yellow]Película '{titulo}' agregada correctamente.[/bold yellow]"
        )
        pausar()
    except ValueError:
        console.print("[yellow]Error: valor inválido[/yellow]")
    except Exception as e:
        console.print(f"[red]Error al guardar la película: {e}[/red]")


def listar_peliculas():
    limpiar_pantalla()
    console.print(
        Panel("[bold yellow]Listado de películas[/bold yellow]", border_style="yellow")
    )

    try:
        with open("peliculas.csv", mode="r", newline="", encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)

            if not reader.fieldnames or [
                h.strip().lower() for h in reader.fieldnames
            ] != [e.lower() for e in ["ID", "Titulo", "Genero", "Duracion_min"]]:
                console.print(
                    "[yellow]Encabezados inesperados en peliculas.csv[/yellow]"
                )
                pausar()
                return

            filas = []
            for fila in reader:
                # ignorar filas malformadas
                if not all(
                    k in fila for k in ["ID", "Titulo", "Genero", "Duracion_min"]
                ):
                    continue
                filas.append(
                    {
                        k: (fila.get(k) or "").strip()
                        for k in ["ID", "Titulo", "Genero", "Duracion_min"]
                    }
                )
    except FileNotFoundError:
        console.print("[yellow]El archivo peliculas.csv no existe.[/yellow]")
        pausar()
        return
    except Exception as e:
        console.print(f"[red]Error leyendo el archivo: {e}[/red]")
        pausar()
        return

    if not filas:
        console.print("[yellow]No hay películas registradas.[/yellow]")
        pausar()
        return

    tabla = Table(
        show_header=True,
        header_style="bold bright_white",
        box=box.ROUNDED,
        border_style="bold dark_blue",
        show_lines=True,
    )
    tabla.add_column("ID", justify="center", style="orange3")
    tabla.add_column("Título", justify="left", style="bold grey70")
    tabla.add_column("Género", justify="center", style="bold grey70")
    tabla.add_column("Duración (min)", justify="center", style="bold grey70")

    for fila in filas:
        tabla.add_row(fila["ID"], fila["Titulo"], fila["Genero"], fila["Duracion_min"])

    console.print(tabla)
    pausar()


def actualizar_pelicula():
    limpiar_pantalla()

    # Validar ID numérico
    while True:
        id_buscar = input(
            "Ingresa el ID de la película que quieres actualizar: "
        ).strip()
        if id_buscar.isdigit():
            break
        console.print("[yellow]El ID debe contener solo números.[/yellow]")
    peliculas = []
    encontrado = False

    with open("peliculas.csv", mode="r", encoding="utf-8") as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            if fila["ID"] == id_buscar:
                console.print(f"[cyan]Película encontrada:[/cyan] {fila['Titulo']}")

                # Validar nuevas entradas
                nuevo_titulo = input(
                    "Nuevo título (dejar vacío para mantener el actual): "
                ).strip()
                nuevo_genero = input(
                    "Nuevo género (dejar vacío para mantener el actual): "
                ).strip()
                nueva_duracion = input(
                    "Nueva duración (min, dejar vacío para mantener el actual): "
                ).strip()

                if nuevo_titulo:
                    fila["Titulo"] = nuevo_titulo
                if nuevo_genero:
                    fila["Genero"] = nuevo_genero
                if nueva_duracion:
                    if nueva_duracion.isdigit() and int(nueva_duracion) > 0:
                        fila["Duracion_min"] = nueva_duracion
                    else:
                        console.print(
                            "[yellow]Duración inválida, se mantiene el valor anterior.[/yellow]"
                        )

                encontrado = True
            peliculas.append(fila)

    if encontrado:
        # normalizar rows ya llenadas en 'peliculas'
        try:
            safe_write_csv(
                "peliculas.csv", ["ID", "Titulo", "Genero", "Duracion_min"], peliculas
            )
            console.print("[bold yellow]Película actualizada con éxito.[/bold yellow]")
        except Exception as e:
            console.print(f"[red]Error al guardar cambios: {e}[/red]")
    else:
        console.print(
            "[bold yellow]No se encontró una película con ese ID.[/bold yellow]"
        )
    pausar()


def eliminar_pelicula():
    limpiar_pantalla()

    # Validar ID numérico
    while True:
        id_eliminar = input(
            "Ingresa el ID de la película que deseas eliminar: "
        ).strip()
        if id_eliminar.isdigit():
            break
        console.print("[red]El ID debe contener solo números.[/red]")

    peliculas = []
    eliminado = False

    with open("peliculas.csv", mode="r", encoding="utf-8") as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            if fila["ID"] != id_eliminar:
                peliculas.append(fila)
            else:
                eliminado = True

    with open("peliculas.csv", mode="w", newline="", encoding="utf-8") as archivo:
        fieldnames = ["ID", "Titulo", "Genero", "Duracion_min"]
        writer = csv.DictWriter(archivo, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(peliculas)

    if eliminado:
        console.print("[bold yellow]Película eliminada correctamente.[/bold yellow]")
    else:
        console.print(
            "[bold yellow]No se encontró ninguna película con ese ID.[/bold yellow]"
        )

    pausar()


# Menú interactivo


def cargar_peliculas_dict():
    peliculas = {}
    if not os.path.exists("peliculas.csv"):
        return peliculas
    with open("peliculas.csv", mode="r", newline="", encoding="utf-8") as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            peliculas[fila["ID"]] = fila["Titulo"]
    return peliculas


def menu_peliculas():
    inicializar_csv()
    opciones = [
        "AGREGAR PELÍCULA",
        "LISTAR PELÍCULAS",
        "BUSCAR POR GÉNERO",
        "ACTUALIZAR PELÍCULA",
        "ELIMINAR PELÍCULA",
        "VOLVER AL MENÚ PRINCIPAL",
    ]
    seleccionado = 0

    while True:
        limpiar_pantalla()

        tabla = Table(
            title="[bold black on gold1]GESTIÓN DE PELÍCULAS[/bold black on gold1]",
            box=box.ROUNDED,
            border_style="bold dark_blue",
            show_lines=True,
            title_style="bold bright_red",
            header_style="bold bright_white",
        )
        tabla.add_column("N°", justify="center", style="orange3")
        tabla.add_column("OPCIONES", justify="left", style="bold grey70")

        for i, texto in enumerate(opciones):
            if i == seleccionado:
                tabla.add_row(
                    str(i + 1),
                    f"[gold1 on dark_red]{texto.center(40)}[/gold1 on dark_red]",
                )
            else:
                tabla.add_row(str(i + 1), texto)

        console.print(tabla)
        console.print(
            "\n[bold white]Usa ↑ ↓ para moverte y Enter para seleccionar.[/bold white]"
        )

        tecla = readchar.readkey()

        if tecla == readchar.key.UP:
            seleccionado = (seleccionado - 1) % len(opciones)
        elif tecla == readchar.key.DOWN:
            seleccionado = (seleccionado + 1) % len(opciones)
        elif tecla == readchar.key.ENTER or tecla == readchar.key.CR:
            if seleccionado == 0:
                agregar_pelicula()
            elif seleccionado == 1:
                listar_peliculas()
            elif seleccionado == 2:
                buscar_peliculas_por_genero()
            elif seleccionado == 3:
                actualizar_pelicula()
            elif seleccionado == 4:
                eliminar_pelicula()
            elif seleccionado == 5:
                break


def buscar_peliculas_por_genero():
    """
    Buscar películas por género (coincidencia exacta)
    """
    limpiar_pantalla()
    console.print(
        Panel(
            "[bold gold1]Buscar películas por género[/bold gold1]",
            border_style="dark_red",
        )
    )

    # Validar existencia del archivo
    if not os.path.exists("peliculas.csv"):
        console.print("[yellow]No existe el archivo 'peliculas.csv'.[/yellow]")
        pausar()
        return

    # Validar y leer encabezados del CSV
    try:
        with open("peliculas.csv", mode="r", newline="", encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)
            expected = ["ID", "Titulo", "Genero", "Duracion_min"]
            if reader.fieldnames is None:
                console.print(
                    "[yellow]El archivo 'peliculas.csv' está vacío o malformado.[/yellow]"
                )
                pausar()
                return
            headers = [h.strip() for h in reader.fieldnames]
            if headers != expected:
                console.print(
                    f"[yellow]Encabezados inesperados en 'peliculas.csv'. Se esperaban: {expected}[/yellow]"
                )
                console.print(f"[yellow]Encabezados encontrados: {headers}[/yellow]")
                pausar()
                return
    except Exception as e:
        console.print(f"[red]Error al leer 'peliculas.csv': {e}[/red]")
        pausar()
        return

    # Pedir género y validarlo
    while True:
        genero_buscar = input(
            "Ingresa el género a buscar (coincidencia exacta): "
        ).strip()
        if not genero_buscar:
            console.print(
                "[yellow]Búsqueda vacía. Intenta nuevamente o escribe 'q' para cancelar.[/yellow]"
            )
            opcion = (
                input("¿Cancelar? (s para sí / Enter para reintentar): ")
                .strip()
                .lower()
            )
            if opcion in ("s", "q"):
                console.print("[dim]Búsqueda cancelada.[/dim]")
                pausar()
                return
            continue
        if len(genero_buscar) > 50:
            console.print(
                "[yellow]El género es demasiado largo. Usa menos de 50 caracteres.[/yellow]"
            )
            continue
        break

    genero_buscar_norm = genero_buscar.lower()

    # Buscar y recopilar resultados por coincidencia exacta
    resultados = []
    try:
        with open("peliculas.csv", mode="r", newline="", encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)
            for fila in reader:
                if not all(
                    k in fila for k in ("ID", "Titulo", "Genero", "Duracion_min")
                ):
                    continue  # Salta filas malformadas

                genero_fila_raw = fila.get("Genero") or ""
                genero_fila = genero_fila_raw.strip().lower()

                if genero_buscar_norm == genero_fila:
                    id_val = (fila.get("ID") or "").strip()
                    titulo_val = (fila.get("Titulo") or "").strip()
                    duracion_val = (fila.get("Duracion_min") or "").strip()
                    resultados.append(
                        {
                            "ID": id_val,
                            "Titulo": titulo_val,
                            "Genero": genero_fila_raw.strip(),
                            "Duracion_min": duracion_val,
                        }
                    )
    except Exception as e:
        console.print(f"[red]Error al procesar 'peliculas.csv': {e}[/red]")
        pausar()
        return

    # Mostrar resultados
    if not resultados:
        console.print(
            f"[yellow]No se encontraron películas con el género exacto: '{genero_buscar}'[/yellow]"
        )
        pausar()
        return

    tabla = Table(
        show_header=True,
        header_style="bold bright_white",
        box=box.ROUNDED,
        border_style="bold dark_blue",
        show_lines=True,
    )
    tabla.add_column("ID", justify="center", style="orange3")
    tabla.add_column("Título", justify="left", style="bold grey70")
    tabla.add_column("Género", justify="center", style="bold grey70")
    tabla.add_column("Duración (min)", justify="center", style="bold grey70")

    for fila in resultados:
        tabla.add_row(fila["ID"], fila["Titulo"], fila["Genero"], fila["Duracion_min"])

    console.print(tabla)
    pausar()
