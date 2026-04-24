def carga_a_excel(df,fecha):
    df.to_csv(f"Tarifas/sap_tarifas_mme_{fecha}.txt", sep="|", index=False, header=False)