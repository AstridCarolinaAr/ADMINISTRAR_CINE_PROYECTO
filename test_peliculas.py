import unittest
from unittest.mock import patch, mock_open
import peliculas  # importa tu archivo principal en minúsculas


class TestPeliculas(unittest.TestCase):

    # --- Prueba de inicialización del archivo CSV ---
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_inicializar_csv_crea_archivo(self, mock_file, mock_exists):
        peliculas.inicializar_csv()
        mock_file.assert_called_once_with('peliculas.csv', mode='w', newline='', encoding='utf-8')

    # --- Prueba de agregar película ---
    @patch("builtins.input", side_effect=["1", "Matrix", "Acción", "120"])
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="ID,Titulo,Genero,Duracion_min\n")
    @patch("peliculas.pausar")
    def test_agregar_pelicula(self, mock_pausar, mock_file, mock_exists, mock_input):
        peliculas.agregar_pelicula()
        handle = mock_file()
        # Verificar que se haya escrito la línea con la película
        handle.write.assert_any_call("1,Matrix,Acción,120\r\n")

    # --- Prueba de listar películas ---
    @patch("builtins.open", new_callable=mock_open, read_data="ID,Titulo,Genero,Duracion_min\n1,Matrix,Acción,120\n")
    @patch("peliculas.pausar")
    @patch("os.path.exists", return_value=True)
    def test_listar_peliculas(self, mock_exists, mock_pausar, mock_file):
        peliculas.listar_peliculas()
        mock_file.assert_called_once_with('peliculas.csv', mode='r', newline='', encoding='utf-8')

    # --- Prueba de actualizar película ---
    @patch("builtins.input", side_effect=["1", "Matrix Reloaded", "Ciencia Ficción", "150"])
    @patch("builtins.open", new_callable=mock_open, read_data="ID,Titulo,Genero,Duracion_min\n1,Matrix,Acción,120\n")
    @patch("peliculas.pausar")
    def test_actualizar_pelicula(self, mock_pausar, mock_file, mock_input):
        peliculas.actualizar_pelicula()
        handle = mock_file()
        # Comprobar que se reescribió con los datos nuevos
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Matrix Reloaded", written)
        self.assertIn("Ciencia Ficción", written)

    # --- Prueba de eliminar película ---
    @patch("builtins.input", side_effect=["1"])
    @patch("builtins.open", new_callable=mock_open, read_data="ID,Titulo,Genero,Duracion_min\n1,Matrix,Acción,120\n")
    @patch("peliculas.pausar")
    def test_eliminar_pelicula(self, mock_pausar, mock_file, mock_input):
        peliculas.eliminar_pelicula()
        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        # Debe contener solo los encabezados, sin la película eliminada
        self.assertIn("ID,Titulo,Genero,Duracion_min", written)
        self.assertNotIn("Matrix", written)


if __name__ == "__main__":
    unittest.main()
