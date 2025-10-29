import json
import os

import readchar
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reservas import ejecutar_reserva

console = Console()

# FUNCIONES DE UI (Copias de ui.py)


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


# ==========================================================
# Funciones Marcadoras (Stubs) - ¡LO NUEVO!
# Estas reemplazan temporalmente a los archivos externos.
# ==========================================================


def menu_peliculas() -> None:
    """[STUB] Muestra el menú temporal de Películas."""
    limpiar_pantalla()
    mostrar_titulo("Gestión de Películas (TEMPORAL)")
    console.print(
        "[yellow]¡Hola! Aquí irá el menú completo de CRUD de películas.[/yellow]"
    )
    pausar_pantalla()


def menu_funciones() -> None:
    """[STUB] Muestra el menú temporal de Funciones."""
    limpiar_pantalla()
    mostrar_titulo("Gestión de Funciones (TEMPORAL)")
    console.print(
        "[yellow]¡Hola! Aquí irá el menú completo de CRUD de funciones.[/yellow]"
    )
    pausar_pantalla()


def buscar_por_genero() -> None:
    """[STUB] Función temporal para buscar."""
    limpiar_pantalla()
    mostrar_titulo("Buscar por Género (TEMPORAL)")
    console.print("[yellow]¡Hola! Aquí va la lógica de búsqueda y filtrado.[/yellow]")
    pausar_pantalla()


def crear_reserva() -> None:
    limpiar_pantalla()
    mostrar_titulo("Crear Reserva")

    console.print("[bold cyan]Ingresa los datos para la reserva:[/bold cyan]\n")
    nombre = input("Nombre del cliente: ")
    id_funcion = input("ID de función (simulado): ")

    asientos = ejecutar_reserva(nombre, id_funcion)

    limpiar_pantalla()
    mostrar_titulo("Resultado de la Reserva")

    if asientos:
        console.print("[bold green]Reserva guardada con éxito.[/bold green]")
        console.print(f"Asientos seleccionados: [white]{', '.join(asientos)}[/white]")
    else:
        console.print(
            "[bold red]No se seleccionaron asientos. Reserva cancelada.[/bold red]"
        )

    pausar_pantalla()


def ver_reservas() -> None:
    limpiar_pantalla()
    mostrar_titulo("Reservas por Función")

    ruta = "reservas.json"
    if not os.path.exists(ruta):
        console.print("[bold red]No hay reservas registradas.[/bold red]")
        pausar_pantalla()
        return

    with open(ruta, "r", encoding="utf-8") as f:
        reservas = json.load(f)

    if not reservas:
        console.print("[bold red]No hay reservas registradas.[/bold red]")
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
        console.print(f"\n[bold blue]Función: {id_funcion}[/bold blue]")
        tabla = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        tabla.add_column("ID Reserva", justify="center")
        tabla.add_column("Cliente", justify="left")
        tabla.add_column("Boletos", justify="center")
        tabla.add_column("Asientos", justify="left")

        for r in grupo:
            tabla.add_row(
                str(r["id_reserva"]),
                r["nombre_cliente"],
                str(r["cantidad_boletos"]),
                ", ".join(r["asientos"]),
            )

        console.print(tabla)

    pausar_pantalla()


def menu_principal() -> None:
    """Muestra el menú principal con navegación por teclas Up/Down y Enter."""
    opciones_texto = [
        "GESTIÓN DE PELÍCULAS",
        "GESTIÓN DE FUNCIONES",
        "CREAR RESERVA",
        "VER RESERVAS POR FUNCIÓN",
        "BUSCAR PELÍCULAS POR GÉNERO",
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
                # Calcula el ancho total deseado (ajústalo según tu consola)
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
        tecla = readchar.readkey()

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
                buscar_por_genero()
            elif seleccionado == 5:
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
