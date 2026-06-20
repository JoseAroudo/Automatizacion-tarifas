import pandas as pd

from consolidacion_df import consolidacion_df_final

def transformar_datos(NombreArchivo, hoy):
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



    df_tarifa= df.iloc[::2, 0:4].copy().reset_index(drop=True)#.tolist()

    df_cu= df.iloc[1::2, :4].copy().reset_index(drop=True)#.tolist()

    df_factor = 1-(df_tarifa.divide(df_cu)).round(7)




    df_final = pd.DataFrame({
        "mes": [hoy.strftime("%m")]*12,
        "ano": [hoy.year]*12,
        "estrato": [(x % 3) + 1 for x in range(12)],
        "combo": [x for x in range(1, 5) for y in range(1, 4)],
        "CU": [0.0]*12,
        "TA": [0.0]*12,
        "Factor": [0.0]*12
    })


    consolidacion_df_final(df_cu,df_final,4)
    consolidacion_df_final(df_tarifa,df_final,5)
    consolidacion_df_final(df_factor,df_final,6)

    
    
    return df_final