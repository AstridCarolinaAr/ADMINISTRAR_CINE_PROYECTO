import csv
import curses
import json
import os
import re

import readchar
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from asientos import crear_mapa_asientos, serializar_asientos

console = Console()
ARCHIVO_PELICULAS = "peliculas.csv"
ARCHIVO_FUNCIONES = "funciones.csv"
ARCHIVO_RESERVAS = "reservas.json"


# Función para limpiar pantalla
def limpiar_pantalla():
    os.system("cls")


def cargar_funciones():
    funciones = []
    ocupados_por_funcion = {}

    # Cargar reservas y agrupar asientos ocupados por función
    if os.path.exists(ARCHIVO_RESERVAS):
        with open(ARCHIVO_RESERVAS, "r", encoding="utf-8") as f:
            try:
                reservas = json.load(f)
                for r in reservas:
                    id_funcion = r.get("id_funcion")
                    if not id_funcion:
                        continue
                    if id_funcion not in ocupados_por_funcion:
                        ocupados_por_funcion[id_funcion] = []
                    ocupados_por_funcion[id_funcion].extend(r.get("asientos", []))
            except Exception as e:
                console.print(f"[yellow]Error al leer {ARCHIVO_RESERVAS}: {e}[/yellow]")

    # Cargar funciones desde CSV
    if not os.path.exists(ARCHIVO_FUNCIONES):
        return funciones

    try:
        with open(ARCHIVO_FUNCIONES, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected = [
                "id_funcion",
                "id_pelicula",
                "sala",
                "hora",
                "asientos_disponibles",
                "asientos",
            ]

            if reader.fieldnames is None:
                return funciones

            # Normalizar encabezados
            headers = [h.strip().lower().lstrip("\ufeff") for h in reader.fieldnames]

            # Verificar que todos los esperados estén presentes
            if not all(e in headers for e in expected):
                console.print(
                    f"[yellow]Encabezados inesperados en {ARCHIVO_FUNCIONES}. "
                    f"Se esperaban al menos: {expected}[/yellow]"
                )
            for row in reader:
                # Normalizar campos
                row["id_funcion"] = str(row.get("id_funcion", "")).strip()
                row["id_pelicula"] = str(row.get("id_pelicula", "")).strip()
                row["sala"] = str(row.get("sala", "")).strip()
                row["hora"] = str(row.get("hora", "")).strip()

                try:
                    row["asientos_disponibles"] = int(
                        row.get("asientos_disponibles", 0)
                    )
                except Exception:
                    row["asientos_disponibles"] = 0
                total = row["asientos_disponibles"]
                mapa = crear_mapa_asientos(total)
                # Marcar ocupados
                for ocupado in ocupados_por_funcion.get(row["id_funcion"], []):
                    if ocupado in mapa:
                        mapa[ocupado] = "ocupado"
                row["asientos"] = mapa
                row["asientos_ocupados"] = ocupados_por_funcion.get(
                    row["id_funcion"], []
                )

                funciones.append(row)

    except Exception as e:
        console.print(f"[yellow]Error al leer {ARCHIVO_FUNCIONES}: {e}[/yellow]")

    return funciones


def guardar_funcion(funciones):
    atributos = [
        "id_funcion",
        "id_pelicula",
        "sala",
        "hora",
        "asientos_disponibles",
        "asientos",
    ]
    temp = ARCHIVO_FUNCIONES + ".tmp"

    try:
        with open(temp, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=atributos)
            writer.writeheader()
            for fn in funciones:
                fila = {k: v for k, v in fn.items() if k in atributos}
                fila["id_funcion"] = str(fila.get("id_funcion", ""))
                fila["id_pelicula"] = str(fila.get("id_pelicula", ""))
                fila["sala"] = str(fila.get("sala", ""))
                fila["hora"] = str(fila.get("hora", ""))
                fila["asientos_disponibles"] = str(fila.get("asientos_disponibles", 0))
                fila["asientos"] = serializar_asientos(fila.get("asientos", {}))
                writer.writerow(fila)
        os.replace(temp, ARCHIVO_FUNCIONES)
    except Exception as e:
        console.print(f"[yellow] Error guardando {ARCHIVO_FUNCIONES}: {e}[/yellow]")
        if os.path.exists(temp):
            os.remove(temp)


def validar_texto(valor: str, campo: str, max_len: int = 64) -> str:
    """
    Valida que no esté vacío, su longitud <= max_len,contenga solo letras, números, espacios, guiones o dos puntos .
    Devuelve el string limpio (strip).
    """
    valor = (valor or "").strip()
    if not valor:
        raise ValueError(f" {campo} no puede estar vacío.")
    if len(valor) > max_len:
        raise ValueError(f" {campo} demasiado largo (máx {max_len} caracteres).")
    patron = r"^[A-Za-zÁÉÍÓÚáéíóú0-9\s\-:]+$"
    if not re.match(patron, valor):
        raise ValueError(
            f" {campo} solo puede contener letras, números, espacios o guiones."
        )
    return valor


def validar_entero(valor: str, campo: str, minimo: int = 0, maximo: int = 1000) -> int:
    """valida que sea numero para entre 0 a 1000"""
    valor = (valor or "").strip()
    if not valor.isdigit():
        raise ValueError(f" {campo} debe ser un número válido.")
    numero = int(valor)
    if numero < minimo:
        raise ValueError(f" {campo} no puede ser menor que {minimo}.")
    if numero > maximo:
        raise ValueError(f" {campo} no puede ser mayor que {maximo}.")
    return numero


def validar_hora(valor: str, campo: str) -> str:
    """Valida formato HH:MM y rango 00:00-23:59"""
    valor = valor.strip()
    if not re.match(r"^\d{1,2}:\d{2}$", valor):
        raise ValueError(f" {campo} debe tener formato HH:MM.")
    horas, minutos = valor.split(":")
    try:
        h = int(horas)
        m = int(minutos)
    except ValueError:
        raise ValueError(f" {campo} contiene valores no numéricos.")
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f" {campo} fuera de rango. Usa 00:00-23:59.")
    return f"{h:02d}:{m:02d}"


