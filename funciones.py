import csv
import os
import re

from rich.console import Console
from rich.table import Table

console = Console()

ARCHIVO_FUNCIONES = "funciones.csv"


def cargar_funciones():
    funciones = []
    if os.path.exists(ARCHIVO_FUNCIONES):
        with open(ARCHIVO_FUNCIONES, "r", newline="", encoding="utf-8") as csvfile:
            funciones = list(csv.DictReader(csvfile))
    return funciones


def guardar_funcion(funciones):
    atributos = ["id_funcion", "id_pelicula", "sala", "hora", "asientos_disponibles"]
    with open(ARCHIVO_FUNCIONES, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=atributos)
        writer.writeheader()
        writer.writerows(funciones)


def validar_texto(valor: str, campo: str) -> str:
    """Valida que solo tenga letras, números, espacios o guiones"""
    patron = r"^[A-Za-zÁÉÍÓÚáéíóú0-9\s\-:]+$"
    if not re.match(patron, valor):
        raise ValueError(
            f" {campo} solo puede contener letras, números, espacios o guiones."
        )
    return valor.strip()


def validar_entero(valor: str, campo: str) -> int:
    """Valida que el valor sea un número entero positivo"""
    if not valor.isdigit():
        raise ValueError(f" {campo} debe ser un número válido.")
    numero = int(valor)
    if numero < 0:
        raise ValueError(f" {campo} no puede ser negativo.")
    return numero


def ver_funciones(funciones):
    if not funciones:
        console.print("[red] No hay funciones registradas.[/red]")
        return

    tabla = Table(title="[bold cyan]FUNCIONES DISPONIBLES[/bold cyan]")
    for atributo in [
        "id_funcion",
        "id_pelicula",
        "sala",
        "hora",
        "asientos_disponibles",
    ]:
        tabla.add_column(atributo.capitalize(), justify="center", style="green")

    for fn in funciones:
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
    console.rule("[bold green]🎬 Crear Nueva Función[/bold green]")

    try:
        id_funcion = validar_texto(input("ID de la función: "), "ID de la función")
        if any(funcion["id_funcion"] == id_funcion for funcion in funciones):
            console.print(f"[red] Ya existe una función con ID {id_funcion}.[/red]")
            return

        id_pelicula = validar_texto(input("ID de la película: "), "ID de la película")
        sala = validar_texto(input("Sala: "), "Sala")
        hora = validar_texto(input("Hora (HH:MM): "), "Hora")
        asientos_disponibles = validar_entero(
            input("Asientos disponibles: "), "Asientos disponibles"
        )

        nueva_funcion = {
            "id_funcion": id_funcion,
            "id_pelicula": id_pelicula,
            "sala": sala,
            "hora": hora,
            "asientos_disponibles": str(asientos_disponibles),
        }

        funciones.append(nueva_funcion)
        guardar_funcion(funciones)
        console.print("[green] Función creada exitosamente.[/green]")

    except ValueError as e:
        console.print(f"[red]{e}[/red]")


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
        console.print("[red] No se encontró una función con ese ID.[/red]")


def main():
    while True:
        console.rule("[bold blue] Sistema de Funciones de Cine[/bold blue]")
        print("1 Crear Función")
        print("2 Ver Funciones")
        print("3 Editar Función")
        print("4 Salir")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            crear_funcion()
        elif opcion == "2":
            ver_funciones(cargar_funciones())
        elif opcion == "3":
            editar_funcion()
        elif opcion == "4":
            console.print("[bold cyan] Saliendo del sistema...[/bold cyan]")
            break
        else:
            console.print("[red] Opción no válida, intenta de nuevo.[/red]")


if __name__ == "__main__":
    main()
