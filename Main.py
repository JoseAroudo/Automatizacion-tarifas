import pandas as pd
from Acceder import mostrar_entrada_archivo


NombreArchivo= mostrar_entrada_archivo()

# Lee solo las columnas que necesitas (por letra o nombre)
df = pd.read_excel(
    NombreArchivo,
    sheet_name="Tarifas Pub ADD",
    usecols="D:F",          # ajusta
    skiprows=6              # si hay encabezados raros
)

df["combo 1"] = df["Unnamed: 3"].copy()

columnas = ["combo 2", "combo 3", "combo 4", "combo 1"]

df.columns = columnas
df = df[["combo 1", "combo 2", "combo 3", "combo 4"]]
#df = df.dropna(how="all")
df
print(df)