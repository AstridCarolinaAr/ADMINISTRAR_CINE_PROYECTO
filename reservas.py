import curses
import json
import os
import re

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from funciones import cargar_funciones, guardar_funcion, ver_funciones
from Peliculas import cargar_peliculas_dict

console = Console()
# Configuración de la sala
filas = ["A", "B", "C", "D", "E"]
columnas = ["1", "2", "3", "4", "5", "6"]


def validar_id_funcion(id_funcion):
    funciones = cargar_funciones()
    return any(f["id_funcion"] == id_funcion for f in funciones)


# Función para limpiar pantalla
def limpiar_pantalla():
    os.system("cls")


# Función para mostrar el título
def mostrar_titulo(titulo: str):
    console.print(
        Panel(
            f"[bold white on dark_blue]{titulo.upper()}[/bold white on dark_blue]",
            border_style="dark_red",
            expand=False,
        )
    )


# Función para pausar (temporal)
def pausar_pantalla():
    console.print("\n[dim]Presiona Enter para continuar...[/dim]", end="")
    input()


def crear_reserva() -> None:
    limpiar_pantalla()
    mostrar_titulo("Crear Reserva")

    console.print(
        "[bold black on gold1]Ingresa los datos para la reserva:[/bold black on gold1]\n"
    )
    import re

    # Validar nombre del cliente (sin números)
    while True:
        nombre = input("Nombre del cliente (o '-' para salir): ").strip()
        if nombre == "-":
            return
        if not nombre:
            console.print("[yellow]El nombre no puede estar vacío.[/yellow]")
            continue
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", nombre):
            console.print(
                "[yellow]El nombre solo puede contener letras y espacios. No se permiten números ni símbolos.[/yellow]"
            )
            continue
        break
    funciones = cargar_funciones()
    peliculas = cargar_peliculas_dict()

    if not funciones:
        console.print("[yellow]No hay funciones disponibles para reservar.[/yellow]")
        pausar_pantalla()
        return

        # Mostrar funciones disponibles antes de pedir el ID
    console.print("\n[bold yellow]Funciones disponibles:[/bold yellow]")
    ver_funciones(funciones, peliculas)

    # Validar ID de función
    while True:
        id_funcion = input("\nID de función (o '-' para salir): ").strip()
        if id_funcion == "-":
            return
        if any(f["id_funcion"] == id_funcion for f in funciones):
            break
        console.print(
            f"[yellow]La función con ID '{id_funcion}' no existe. Intenta de nuevo.[/yellow]"
        )

    # Selección de asientos
    asientos = ejecutar_reserva(nombre, id_funcion)

    limpiar_pantalla()
    mostrar_titulo("Resultado de la Reserva")
    if asientos:
        console.print("[bold yellow]Reserva guardada con éxito.[/bold yellow]")
        console.print(f"Asientos seleccionados: [white]{', '.join(asientos)}[/white]")
    else:
        console.print(
            "[bold yellow]No se seleccionaron asientos. Reserva cancelada.[/bold yellow]"
        )

    pausar_pantalla()


def ver_reservas() -> None:
    limpiar_pantalla()
    mostrar_titulo("Reservas por Función")

    ruta = "reservas.json"
    if not os.path.exists(ruta):
        console.print("[bold yellow]No hay reservas registradas.[/bold yellow]")
        pausar_pantalla()
        return

    with open(ruta, "r", encoding="utf-8") as f:
        reservas = json.load(f)

    if not reservas:
        console.print("[bold yellow]No hay reservas registradas.[/bold yellow]")
        pausar_pantalla()
        return

    # Agrupar reservas por función
    funciones = {}
    for reserva in reservas:
        id_funcion = reserva["id_funcion"]
        if id_funcion not in funciones:
            funciones[id_funcion] = []
        funciones[id_funcion].append(reserva)

    # Mostrar tabla por cada función
    for id_funcion, grupo in funciones.items():
        console.print(f"\n[gold1 on dark_red]Función: {id_funcion}[/gold1 on dark_red]")
        tabla = Table(
            show_header=True,
            header_style="bold bright_white",
            box=box.ROUNDED,
            border_style="bold dark_blue",
            show_lines=True,
        )
        tabla.add_column("ID Reserva", justify="center", style="orange3")
        tabla.add_column("Cliente", justify="left", style="bold grey70")
        tabla.add_column("Boletos", justify="center", style="bold grey70")
        tabla.add_column("Asientos", justify="left", style="bold grey70")

        for r in grupo:
            tabla.add_row(
                str(r["id_reserva"]),
                r["nombre_cliente"],
                str(r["cantidad_boletos"]),
                ", ".join(r["asientos"]),
            )

        console.print(tabla)

    pausar_pantalla()


def cargar_ocupados():
    ruta = "reservas.json"
    ocupados = []
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            reservas = json.load(f)
            for reserva in reservas:
                ocupados.extend(reserva.get("asientos", []))
    return ocupados


