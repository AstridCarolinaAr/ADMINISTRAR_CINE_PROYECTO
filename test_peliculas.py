import unittest
from unittest.mock import mock_open, patch

import Peliculas  # importa tu archivo principal en minúsculas


class TestPeliculas(unittest.TestCase):
    # --- Prueba de inicialización del archivo CSV ---
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_inicializar_csv_crea_archivo(self, mock_file, mock_exists):
        Peliculas.inicializar_csv()
        mock_file.assert_called_once_with(
            "peliculas.csv", mode="w", newline="", encoding="utf-8"
        )

    # --- Prueba de agregar película ---
    @patch("builtins.input", side_effect=["Matrix", "Acción", "120"])
    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo,Genero,Duracion_min\n",
    )
    @patch("Peliculas.pausar")
    def test_agregar_pelicula(self, mock_pausar, mock_file, mock_exists, mock_input):
        Peliculas.agregar_pelicula()
        handle = mock_file()
        # Verificar que se haya escrito la línea con la película
        handle.write.assert_any_call("1,Matrix,Acción,120\r\n")

    # --- Prueba de listar películas ---
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo,Genero,Duracion_min\n1,Matrix,Acción,120\n",
    )
    @patch("Peliculas.pausar")
    @patch("os.path.exists", return_value=True)
    def test_listar_peliculas(self, mock_exists, mock_pausar, mock_file):
        Peliculas.listar_peliculas()
        mock_file.assert_called_once_with(
            "peliculas.csv", mode="r", newline="", encoding="utf-8"
        )

    # --- Prueba de actualizar película ---
    @patch(
        "builtins.input", side_effect=["1", "Matrix Reloaded", "Ciencia Ficción", "150"]
    )
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo,Genero,Duracion_min\n1,Matrix,Acción,120\n",
    )
    @patch("Peliculas.pausar")
    def test_actualizar_pelicula(self, mock_pausar, mock_file, mock_input):
        Peliculas.actualizar_pelicula()
        handle = mock_file()
        # Comprobar que se reescribió con los datos nuevos
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Matrix Reloaded", written)
        self.assertIn("Ciencia Ficción", written)

    # --- Prueba de eliminar película ---
    @patch("builtins.input", side_effect=["1"])
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo,Genero,Duracion_min\n1,Matrix,Acción,120\n",
    )
    @patch("Peliculas.pausar")
    def test_eliminar_pelicula(self, mock_pausar, mock_file, mock_input):
        Peliculas.eliminar_pelicula()
        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        # Debe contener solo los encabezados, sin la película eliminada
        self.assertIn("ID,Titulo,Genero,Duracion_min", written)
        self.assertNotIn("Matrix", written)

    # --- Pruebas para las funciones de validación ---
    def test_validar_texto_valido(self):
        self.assertEqual(Peliculas.validar_texto("Dune 2", "Título"), "Dune 2")

    def test_validar_texto_vacio(self):
        with self.assertRaises(ValueError):
            Peliculas.validar_texto(" ", "Título")

    def test_validar_texto_muy_largo(self):
        with self.assertRaises(ValueError):
            Peliculas.validar_texto("a" * 121, "Título")

    def test_validar_texto_caracteres_invalidos(self):
        with self.assertRaises(ValueError):
            Peliculas.validar_texto("Título con @", "Título")

    def test_validar_duracion_valida(self):
        self.assertEqual(Peliculas.validar_duracion("120", "Duración"), 120)

    def test_validar_duracion_no_numerica(self):
        with self.assertRaises(ValueError):
            Peliculas.validar_duracion("abc", "Duración")

    def test_validar_duracion_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            Peliculas.validar_duracion("700", "Duración")

    # --- Pruebas para funciones de CSV ---
    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo,Genero,Duracion_min\n",
    )
    def test_verificar_encabezados_csv_validos(self, mock_open, mock_exists):
        is_valid, error = Peliculas.verificar_encabezados_csv(
            "peliculas.csv", ["ID", "Titulo", "Genero", "Duracion_min"]
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Nombre,Categoria,Tiempo\n",
    )
    def test_verificar_encabezados_csv_invalidos(self, mock_open, mock_exists):
        is_valid, error = Peliculas.verificar_encabezados_csv(
            "peliculas.csv", ["ID", "Titulo", "Genero", "Duracion_min"]
        )
        self.assertFalse(is_valid)
        self.assertIn("Encabezados inesperados", error)

    @patch("os.path.exists", return_value=False)
    def test_verificar_encabezados_csv_no_existe(self, mock_exists):
        is_valid, error = Peliculas.verificar_encabezados_csv(
            "peliculas.csv", ["ID", "Titulo", "Genero", "Duracion_min"]
        )
        self.assertFalse(is_valid)
        self.assertIn("no existe", error)

    @patch("os.replace")
    @patch("builtins.open", new_callable=mock_open)
    def test_safe_write_csv(self, mock_open, mock_replace):
        fieldnames = ["ID", "Titulo"]
        rows = [{"ID": "1", "Titulo": "Test"}]
        Peliculas.safe_write_csv("test.csv", fieldnames, rows)

        mock_open.assert_called_once_with(
            "test.csv.tmp", "w", encoding="utf-8", newline=""
        )
        handle = mock_open()
        handle.write.assert_any_call("ID,Titulo\r\n")
        handle.write.assert_any_call("1,Test\r\n")
        mock_replace.assert_called_once_with("test.csv.tmp", "test.csv")

    # --- Pruebas para funciones de carga y búsqueda ---
    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo\n1,Inception\n2,Interstellar\n",
    )
    def test_cargar_peliculas_dict(self, mock_open, mock_exists):
        peliculas = Peliculas.cargar_peliculas_dict()
        self.assertEqual(len(peliculas), 2)
        self.assertEqual(peliculas["1"], "Inception")
        self.assertEqual(peliculas["2"], "Interstellar")

    @patch("builtins.input", side_effect=["Ciencia Ficción"])
    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="ID,Titulo,Genero,Duracion_min\n1,Inception,Ciencia Ficción,148\n2,The Matrix,Ciencia Ficción,136\n3,Drama,Drama,120\n",
    )
    @patch("Peliculas.pausar")
    def test_buscar_peliculas_por_genero(
        self, mock_pausar, mock_open, mock_exists, mock_input
    ):
        with patch("Peliculas.console.print") as mock_print:
            Peliculas.buscar_peliculas_por_genero()

            # Esta es una aserción débil, pero confirma que se intentó imprimir algo.
            # Una mejor prueba requeriría capturar la salida de la tabla Rich.
            self.assertTrue(mock_print.called)


if __name__ == "__main__":
    unittest.main()
