import curses
import json
import os

from rich.console import Console

console = Console()
# Configuración de la sala
filas = ["A", "B", "C", "D", "E"]
columnas = ["1", "2", "3", "4", "5", "6"]


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


def seleccionar_asientos(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Disponible
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)  # Ocupado
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Cursor
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)  # Seleccionado

    fila_idx = 0
    col_idx = 0
    seleccionados = []
    ocupados = cargar_ocupados()

    while True:
        stdscr.clear()
        stdscr.addstr(
            1,
            2,
            " SELECCIONA TUS ASIENTOS (ENTER para elegir, Q para salir)",
            curses.A_BOLD,
        )

        for i, fila in enumerate(filas):
            for j, col in enumerate(columnas):
                asiento = f"{fila}{col}"
                y = 3 + i * 3
                x = 5 + j * 10

                if asiento in ocupados:
                    color = curses.color_pair(2)
                elif i == fila_idx and j == col_idx:
                    color = curses.color_pair(3)
                elif asiento in seleccionados:
                    color = curses.color_pair(4)
                else:
                    color = curses.color_pair(1)

                stdscr.attron(color)
                stdscr.addstr(y, x, "┌────┐")
                stdscr.addstr(y + 1, x, f"│ {asiento} │")
                stdscr.addstr(y + 2, x, "└────┘")
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
            asiento_actual = f"{filas[fila_idx]}{columnas[col_idx]}"
            if asiento_actual not in ocupados and asiento_actual not in seleccionados:
                seleccionados.append(asiento_actual)
        elif key in [ord("q"), ord("Q")]:
            break

    return seleccionados


def main():
    nombre = input("Nombre del cliente: ")
    id_funcion = input("ID de función (simulado): ")
    asientos = curses.wrapper(seleccionar_asientos)
    if asientos:
        guardar_reserva(nombre, id_funcion, asientos)
        console.print(
            f"\n[green]Reserva guardada  Asientos: {', '.join(asientos)}[/green]"
        )
    else:
        print("\nNo se seleccionaron asientos. Reserva cancelada.")


def ejecutar_reserva(nombre_cliente, id_funcion):
    import curses

    asientos = curses.wrapper(seleccionar_asientos)
    if asientos:
        guardar_reserva(nombre_cliente, id_funcion, asientos)
        return asientos
    else:
        return []
