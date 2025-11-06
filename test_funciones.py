import unittest
from unittest.mock import MagicMock, mock_open, patch

import funciones


class TestFunciones(unittest.TestCase):
    def setUp(self):
        # Datos de ejemplo
        self.funciones_mock = [
            {
                "id_funcion": "F1",
                "id_pelicula": "P1",
                "sala": "Sala 1",
                "hora": "10:00",
                "asientos_disponibles": "50",
            },
            {
                "id_funcion": "F2",
                "id_pelicula": "P2",
                "sala": "Sala 2",
                "hora": "12:00",
                "asientos_disponibles": "30",
            },
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

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="id_funcion,id_pelicula,sala,hora,asientos_disponibles\nF1,P1,Sala 1,10:00,50\n",
    )
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

    @patch("os.replace")
    @patch("builtins.open", new_callable=mock_open)
    def test_guardar_funcion_escribe_csv(self, mock_file, mock_replace):
        funciones.guardar_funcion(self.funciones_mock)
        mock_file.assert_called_once_with(
            "funciones.csv.tmp", "w", newline="", encoding="utf-8"
        )
        handle = mock_file()
        # Verificar que se haya escrito la cabecera
        handle.write.assert_any_call(
            "id_funcion,id_pelicula,sala,hora,asientos_disponibles,asientos\r\n"
        )

    # ------------------- ver_funciones -------------------

    @patch("funciones.console.print")
    def test_ver_funciones_vacia(self, mock_print):
        funciones.ver_funciones([], {})
        mock_print.assert_called_once_with(
            "[bold gold1] No hay funciones registradas.[/bold gold1]"
        )

    @patch("funciones.console.print")
    def test_ver_funciones_con_datos(self, mock_print, rich=None, Table=None):
        funciones.ver_funciones(self.funciones_mock, {})
        # Verifica que haya impreso una tabla Rich
        args, _ = mock_print.call_args
        from rich.table import Table

        assert isinstance(args[0], Table)
        # No debería mostrar mensaje de error
        for call in mock_print.call_args_list:
            if isinstance(call.args[0], str):
                assert "[red] No hay funciones registradas.[/red]" not in call.args[0]

    # ------------------- Pruebas para validaciones de datos -------------------

    def test_validar_hora_valida(self):
        self.assertEqual(funciones.validar_hora("14:30", "Hora"), "14:30")

    def test_validar_hora_formato_invalido(self):
        with self.assertRaises(ValueError):
            funciones.validar_hora("14-30", "Hora")

    def test_validar_hora_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            funciones.validar_hora("25:00", "Hora")

    # ------------------- Pruebas para funciones de UI y cálculo -------------------

    def test_calcular_max_asientos(self):
        # Simular una pantalla de 80x24
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (24, 80)
        max_asientos = funciones.calcular_max_asientos(mock_stdscr)
        # max_columnas = 80 // 6 = 13
        # max_filas = (24 - 4) // 2 = 10
        self.assertEqual(max_asientos, 13 * 10)

    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open", new_callable=mock_open, read_data="ID,Titulo\n1,Pelicula 1\n"
    )
    @patch("funciones.console.print")
    def test_mostrar_tabla_peliculas(self, mock_print, mock_open, mock_exists):
        peliculas = funciones.mostrar_tabla_peliculas()
        self.assertEqual(peliculas, {"1": "Pelicula 1"})
        self.assertTrue(mock_print.called)

    # ------------------- Pruebas para CRUD de funciones -------------------

    @patch("builtins.input", side_effect=["1", "3", "15:00", "50"])
    @patch("funciones.cargar_funciones", return_value=[])
    @patch("funciones.mostrar_tabla_peliculas", return_value={"1": "Pelicula 1"})
    @patch("funciones.guardar_funcion")
    @patch("curses.wrapper", return_value=130)  # Simula max asientos
    def test_crear_funcion(
        self, mock_curses, mock_guardar, mock_mostrar, mock_cargar, mock_input
    ):
        funciones.crear_funcion()
        # Verifica que se llame a guardar_funcion con la nueva función
        mock_guardar.assert_called_once()
        args, _ = mock_guardar.call_args
        nueva_funcion = args[0][0]
        self.assertEqual(nueva_funcion["id_pelicula"], "1")
        self.assertEqual(nueva_funcion["sala"], "3")
        self.assertEqual(nueva_funcion["hora"], "15:00")

    @patch("builtins.input", side_effect=["F1", "Sala 10", "20:00"])
    @patch("funciones.cargar_funciones")
    @patch("funciones.mostrar_tabla_peliculas", return_value={})
    @patch("funciones.ver_funciones")
    @patch("funciones.guardar_funcion")
    def test_editar_funcion(
        self, mock_guardar, mock_ver, mock_mostrar, mock_cargar, mock_input
    ):
        # Configura el mock para que devuelva una copia de los datos de prueba
        mock_cargar.return_value = [f.copy() for f in self.funciones_mock]

        funciones.editar_funcion()

        mock_guardar.assert_called_once()
        args, _ = mock_guardar.call_args
        funciones_actualizadas = args[0]
        self.assertEqual(funciones_actualizadas[0]["sala"], "Sala 10")
        self.assertEqual(funciones_actualizadas[0]["hora"], "20:00")


if __name__ == "_main_":
    unittest.main()
