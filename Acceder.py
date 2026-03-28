import argparse
import os


def mostrar_entrada_archivo():
    parser = argparse.ArgumentParser(description='Procesa un archivo de registros separados por punto y coma.')
    parser.add_argument('archivo', nargs='?', default=None, help='ruta del archivo a procesar')
    args = parser.parse_args()

    p = args.archivo
    if not p:
        default_name = 'Tarifas Pub ADD Mar 2026.xlsx'
        entrada = input(f"Ingrese ruta del archivo (ENTER para usar '{default_name}'): ").strip()
        p = entrada or default_name

    if not os.path.isabs(p):
        p = os.path.join(os.path.dirname(__file__), p)

    while not os.path.exists(p):
        entrada = input(f"\n\n\n\nArchivo no encontrado: {p}\nIngrese otra ruta o 'q' para salir: ").strip()
        if entrada.lower() in ('q', 'quit', 'exit'):
            print('Abortando.')
            raise SystemExit(1)
        if not os.path.isabs(entrada):
            entrada = os.path.join(os.path.dirname(__file__), entrada)
        p = entrada

    return p