def calcular_max_asientos(stdscr):
    """
    Calcula el máximo de asientos que se pueden mostrar en la consola actual.
    - Cada asiento ocupa ~6 caracteres de ancho.
    - Cada fila ocupa 2 líneas de alto.
    """
    alto, ancho = stdscr.getmaxyx()
    max_columnas = ancho // 6
    max_filas = (alto - 4) // 2
    return max_columnas * max_filas


def ver_funciones(funciones, peliculas):
    if not funciones:
        console.print("[bold gold1] No hay funciones registradas.[/bold gold1]")
        return

    tabla = Table(
        title="[bold black on gold1]FUNCIONES DISPONIBLES[/bold black on gold1]",
        box=box.ROUNDED,
        border_style="bold dark_blue",
        title_style="bold bright_red",
        header_style="bold bright_white",
        show_lines=True,
    )

    # Columnas
    tabla.add_column("ID Función", justify="center", style="gold1 on dark_red")
    tabla.add_column("ID Película", justify="center", style="gold1 on dark_red")
    tabla.add_column("Título", justify="center", style="gold1 on dark_red")
    tabla.add_column("Sala", justify="center", style="gold1 on dark_red")
    tabla.add_column("Hora", justify="center", style="gold1 on dark_red")
    tabla.add_column("Disponibles", justify="center", style="gold1 on dark_red")
    tabla.add_column("Ocupados", justify="center", style="gold1 on dark_red")

    for fn in funciones:
        id_pelicula = fn.get("id_pelicula", "N/A")
        titulo = peliculas.get(id_pelicula, "N/A")
        mapa = fn.get("asientos", {})
        ocupados = sum(1 for v in mapa.values() if v == "ocupado")
        libres = sum(1 for v in mapa.values() if v == "libre")

        tabla.add_row(
            fn["id_funcion"],
            id_pelicula,
            titulo,
            fn["sala"],
            fn["hora"],
            str(libres),
            str(ocupados),
        )

    console.print(tabla)


