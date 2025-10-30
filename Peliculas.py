import csv
import os
import readchar
from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
import pyfiglet

console = Console()

console.print(
    Panel.fit(
        "[bold white on blue]GESTIÓN DE PELÍCULAS 🎬[/bold white on blue]",
        border_style="bright_blue",
        padding=(1, 5),
    )
)

titulo = pyfiglet.figlet_format("GESTIÓN DE PELÍCULAS", font="slant")
print(titulo)
console.print(f"[bold blue]{titulo}[/bold blue]")

# Funciones utilitarias


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    console.print("\n[dim]Presiona Enter para continuar...[/dim]")
    input()

# Funciones del CRUD

def inicializar_csv():
    """ se Crea el archivo CSV si no existe."""
    if not os.path.exists('peliculas.csv'):
        with open('peliculas.csv', mode='w', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)
            writer.writerow(['ID', 'Titulo', 'Genero', 'Duracion_min'])
        console.print("[green]Archivo 'peliculas.csv' se ha creado con éxito.[/green]")


def agregar_pelicula():
    limpiar_pantalla()
    console.print(Panel("[bold cyan]Agregar nueva película[/bold cyan]", border_style="cyan"))

# Validar que el ID solo contenga números
    while True:
        id = input("digita el ID: ").strip()
        if id.isdigit():
            break
        console.print("[red]El ID debe contener solamente números. Inténtalo de nuevo.[/red]")
#Validar título no vacío
    while True:
        titulo = input("Titulo de la pelicula: ").strip()
        if titulo:
            break
        console.print("[red]El título NO PUEDE estar vacío.[/red]")

#Validar género no vacío
    while True:
        genero = input("Género de la pelicula: ").strip()
        if genero:
            break
        console.print("[red]El género no puede estar vacío.[/red]")

# Validar duración numérica y positiva
    while True:
        duracion = input("Duración (min): ").strip()
        if duracion.isdigit() and int(duracion) > 0:
            break
        console.print("[red]La duración debe ser un número positivo.[/red]")

#Guardar en CSV
    with open('peliculas.csv', mode='a', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow([id, titulo, genero, duracion])

    console.print(f"[bold green]Película '{titulo}' agregada correctamente.[/bold green]")
    pausar()


def listar_peliculas():
    limpiar_pantalla()
    console.print(Panel("[bold yellow]Listado de películas[/bold yellow]", border_style="yellow"))

    if not os.path.exists('peliculas.csv'):
        console.print("[red]No existe el archivo de películas.[/red]")
        pausar()
        return

    with open('peliculas.csv', mode='r', newline='', encoding='utf-8') as archivo:
        reader = csv.DictReader(archivo)
        filas = list(reader)

    if not filas:
        console.print("[red]No hay películas registradas.[/red]")
        pausar()
        return

    tabla = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    tabla.add_column("ID", justify="center")
    tabla.add_column("Título", justify="left")
    tabla.add_column("Género", justify="center")
    tabla.add_column("Duración (min)", justify="center")

    for fila in filas:
        tabla.add_row(fila['ID'], fila['Titulo'], fila['Genero'], fila['Duracion_min'])

    console.print(tabla)
    pausar()


def actualizar_pelicula():
    limpiar_pantalla()

#Validar ID numérico
    while True:
        id_buscar = input("Ingresa el ID de la película que quieres actualizar: ").strip()
        if id_buscar.isdigit():
            break
        console.print("[red]El ID debe contener solo números.[/red]")

    peliculas = []
    encontrado = False

    with open('peliculas.csv', mode='r', encoding='utf-8') as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            if fila['ID'] == id_buscar:
                console.print(f"[cyan]Película encontrada:[/cyan] {fila['Titulo']}")

                # Validar nuevas entradas
                nuevo_titulo = input("Nuevo título (dejar vacío para mantener el actual): ").strip()
                nuevo_genero = input("Nuevo género (dejar vacío para mantener el actual): ").strip()
                nueva_duracion = input("Nueva duración (min, dejar vacío para mantener el actual): ").strip()

                if nuevo_titulo:
                    fila['Titulo'] = nuevo_titulo
                if nuevo_genero:
                    fila['Genero'] = nuevo_genero
                if nueva_duracion:
                    if nueva_duracion.isdigit() and int(nueva_duracion) > 0:
                        fila['Duracion_min'] = nueva_duracion
                    else:
                        console.print("[yellow]Duración inválida, se mantiene el valor anterior.[/yellow]")

                encontrado = True
            peliculas.append(fila)

    if encontrado:
        with open('peliculas.csv', mode='w', newline='', encoding='utf-8') as archivo:
            fieldnames = ['ID', 'Titulo', 'Genero', 'Duracion_min']
            writer = csv.DictWriter(archivo, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(peliculas)
        console.print("[bold green]Película actualizada con éxito.[/bold green]")
    else:
        console.print("[bold red]No se encontró una película con ese ID.[/bold red]")

    pausar()


def eliminar_pelicula():
    limpiar_pantalla()

#Validar ID numérico
    while True:
        id_eliminar = input("Ingresa el ID de la película que deseas eliminar: ").strip()
        if id_eliminar.isdigit():
            break
        console.print("[red]El ID debe contener solo números.[/red]")

    peliculas = []
    eliminado = False

    with open('peliculas.csv', mode='r', encoding='utf-8') as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            if fila['ID'] != id_eliminar:
                peliculas.append(fila)
            else:
                eliminado = True

    with open('peliculas.csv', mode='w', newline='', encoding='utf-8') as archivo:
        fieldnames = ['ID', 'Titulo', 'Genero', 'Duracion_min']
        writer = csv.DictWriter(archivo, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(peliculas)

    if eliminado:
        console.print("[bold green]Película eliminada correctamente.[/bold green]")
    else:
        console.print("[bold red]No se encontró ninguna película con ese ID.[/bold red]")

    pausar()

# Menú interactivo

def menu_peliculas():
    inicializar_csv()
    opciones = [
        "AGREGAR PELÍCULA",
        "LISTAR PELÍCULAS",
        "ACTUALIZAR PELÍCULA",
        "ELIMINAR PELÍCULA",
        "VOLVER AL MENÚ PRINCIPAL",
    ]
    seleccionado = 0

    while True:
        limpiar_pantalla()

        tabla = Table(
            title="[bold white on blue]GESTIÓN DE PELÍCULAS[/bold white on blue]",
            box=box.ROUNDED,
            border_style="blue",
            show_lines=True,
        )
        tabla.add_column("N°", justify="center", style="yellow")
        tabla.add_column("OPCIÓN", justify="left", style="white")

        for i, texto in enumerate(opciones):
            if i == seleccionado:
                tabla.add_row(str(i + 1), f"[black on red]{texto.center(40)}[/black on red]")
            else:
                tabla.add_row(str(i + 1), texto)

        console.print(tabla)
        console.print("\n[bold white]Usa ↑ ↓ para moverte y Enter para seleccionar.[/bold white]")

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
                actualizar_pelicula()
            elif seleccionado == 3:
                eliminar_pelicula()
            elif seleccionado == 4:
                break

# Ejecución principal

if __name__ == "__main__":
    menu_peliculas()
