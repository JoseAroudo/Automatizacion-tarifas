import argparse
import os

import datetime


def mostrar_entrada_archivo():
    parser = argparse.ArgumentParser(description='Procesa un archivo de registros separados por punto y coma.')
    parser.add_argument('archivo', nargs='?', default=None, help='ruta del archivo a procesar')
    
    meses = {
        '01': 'Ene',
        '02': 'Feb',
        '03': 'Mar',
        '04': 'Abr',
        '05': 'May',
        '06': 'Jun',
        '07': 'Jul',
        '08': 'Ago',
        '09': 'Sep',
        '10': 'Oct',
        '11': 'Nov',
        '12': 'Dic'
    }
    
    hoy = datetime.datetime.now()
    mes=hoy.strftime("%m")
    ano=hoy.year
    # In notebooks/interactive sessions, Jupyter adds extra args like --f=kernel.json.
    # We ignore unknown args so the same function works in both CLI and Jupyter.
    args, _ = parser.parse_known_args()

    p = args.archivo
    if not p:
        default_name = f'Tarifas Pub ADD {meses[mes]} {ano}.xlsx'
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