def consolidacion_df_final(df, df_final, columna):
    filas = 0
    for combo in df.columns:
        for i in range(len(df)):
            df_final.iloc[filas, columna] = round(float(df.at[i, combo]), 7)
            filas += 1