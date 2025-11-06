# GEMINI.md - Project Overview

This document provides a comprehensive overview of the "administrar-cine" project, intended to be used as instructional context for future interactions.

## Project Overview

This project is a command-line cinema management system written in Python. It allows users to manage movies, showtimes (funciones), and reservations. The application uses a menu-driven interface powered by the `rich` and `readchar` libraries for a modern and interactive user experience. The `curses` library is used for seat selection during the reservation process.

The application's data is stored in CSV files (`peliculas.csv`, `funciones.csv`) and a JSON file (`reservas.json`).

## Building and Running

### Dependencies

The project's dependencies are listed in the `pyproject.toml` file. The main dependencies are:

*   `rich`: For creating rich and beautiful command-line interfaces.
*   `readchar`: for reading single characters and keystrokes.
*   `ruff`: As a linter and formatter.
*   `pytest`: As a testing framework.

### Installation

To install the project's dependencies, run the following command:

```bash
pip install -e .[dev]
```

### Running the Application

To run the application, execute the `main.py` file:

```bash
python main.py
```

### Running Tests

The project uses `pytest` for testing. To run the tests, use the following command:

```bash
pytest
```

## Development Conventions

### Coding Style

The project uses `ruff` for linting and formatting. The configuration can be found in the `ruff.toml` file. The main conventions are:

*   Line length: 88 characters
*   Indentation: 4 spaces
*   Target Python version: 3.13
*   Quote style: double
*   Linting rules: E, F, I, W (with E501 ignored)

The project also uses `pre-commit` to enforce coding standards before committing code. The configuration is in the `.pre-commit-config.yaml` file.

### Testing

The project uses the `unittest` framework for testing, and the tests are located in the root directory with the `test_*.py` pattern. The tests use the `unittest.mock` library for mocking objects and functions.

## File Descriptions

| File                       | Description                                                                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`                  | The main entry point of the application. It displays the main menu and handles user input.                                               |
| `Peliculas.py`             | Handles the CRUD operations for movies. It reads and writes to `peliculas.csv`.                                                          |
| `funciones.py`             | Manages the showtimes for the movies. It reads and writes to `funciones.csv`.                                                            |
| `reservas.py`              | Handles the creation and viewing of reservations. It reads and writes to `reservas.json`.                                                |
| `asientos.py`              | Provides helper functions for creating and managing the seat map.                                                                        |
| `peliculas.csv`            | A CSV file that stores the movie data.                                                                                                   |
| `funciones.csv`            | A CSV file that stores the showtime data.                                                                                                |
| `reservas.json`            | A JSON file that stores the reservation data.                                                                                            |
| `test_peliculas.py`        | Contains the unit tests for the `Peliculas.py` module.                                                                                   |
| `test_funciones.py`        | Contains the unit tests for the `funciones.py` module.                                                                                   |
| `test_reservas.py`         | Contains the unit tests for the `reservas.py` module.                                                                                    |
| `pyproject.toml`           | The project's configuration file. It contains information about the project, its dependencies, and more.                                   |
| `ruff.toml`                | The configuration file for the `ruff` linter and formatter.                                                                              |
| `.pre-commit-config.yaml`  | The configuration file for the `pre-commit` hooks.                                                                                       |
| `.gitignore`               | Specifies which files and directories to ignore in a Git repository.                                                                     |