def mostrar_tabla_peliculas():
    """
    Muestra la tabla de películas disponibles usando rich.Table.
    Devuelve un dict {id: título} para validación.
    Detecta encabezados aunque estén en mayúsculas, acentuados o con paréntesis.
    """
    peliculas = {}
    ruta = "peliculas.csv"
    if not os.path.exists(ruta):
        console.print("[yellow]No se encontró el archivo peliculas.csv[/yellow]")
        return peliculas

    try:
        with open(ruta, mode="r", encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)
            if not reader.fieldnames:
                console.print(
                    "[yellow]El archivo está vacío o sin encabezados.[/yellow]"
                )
                return peliculas

            # Normalizar encabezados
            encabezados = {
                h.strip()
                .lower()
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
                .replace("é", "e")
                .replace("á", "a")
                .replace("(", "")
                .replace(")", "")
                .replace(" ", ""): h
                for h in reader.fieldnames
            }

            id_field = encabezados.get("id") or encabezados.get("idpelicula")
            title_field = encabezados.get("titulo")
            genre_field = encabezados.get("genero")
            dur_field = next((h for k, h in encabezados.items() if "dura" in k), None)

            if not id_field:
                console.print(
                    "[yellow]No se encontró columna de ID en el archivo.[/yellow]"
                )
                return peliculas

            tabla = Table(
                title="[bold black on gold1]Listado de películas[/bold black on gold1]",
                show_header=True,
                header_style="bold bright_white",
                box=box.ROUNDED,
                border_style="bold dark_blue",
                show_lines=True,
            )
            tabla.add_column("ID", style="orange3")
            tabla.add_column("Título", style="bold grey70")
            tabla.add_column("Género", style="bold grey70")
            tabla.add_column("Duración", justify="right", style="bold grey70")

            for fila in reader:
                pid = str(fila.get(id_field, "")).strip()
                titulo = str(fila.get(title_field, "")).strip() if title_field else "-"
                genero = str(fila.get(genre_field, "")).strip() if genre_field else "-"
                duracion = str(fila.get(dur_field, "")).strip() if dur_field else "-"
                if pid:
                    peliculas[pid] = titulo or "-"
                    tabla.add_row(pid, titulo or "-", genero or "-", duracion or "-")

            if peliculas:
                console.print(tabla)
            else:
                console.print("[yellow]No hay películas registradas.[/yellow]")

    except Exception as e:
        console.print(f"[yellow]Error leyendo {ruta}: {e}[/yellow]")

    return peliculas


def crear_funcion():
    funciones = cargar_funciones()
    console.rule(
        "[bold white on dark_blue] Sistema de Funciones de Cine[/bold white on dark_blue]"
    )

    try:
        # Generar ID de función automáticamente (incremental)
        if funciones:
            id_funcion = str(len(funciones) + 1)
        else:
            id_funcion = "1"
        console.print(
            f"[cyan]ID de función asignado automáticamente: {id_funcion}[/cyan]"
        )

        # Mostrar tabla de películas y validar id
        peliculas_existentes = mostrar_tabla_peliculas()

        while True:
            id_pelicula = input("ID de la película (o '-' para salir): ").strip()
            if id_pelicula == "-":
                return
            if not id_pelicula:
                console.print(
                    "[yellow]El ID de la película no puede estar vacío.[/yellow]"
                )
                continue
            if id_pelicula not in peliculas_existentes:
                console.print(
                    f"[yellow]No existe una película con ID {id_pelicula}.[/yellow]"
                )
                continue
            break

        # Validar sala
        while True:
            sala = input("Escribe el numero de la sala (o '-' para salir): ").strip()
            if sala == "-":
                return
            if not sala.isdigit():
                console.print("[yellow]La sala debe contener solo números.[/yellow]")
                continue
            break

        # Valida hora con formato HH:MM
        while True:
            hora_input = input("Hora (formato HH:MM) (o '-' para salir): ").strip()
            if hora_input == "-":
                return
            try:
                hora = validar_hora(hora_input, "Hora")
                # Validar que no haya otra función en la misma sala y hora
                conflicto = any(
                    f["sala"] == sala and f["hora"] == hora for f in funciones
                )
                if conflicto:
                    console.print(
                        f"[yellow]Ya existe una función en la sala {sala} a las {hora}. Elige otro horario o sala.[/yellow]"
                    )
                    continue  # vuelve a pedir hora
                break
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

        # Valida asientos disponibles
        max_asientos = curses.wrapper(calcular_max_asientos)
        while True:
            try:
                asientos_input = input(
                    f"Asientos disponibles (máx {max_asientos}) (o '-' para salir): "
                )
                if asientos_input == "-":
                    return
                asientos_disponibles = validar_entero(
                    asientos_input,
                    "Asientos disponibles",
                )
                if asientos_disponibles > max_asientos:
                    console.print(
                        f"[yellow]El máximo permitido en esta consola es {max_asientos} asientos.[/yellow]"
                    )
                    continue
                if asientos_disponibles <= 0:
                    console.print("[yellow]Debes ingresar al menos 1 asiento.[/yellow]")
                    continue
                break
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

        # Genera el mapa de asientos automáticamente
        mapa = crear_mapa_asientos(asientos_disponibles)

        nueva_funcion = {
            "id_funcion": id_funcion,
            "id_pelicula": id_pelicula,
            "sala": sala,
            "hora": hora,
            "asientos_disponibles": str(asientos_disponibles),
            "asientos": mapa,
        }

        funciones.append(nueva_funcion)
        guardar_funcion(funciones)
        console.print("[bold yellow]Función creada exitosamente.[/bold yellow]")

    except Exception as e:
        console.print(f"[yellow]Error inesperado: {e}[/yellow]")


