import os

import readchar
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from funciones import menu_funciones
from Peliculas import menu_peliculas
from reservas import crear_reserva, ver_reservas

console = Console()


# Función para limpiar pantalla
def limpiar_pantalla():
    os.system("cls")


# Función para mostrar el título
def mostrar_titulo(titulo: str):
    console.print(
        Panel(
            f"[bold black on yellow]{titulo.upper()}[/bold  black on yellow]",
            border_style="red",
            expand=False,
        )
    )


# Función para pausar (temporal)
def pausar_pantalla():
    console.print("\n[dim]Presiona Enter para continuar...[/dim]", end="")
    input()


def menu_principal() -> None:
    """Muestra el menú principal con navegación por teclas Up/Down y Enter."""
    opciones_texto = [
        "GESTIÓN DE PELÍCULAS",
        "GESTIÓN DE FUNCIONES",
        "CREAR RESERVA",
        "VER RESERVAS POR FUNCIÓN",
        "SALIR",
    ]

    seleccionado = 0  # índice de la opción actualmente seleccionada

    while True:
        limpiar_pantalla()

        # Creamos la tabla para mostrar el menú
        opciones = Table(
            title="[bold black on gold1]MENÚ PRINCIPAL[/bold black on gold1]",
            box=box.ROUNDED,
            border_style="bold dark_blue",
            title_style="bold bright_red",
            header_style="bold bright_white",
            show_lines=True,
        )
        opciones.add_column("N°", justify="center", style="orange3", no_wrap=True)
        opciones.add_column("OPCIÓN", justify="left", style="bold grey70")

        # llenamos las filas y marcamos la seleccionada
        for i, texto in enumerate(opciones_texto):
            numero = str(i + 1)
            if i == seleccionado:
                # Calcula el ancho total
                ancho_total = 50
                texto_formateado = texto.center(ancho_total)
                opciones.add_row(
                    numero,
                    f"[gold1 on dark_red]{texto_formateado}[/gold1 on dark_red]",
                )
            else:
                opciones.add_row(numero, texto)

        console.print(opciones)
        console.print(
            "\n[bold bright_white]Usa ↑ ↓ para navegar. Enter para seleccionar.[/bold bright_white]"
        )

        # Leer una tecla
        try:
            tecla = readchar.readkey()
        except Exception as e:
            console.print(f"[red]Error al leer tecla: {e}[/red]")
            tecla = ""

        # Movimientos con flechas o con las teclas 'w' y 's' (opcional)
        if tecla == readchar.key.UP:
            seleccionado = (seleccionado - 1) % len(opciones_texto)
        elif tecla == readchar.key.DOWN:
            seleccionado = (seleccionado + 1) % len(opciones_texto)
        elif tecla == readchar.key.ENTER or tecla == readchar.key.CR:
            if seleccionado == 0:
                menu_peliculas()
            elif seleccionado == 1:
                menu_funciones()
            elif seleccionado == 2:
                crear_reserva()
            elif seleccionado == 3:
                ver_reservas()
            elif seleccionado == 4:
                break
        else:
            if tecla.isdigit():
                n = int(tecla)
                if 1 <= n <= len(opciones_texto):
                    seleccionado = n - 1
                    continue
            continue


if __name__ == "__main__":
    menu_principal()
