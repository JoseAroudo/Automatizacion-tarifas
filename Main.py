import datetime

from Acceder import mostrar_entrada_archivo
from Tranformacion import transformar_datos
from carga_df_final import carga_a_excel

import os

os.system("cls")
hoy = datetime.datetime.now()

NombreArchivo= mostrar_entrada_archivo()

df_con_datos_finales=transformar_datos(NombreArchivo, hoy)

carga_a_excel(df_con_datos_finales, hoy.strftime("%Y%m"))