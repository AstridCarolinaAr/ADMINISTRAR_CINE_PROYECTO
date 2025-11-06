import os
import sys

# 💡 Simulación de curses para evitar error en Windows durante las pruebas
import unittest
from unittest.mock import MagicMock, mock_open, patch

import reservas

sys.modules["curses"] = MagicMock()
sys.modules["curses.wrapper"] = MagicMock()

# Añade la raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestReservas(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    @patch("os.path.exists", return_value=False)
    def test_guardar_reserva_crea_archivo(self, mock_exists, mock_file):
        """Verifica que se cree el archivo y se escriba una reserva."""
        reservas.guardar_reserva("Zharith", "FUNC1", ["A1", "A2"])
        mock_file.assert_called_once_with("reservas.json", "w", encoding="utf-8")
        handle = mock_file()
        handle.write.assert_called()  # Se escribió algo en el archivo

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"asientos": ["B1", "B2"]}]',
    )
    @patch("os.path.exists", return_value=True)
    def test_cargar_ocupados_lee_correctamente(self, mock_exists, mock_file):
        """Comprueba que los asientos ocupados se cargan correctamente."""
        ocupados = reservas.cargar_ocupados()
        self.assertIn("B1", ocupados)
        self.assertIn("B2", ocupados)
        self.assertEqual(len(ocupados), 2)

    @patch(
        "reservas.cargar_funciones",
        return_value=[
            {
                "id_funcion": "FUNC2",
                "asientos": {
                    "A1": "libre",
                    "A2": "libre",
                    "B1": "libre",
                    "B2": "libre",
                },
            }
        ],
    )
    @patch("reservas.cargar_ocupados", return_value=["A1", "A2"])
    @patch("reservas.guardar_reserva")
    @patch("reservas.curses.wrapper", return_value=["B1", "B2"])
    def test_ejecutar_reserva(
        self, mock_wrapper, mock_guardar, mock_ocupados, mock_funciones
    ):
        """Simula una reserva válida y verifica que se guarde correctamente."""
        asientos = reservas.ejecutar_reserva("Zharith", "FUNC2")
        self.assertEqual(asientos, ["B1", "B2"])
        mock_guardar.assert_called_once_with("Zharith", "FUNC2", ["B1", "B2"])

    @patch("reservas.cargar_funciones", return_value=[{"id_funcion": "FUNC3"}])
    @patch("reservas.curses.wrapper", return_value=[])
    @patch("reservas.guardar_reserva")
    def test_ejecutar_reserva_sin_asientos(
        self, mock_guardar, mock_wrapper, mock_funciones
    ):
        """Prueba cuando no se seleccionan asientos (reserva vacía)."""
        resultado = reservas.ejecutar_reserva("Zharith", "FUNC3")
        self.assertEqual(resultado, [])
        mock_guardar.assert_not_called()

    # --- Pruebas de validación y flujo principal ---

    @patch("reservas.cargar_funciones", return_value=[{"id_funcion": "F1"}])
    def test_validar_id_funcion_existente(self, mock_cargar):
        self.assertTrue(reservas.validar_id_funcion("F1"))

    @patch("reservas.cargar_funciones", return_value=[{"id_funcion": "F1"}])
    def test_validar_id_funcion_no_existente(self, mock_cargar):
        self.assertFalse(reservas.validar_id_funcion("F2"))

    @patch("builtins.input", side_effect=["Test Client", "F1"])
    @patch("reservas.cargar_funciones", return_value=[{"id_funcion": "F1"}])
    @patch("reservas.cargar_peliculas_dict", return_value={})
    @patch("reservas.ver_funciones")
    @patch("reservas.ejecutar_reserva", return_value=["A1"])
    @patch("reservas.console.print")
    @patch("reservas.pausar_pantalla")
    def test_crear_reserva(
        self,
        mock_pausar,
        mock_print,
        mock_ejecutar,
        mock_ver,
        mock_peliculas,
        mock_funciones,
        mock_input,
    ):
        reservas.crear_reserva()
        mock_ejecutar.assert_called_once_with("Test Client", "F1")
        # Verificar que se imprime el mensaje de éxito
        mock_print.assert_any_call(
            "[bold yellow]Reserva guardada con éxito.[/bold yellow]"
        )

    # --- Pruebas de visualización ---

    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"id_reserva": 1, "nombre_cliente": "User1", "id_funcion": "F1", "cantidad_boletos": 1, "asientos": ["A1"]}]',
    )
    @patch("reservas.console.print")
    @patch("reservas.pausar_pantalla")
    def test_ver_reservas(self, mock_pausar, mock_print, mock_open, mock_exists):
        from rich.table import Table

        reservas.ver_reservas()
        # Verifica que se haya impreso una tabla Rich
        self.assertTrue(
            any(isinstance(call.args[0], Table) for call in mock_print.call_args_list)
        )

    @patch("os.path.exists", return_value=False)
    @patch("reservas.console.print")
    @patch("reservas.pausar_pantalla")
    def test_ver_reservas_sin_archivo(self, mock_pausar, mock_print, mock_exists):
        reservas.ver_reservas()
        mock_print.assert_any_call(
            "[bold yellow]No hay reservas registradas.[/bold yellow]"
        )


if __name__ == "__main__":
    unittest.main()
