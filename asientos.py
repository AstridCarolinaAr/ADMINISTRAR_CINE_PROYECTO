import json
import math


def serializar_asientos(mapa: dict) -> str:
    """Convierte el mapa de asientos en un string JSON para guardar en CSV."""
    return json.dumps(mapa, ensure_ascii=False)


def deserializar_asientos(s: str) -> dict:
    """Convierte el string JSON de vuelta a dict. Devuelve {} si hay error."""
    try:
        return json.loads(s) if s else {}
    except Exception:
        return {}


def crear_mapa_asientos(total_asientos):
    """
    Crea un mapa de asientos lo más cuadrado posible.
    Busca la combinación de filas y columnas que se acerque a un cuadrado.
    """

    mejor_cols = 1
    mejor_filas = total_asientos
    mejor_diff = total_asientos

    # Probar columnas desde 1 hasta total_asientos
    for cols in range(1, total_asientos + 1):
        filas = math.ceil(total_asientos / cols)
        if filas * cols < total_asientos:
            continue
        diff = abs(filas - cols)
        # Elegir la combinación más cuadrada
        if diff < mejor_diff:
            mejor_diff = diff
            mejor_cols = cols
            mejor_filas = filas

    # Generar etiquetas de columnas (A, B, ..., Z, AA, AB, ...)
    def generar_columnas(n):
        cols = []
        i = 0
        while len(cols) < n:
            col = ""
            j = i
            while True:
                col = chr(ord("A") + (j % 26)) + col
                j = j // 26 - 1
                if j < 0:
                    break
            cols.append(col)
            i += 1
        return cols

    columnas = generar_columnas(mejor_cols)

    # Construir mapa
    mapa = {}
    asiento_num = 0
    for fila in range(1, mejor_filas + 1):
        for col in columnas:
            asiento_num += 1
            if asiento_num > total_asientos:
                break
            mapa[f"{col}{fila}"] = "libre"

    return mapa
