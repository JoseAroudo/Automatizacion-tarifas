from pathlib import Path


def carga_a_excel(df,fecha):
    ruta_salida = Path(__file__).resolve().parent.parent / f"sap_tarifas_mme_{fecha}.txt"
    df.to_csv(ruta_salida, sep="|", index=False, header=False)