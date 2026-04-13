import datetime

import pandas as pd
from Acceder import mostrar_entrada_archivo

import os

os.system("cls")

NombreArchivo= mostrar_entrada_archivo()
# Fecha actual
hoy = datetime.datetime.now()

    
# Lee solo las columnas que necesitas (por letra o nombre)
df = pd.read_excel(
    NombreArchivo,
    sheet_name="Tarifas Pub ADD",
    usecols="D:F",          # ajusta
    skiprows=6,             # si hay encabezados raros
    nrows=8
)

df["nombre"] = df.iloc[:, 0].copy()#Copio columna de combo 1 para hacerla combo 2



#####ESTOS NOMBRES DE COLUMNAS SON TEMPORALES, SOLO PARA PODER MANEJAR LOS DATOS, LUEGO SE BORRAN###############
columnas_iniciales = ["combo 1", "combo 4", "combo 3", "combo 2"]
df.columns = columnas_iniciales
df = df[["combo 1", "combo 2", "combo 3", "combo 4"]]
################################################################################################################


df = df.dropna(how="all")
#print(f"{df}")



df_tarifa= df.iloc[::2, 0:4].copy().reset_index(drop=True)#.tolist()
#print(df_tarifa)

df_cu= df.iloc[1::2, :4].copy().reset_index(drop=True)#.tolist()
#print(f"CU:\n {df_cu}")

df_factor = 1-(df_tarifa.divide(df_cu)).round(7)
#print(f"\nFACTOR:\n {df_factor}")



df_final = pd.DataFrame({
    "mes": [hoy.strftime("%m")]*12,
    "ano": [hoy.year]*12,
    "estrato": [(x % 3) + 1 for x in range(12)],
    "combo": [x for x in range(1, 5) for y in range(1, 4)],
    "CU": [0.0]*12,
    "TA": [0.0]*12,
    "Factor": [0.0]*12
})




filas = 0

for combo in df_cu.columns:
    for i in range(len(df_cu)):
        df_final.iloc[filas, 4] = float(df_cu.at[i, combo])
        filas += 1
        
        
        
filas = 0

for combo in df_tarifa.columns:
    for i in range(len(df_tarifa)):
        df_final.iloc[filas, 5] = float(df_tarifa.at[i, combo])
        filas += 1

filas = 0

for combo in df_factor.columns:
    for i in range(len(df_factor)):
        df_final.iloc[filas, 6] = float(df_factor.at[i, combo])
        filas += 1

        
        
print(df_final)