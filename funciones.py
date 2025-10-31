import csv
import os
import re

import readchar
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

ARCHIVO_FUNCIONES = "funciones.csv"


# Función para limpiar pantalla
def limpiar_pantalla():
    os.system("cls")


def cargar_funciones():
    funciones = []
    if not os.path.exists(ARCHIVO_FUNCIONES):
        return funciones
    try:
        with open(ARCHIVO_FUNCIONES, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            expected = [
                "id_funcion",
                "id_pelicula",
                "sala",
                "hora",
                "asientos_disponibles",
            ]
            if reader.fieldnames is None:
                return funciones
            headers = [h.strip() for h in reader.fieldnames]
            # aceptar encabezados en cualquier capitalización
            if [h.lower() for h in headers] != expected:
                console.print(
                    f"[yellow] Encabezados inesperados en {ARCHIVO_FUNCIONES}. Se esperaban: {expected}[/yellow]"
                )
                return funciones
            funciones = list(reader)
    except Exception as e:
        console.print(f"[red] Error al leer {ARCHIVO_FUNCIONES}: {e}[/red]")
    return funciones


def guardar_funcion(funciones):
    atributos = ["id_funcion", "id_pelicula", "sala", "hora", "asientos_disponibles"]
    temp = ARCHIVO_FUNCIONES + ".tmp"
    try:
        with open(temp, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=atributos)
            writer.writeheader()
            writer.writerows(funciones)
        os.replace(temp, ARCHIVO_FUNCIONES)
    except Exception as e:
        console.print(f"[red] Error guardando {ARCHIVO_FUNCIONES}: {e}[/red]")
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


def ver_funciones(funciones):
    if not funciones:
        console.print("[bold gold1] No hay funciones registradas.[/bold gold1]")
        return

    tabla = Table(
        title="[bold black on gold1]FUNCIONES DISPONIBLES[/bold black on gold1]",
        box=box.SQUARE,
        border_style="bold dark_blue",
        title_style="bold bright_red",
        header_style="bold bright_white",
        show_lines=True,
    )
    for atributo in [
        "id_funcion",
        "id_pelicula",
        "sala",
        "hora",
        "asientos_disponibles",
    ]:
        # dentro del for, reemplaza la add_column por:
        if atributo == "id_funcion":
            tabla.add_column(
                atributo.capitalize(), justify="center", style="gold1 on dark_red"
            )
        elif atributo == "id_pelicula":
            tabla.add_column(
                atributo.capitalize(), justify="center", style="gold1 on dark_red"
            )
        else:
            tabla.add_column(
                atributo.capitalize(), justify="center", style="gold1 on dark_red"
            )
    for fn in funciones:
        if not all(
            fn.get(k)
            for k in [
                "id_funcion",
                "id_pelicula",
                "sala",
                "hora",
                "asientos_disponibles",
            ]
        ):
            continue  # salta filas incompletas
        tabla.add_row(
            fn["id_funcion"],
            fn["id_pelicula"],
            fn["sala"],
            fn["hora"],
            fn["asientos_disponibles"],
        )

    console.print(tabla)


def crear_funcion():
    funciones = cargar_funciones()
    console.rule(
        "[bold white on dark_blue] Sistema de Funciones de Cine[/bold white on dark_blue]"
    )

    try:
        # Validar ID de función (solo números y único)
        while True:
            id_funcion = input("ID de la función (solo números): ").strip()
            if not id_funcion.isdigit():
                console.print("[red]El ID debe contener solo números.[/red]")
                continue
            if any(funcion["id_funcion"] == id_funcion for funcion in funciones):
                console.print(f"[red]Ya existe una función con ID {id_funcion}.[/red]")
                continue
            break

        # Validar que el ID de película exista en peliculas.csv
        peliculas_existentes = set()
        if os.path.exists("peliculas.csv"):
            with open("peliculas.csv", mode="r", encoding="utf-8") as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    if "ID" in fila:
                        peliculas_existentes.add(fila["ID"].strip())

        while True:
            id_pelicula = input("ID de la película: ").strip()
            if not id_pelicula:
                console.print("[red]El ID de la película no puede estar vacío.[/red]")
                continue
            if id_pelicula not in peliculas_existentes:
                console.print(
                    f"[red]No existe una película con ID {id_pelicula}.[/red]"
                )
                continue
            break

        # Validar sala (solo números)
        while True:
            sala = input("Sala (solo números): ").strip()
            if not sala.isdigit():
                console.print("[red]La sala debe contener solo números.[/red]")
                continue
            break

        # Validar hora con formato HH:MM
        while True:
            hora_input = input("Hora (formato HH:MM): ").strip()
            try:
                hora = validar_hora(hora_input, "Hora")
                # Validar que no haya otra función en la misma sala y hora
                conflicto = any(
                    f["sala"] == sala and f["hora"] == hora for f in funciones
                )
                if conflicto:
                    console.print(
                        f"[red]Ya existe una función en la sala {sala} a las {hora}. Elige otro horario o sala.[/red]"
                    )
                    continue  # vuelve a pedir hora
                break
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

        # Validar asientos disponibles
        while True:
            try:
                asientos_disponibles = validar_entero(
                    input("Asientos disponibles: "), "Asientos disponibles"
                )
                break
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

        nueva_funcion = {
            "id_funcion": id_funcion,
            "id_pelicula": id_pelicula,
            "sala": sala,
            "hora": hora,
            "asientos_disponibles": str(asientos_disponibles),
        }

        funciones.append(nueva_funcion)
        guardar_funcion(funciones)
        console.print("[green]Función creada exitosamente.[/green]")

    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")


def editar_funcion():
    funciones = cargar_funciones()
    ver_funciones(funciones)

    id_funcion = input("\n Ingrese el ID de la función a editar: ").strip()
    encontrada = False

    for funcion in funciones:
        if funcion["id_funcion"] == id_funcion:
            encontrada = True
            console.print("[yellow] Modificando función...[/yellow]")

            try:
                funcion["id_pelicula"] = validar_texto(
                    input(f"Nuevo ID de película (actual: {funcion['id_pelicula']}): ")
                    or funcion["id_pelicula"],
                    "ID de película",
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
                funcion["asientos_disponibles"] = str(
                    validar_entero(
                        input(
                            f"Nuevos asientos disponibles (actual: {funcion['asientos_disponibles']}): "
                        )
                        or funcion["asientos_disponibles"],
                        "Asientos disponibles",
                    )
                )

                guardar_funcion(funciones)
                console.print("[green] Función actualizada correctamente.[/green]")

            except ValueError as e:
                console.print(f"[red]{e}[/red]")

            break

    if not encontrada:
        console.print(
            f"[red] No se encontró una función con el ID '{id_funcion}'. Verifica e intenta nuevamente.[/red]"
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
                ver_funciones(cargar_funciones())
                pausar_pantalla()
            elif opciones[seleccionado] == "CREAR FUNCIÓN":
                crear_funcion()
                pausar_pantalla()
            elif opciones[seleccionado] == "EDITAR FUNCIÓN":
                editar_funcion()
                pausar_pantalla()
            elif opciones[seleccionado] == "VOLVER":
                break
