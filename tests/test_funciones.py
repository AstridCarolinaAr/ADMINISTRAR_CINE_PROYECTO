import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import funciones


class TestFunciones(unittest.TestCase):

    def setUp(self):
        # Datos de ejemplo
        self.funciones_mock = [
            {"id_funcion": "F1", "id_pelicula": "1", "sala": "Sala 1", "hora": "10:00", "asientos_disponibles": "50"},
            {"id_funcion": "F2", "id_pelicula": "2", "sala": "Sala 2", "hora": "12:00", "asientos_disponibles": "30"},
        ]

    # ------------------- validar_texto -------------------

    def test_validar_texto_valido(self):
        resultado = funciones.validar_texto("Sala 1-2", "Sala")
        self.assertEqual(resultado, "Sala 1-2")

    def test_validar_texto_invalido(self):
        with self.assertRaises(ValueError):
            funciones.validar_texto("Sala@1", "Sala")

    # ------------------- validar_entero -------------------

    def test_validar_entero_valido(self):
        resultado = funciones.validar_entero("25", "Asientos disponibles")
        self.assertEqual(resultado, 25)

    def test_validar_entero_negativo(self):
        with self.assertRaises(ValueError):
            funciones.validar_entero("-5", "Asientos disponibles")

    def test_validar_entero_no_numero(self):
        with self.assertRaises(ValueError):
            funciones.validar_entero("abc", "Asientos disponibles")

    # ------------------- cargar_funciones -------------------

    @patch("builtins.open", new_callable=mock_open, read_data="id_funcion,id_pelicula,sala,hora,asientos_disponibles\nF1,P1,Sala 1,10:00,50\n")
    @patch("os.path.exists", return_value=True)
    def test_cargar_funciones(self, mock_exists, mock_file):
        resultado = funciones.cargar_funciones()
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id_funcion"], "F1")

    @patch("os.path.exists", return_value=False)
    def test_cargar_funciones_archivo_no_existe(self, mock_exists):
        resultado = funciones.cargar_funciones()
        self.assertEqual(resultado, [])

    # ------------------- guardar_funcion -------------------

    @patch("builtins.open", new_callable=mock_open)
    def test_guardar_funcion_escribe_csv(self, mock_file):
        funciones.guardar_funcion(self.funciones_mock)
        mock_file.assert_called_once_with("funciones.csv.tmp", "w", newline="", encoding="utf-8")
        handle = mock_file()
        # Verificar que se haya escrito la cabecera
        handle.write.assert_any_call("id_funcion,id_pelicula,sala,hora,asientos_disponibles\r\n")

    # ------------------- ver_funciones -------------------

    @patch("funciones.console.print")
    def test_ver_funciones_vacia(self, mock_print):
        funciones.ver_funciones([])
        mock_print.assert_called_once_with("[red] No hay funciones registradas.[/red]")

    @patch("funciones.console.print")
    def test_ver_funciones_con_datos(self, mock_print, rich=None, Table=None):
        funciones.ver_funciones(self.funciones_mock)
        # Verifica que haya impreso una tabla Rich
        args, _ = mock_print.call_args
        from rich.table import Table
        assert isinstance(args[0], Table)
        # No debería mostrar mensaje de error
        for call in mock_print.call_args_list:
            if isinstance(call.args[0], str):
                assert "[red] No hay funciones registradas.[/red]" not in call.args[0]


if __name__ == "_main_":
    unittest.main()