def editar_funcion():
    funciones = cargar_funciones()
    peliculas = mostrar_tabla_peliculas()
    ver_funciones(funciones, peliculas)

    id_funcion = input("\n Ingrese el ID de la función a editar: ").strip()
    encontrada = False

    for funcion in funciones:
        if funcion["id_funcion"] == id_funcion:
            encontrada = True
            console.print("[yellow] Modificando función...[/yellow]")

            try:
                console.print(
                    f"ID de película (actual: {funcion['id_pelicula']}) - No editable"
                )
                funcion["sala"] = validar_texto(
                    input(f"Nueva sala (actual: {funcion['sala']}): ")
                    or funcion["sala"],
                    "Sala",
                )
                funcion["hora"] = validar_texto(
                    input(f"Nuevo horario (actual: {funcion['hora']}): ")
                    or funcion["hora"],
                    "Hora",
                )
                console.print(
                    f"Asientos disponibles (actual: {funcion['asientos_disponibles']}) - No editable"
                )
                guardar_funcion(funciones)
                console.print(
                    "[bold yellow] Función actualizada correctamente.[/bold yellow]"
                )

            except ValueError as e:
                console.print(f"[red]{e}[/red]")
            break
    if not encontrada:
        console.print(
            f"[yellow] No se encontró una función con el ID '{id_funcion}'. Verifica e intenta nuevamente.[/yellow]"
        )


def pausar_pantalla():
    console.print("\n[dim]Presiona Enter para continuar...[/dim]", end="")
    input()


def mostrar_titulo(titulo: str):
    console.print(
        Panel(
            f"[bold black on yellow]{titulo.upper()}[/bold  black on yellow]",
            border_style="red",
            expand=False,
        )
    )


def menu_funciones() -> None:
    opciones = ["VER FUNCIONES", "CREAR FUNCIÓN", "EDITAR FUNCIÓN", "VOLVER"]
    seleccionado = 0

    while True:
        limpiar_pantalla()

        tabla = Table(
            title="[bold black on gold1]OPCIONES DE FUNCIONES[/bold black on gold1]",
            box=box.ROUNDED,
            border_style="bold dark_blue",
            title_style="bold bright_red",
            header_style="bold bright_white",
            show_lines=True,
        )
        tabla.add_column("N°", justify="center", style="orange3", no_wrap=True)
        tabla.add_column("Opción", justify="left", style="bold grey70")

        for i, texto in enumerate(opciones):
            numero = str(i + 1)
            if i == seleccionado:
                texto_formateado = texto.center(30)
                tabla.add_row(
                    numero, f"[gold1 on dark_red]{texto_formateado}[/gold1 on dark_red]"
                )
            else:
                tabla.add_row(numero, texto)

        console.print(tabla)
        console.print("[dim]Usa ↑ ↓ para navegar y Enter para seleccionar[/dim]")

        tecla = readchar.readkey()
        if tecla == readchar.key.UP:
            seleccionado = (seleccionado - 1) % len(opciones)
        elif tecla == readchar.key.DOWN:
            seleccionado = (seleccionado + 1) % len(opciones)
        elif tecla == readchar.key.ENTER:
            if opciones[seleccionado] == "VER FUNCIONES":
                limpiar_pantalla()
                peliculas = mostrar_tabla_peliculas()
                ver_funciones(cargar_funciones(), peliculas)
                pausar_pantalla()
            elif opciones[seleccionado] == "CREAR FUNCIÓN":
                crear_funcion()
                pausar_pantalla()
            elif opciones[seleccionado] == "EDITAR FUNCIÓN":
                editar_funcion()
                pausar_pantalla()
            elif opciones[seleccionado] == "VOLVER":
                break