def guardar_reserva(nombre_cliente, id_funcion, asientos):
    ruta = "reservas.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            reservas = json.load(f)
    else:
        reservas = []

    nueva_reserva = {
        "id_reserva": len(reservas) + 1,
        "nombre_cliente": nombre_cliente,
        "id_funcion": id_funcion,
        "asientos": asientos,
        "cantidad_boletos": len(asientos),
    }

    reservas.append(nueva_reserva)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=4, ensure_ascii=False)


def seleccionar_asientos(stdscr, mapa):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Disponible
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)  # Ocupado
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Cursor
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)  # Seleccionado

    def clave(asiento):
        col = re.search(r"[A-Z]+", asiento).group()
        fila = int(re.search(r"\d+", asiento).group())
        return (fila, col)

    asientos_ordenados = sorted(mapa.keys(), key=clave)
    #  Extraer filas y columnas en orden correcto
    filas = sorted({int(re.search(r"\d+", a).group()) for a in asientos_ordenados})
    columnas = sorted(
        {re.search(r"[A-Z]+", a).group() for a in asientos_ordenados},
        key=lambda c: (len(c), c),
    )
    fila_idx = 0
    col_idx = 0
    seleccionados = []

    while True:
        stdscr.clear()
        stdscr.addstr(
            1,
            2,
            " SELECCIONA TUS ASIENTOS (ENTER para elegir, Q para salir)",
            curses.A_BOLD,
        )
        stdscr.addstr(
            2,
            2,
            " Verde=Libre | Rojo=Ocupado | Amarillo=Cursor | Verde claro=Seleccionado",
        )

        for i, fila in enumerate(filas):
            for j, col in enumerate(columnas):
                asiento = f"{col}{fila}"
                if asiento not in mapa:
                    continue
                y = 4 + i * 2
                x = 4 + j * 6
                estado = mapa.get(asiento, "libre")
                if estado == "ocupado":
                    color = curses.color_pair(2)
                elif i == fila_idx and j == col_idx:
                    color = curses.color_pair(3)
                elif asiento in seleccionados:
                    color = curses.color_pair(4)
                else:
                    color = curses.color_pair(1)

                stdscr.attron(color)
                stdscr.addstr(y, x, f"[{asiento}]")
                stdscr.attroff(color)
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and fila_idx > 0:
            fila_idx -= 1
        elif key == curses.KEY_DOWN and fila_idx < len(filas) - 1:
            fila_idx += 1
        elif key == curses.KEY_LEFT and col_idx > 0:
            col_idx -= 1
        elif key == curses.KEY_RIGHT and col_idx < len(columnas) - 1:
            col_idx += 1
        elif key == ord("\n"):
            asiento_actual = f"{columnas[col_idx]}{filas[fila_idx]}"
            if (
                mapa.get(asiento_actual) == "libre"
                and asiento_actual not in seleccionados
            ):
                seleccionados.append(asiento_actual)
        elif key in [ord("q"), ord("Q")]:
            break

    return seleccionados


def main():
    nombre = input("Nombre del cliente: ")
    id_funcion = input("ID de función (simulado): ")
    ocupados = []
    asientos = curses.wrapper(lambda stdscr: seleccionar_asientos(stdscr, ocupados))
    if asientos:
        guardar_reserva(nombre, id_funcion, asientos)
        console.print(
            f"\n[green]Reserva guardada  Asientos: {', '.join(asientos)}[/green]"
        )
    else:
        print("\nNo se seleccionaron asientos. Reserva cancelada.")


def ejecutar_reserva(nombre_cliente: str, id_funcion: str) -> list:
    funciones = cargar_funciones()
    funcion = next((f for f in funciones if f["id_funcion"] == id_funcion), None)

    if not funcion:
        console.print(
            f"[yellow]La función con ID '{id_funcion}' no existe. Reserva cancelada.[/yellow]"
        )
        return []

    mapa = funcion.get("asientos", {})
    disponibles = [k for k, v in mapa.items() if v == "libre"]

    if not disponibles:
        console.print(
            "[yellow]No quedan asientos disponibles para esta función.[/yellow]"
        )
        return []

    # Mostrar interfaz visual para seleccionar
    seleccionados = curses.wrapper(lambda stdscr: seleccionar_asientos(stdscr, mapa))

    if not seleccionados:
        console.print(
            "[yellow]No se seleccionaron asientos. Reserva cancelada.[/yellow]"
        )
        return []

    seleccion_valida = []
    for asiento in seleccionados:
        if mapa.get(asiento) == "libre":
            seleccion_valida.append(asiento)
        else:
            console.print(f"[yellow]Asiento inválido o ya ocupado: {asiento}[/yellow]")

    if not seleccion_valida:
        console.print(
            "[yellow]Ninguno de los asientos seleccionados está disponible.[/yellow]"
        )
        return []

    # Marcar como ocupados
    for asiento in seleccion_valida:
        mapa[asiento] = "ocupado"

    funcion["asientos"] = mapa
    funcion["asientos_disponibles"] = sum(1 for v in mapa.values() if v == "libre")

    guardar_funcion(funciones)
    guardar_reserva(nombre_cliente, id_funcion, seleccion_valida)

    return seleccion_valida
