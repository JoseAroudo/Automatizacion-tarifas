# Auditoría del proyecto — Automatización de Tarifas

**Fecha:** 2026-06-19
**Alcance:** `Tarifas/*.py`, `sap_tarifas_mmeV2.bat`, `sap_tarifas_mme.ctl`, `README.md`
**Estado:** revisión sin modificar el código fuente. Cada hallazgo incluye la corrección sugerida.

---

## Resumen ejecutivo

El proyecto es un ETL pequeño y funcional, pero su corrección depende de varios **supuestos implícitos** sobre la forma exacta del Excel de entrada (número de filas, posición de las filas vacías, ausencia de ceros). Si el archivo cambia ligeramente, el proceso puede romperse con un `IndexError`, generar valores `inf`/`NaN` silenciosos o desalinear los datos sin avisar. Hay además un **bug real en el `.bat`** (`rows = 5000`) y varias inconsistencias de nombres entre archivos.

| Severidad | Cantidad | Temas |
|-----------|----------|-------|
| 🔴 Alta   | 4 | `rows = 5000` en sqlldr, dependencia frágil de filas, división por cero, sin manejo de errores |
| 🟠 Media  | 5 | índices/números mágicos, `combo 2` duplicado, inconsistencia de nombres de archivos, sin enmascarar contraseña, descripción engañosa del CLI |
| 🟢 Baja   | 6 | estilo, comentarios de desarrollo, portabilidad, claridad |

---

## 🔴 Hallazgos de severidad alta

### A1. Bug en `sqlldr`: `rows = 5000` con espacios
**Archivo:** `sap_tarifas_mmeV2.bat:50`

```bat
@sqlldr ... errors=10  rows = 5000
```

`sqlldr` espera los parámetros sin espacios alrededor del `=`. Con `rows = 5000` el ejecutable interpreta `rows`, `=` y `5000` como tres tokens separados y aborta con error de parámetro (`SP2-...` / `LRM-00112`).

**Corrección:**
```bat
@sqlldr ... errors=10 rows=5000
```

---

### A2. La consolidación depende de que queden exactamente 6 filas útiles (3 por bloque)
**Archivos:** `Transformacion.py:26-32`, `consolidacion_df.py`

`consolidacion_df_final` recorre `4 columnas × len(df)` y escribe en `df_final` (que tiene **12 filas fijas**):

```python
for combo in df.columns:          # 4 columnas
    for i in range(len(df)):      # len(df) filas
        df_final.iloc[filas, columna] = ...
        filas += 1
```

Esto solo cuadra si `len(df) == 3` (4×3 = 12). Pero `df_tarifa`/`df_cu` salen de:

```python
df = df.dropna(how="all")     # elimina filas vacías ANTES del split
df_tarifa = df.iloc[::2, 0:4] # filas pares
df_cu     = df.iloc[1::2, :4] # filas impares
```

Riesgos concretos:
- Si quedan **8 filas útiles** (ninguna vacía), `df_tarifa`/`df_cu` tendrán 4 filas → `filas` llega a 15 y `df_final.iloc[12, ...]` lanza **`IndexError`**.
- `dropna(how="all")` se aplica **antes** del split par/impar. Si una fila vacía está intercalada, desplaza la alternancia y **empareja mal** tarifa↔CU sin ningún error visible (datos incorrectos cargados a producción).

**Corrección sugerida:** hacer explícita la relación combo↔estrato y validar tamaños en vez de confiar en el patrón de filas vacías:

```python
N_ESTRATOS = 3
N_COMBOS = 4
assert len(df_cu) == N_ESTRATOS, f"Se esperaban {N_ESTRATOS} filas de CU, hay {len(df_cu)}"
assert len(df_tarifa) == len(df_cu), "Tarifa y CU desalineadas"
```

Y en `consolidacion_df.py`, validar que las dimensiones cuadran:

```python
def consolidacion_df_final(df, df_final, columna):
    valores = [round(float(df.at[i, c]), 7) for c in df.columns for i in range(len(df))]
    if len(valores) != len(df_final):
        raise ValueError(f"{len(valores)} valores para {len(df_final)} filas destino")
    df_final.iloc[:, columna] = valores
```

---

### A3. División por cero silenciosa en el factor
**Archivo:** `Transformacion.py:34`

```python
df_factor = 1-(df_tarifa.divide(df_cu)).round(7)
```

Si algún `CU` es `0` (o `NaN`), el resultado es `inf`/`-inf`/`NaN`. Pandas no lanza error: ese valor se escribe en `df_final` y se carga al archivo `.txt`. En `sqlldr` un `inf`/`nan` provocará registros en `.bad` o un factor inválido.

**Corrección:** validar antes de dividir y decidir el comportamiento (abortar o rellenar):

```python
if (df_cu == 0).any().any():
    raise ValueError("Hay valores CU = 0; no se puede calcular el factor")
df_factor = (1 - df_tarifa.divide(df_cu)).round(7)
```

---

### A4. Sin manejo de errores en la lectura/transformación
**Archivos:** `Main.py`, `Transformacion.py:7-13`

El README dice "Si aparece un error de lectura del Excel...", pero el código no captura nada. Si falta la hoja `Tarifas Pub ADD`, falta `openpyxl`, o el rango `D:F`/`skiprows=6` no coincide, el traceback de Python aparece crudo y el `.bat` solo muestra "Main.py fallo".

**Corrección:** envolver en `try/except` con mensajes claros y código de salida controlado, p. ej.:

```python
try:
    df = pd.read_excel(NombreArchivo, sheet_name="Tarifas Pub ADD", usecols="D:F", skiprows=6, nrows=8)
except ValueError as e:
    raise SystemExit(f"No se pudo leer la hoja 'Tarifas Pub ADD': {e}")
except ImportError:
    raise SystemExit("Falta 'openpyxl'. Ejecute: python -m pip install openpyxl")
```

---

## 🟠 Hallazgos de severidad media

### M1. Números e índices mágicos sin documentar
**Archivo:** `Transformacion.py:7-13, 30-52`; `consolidacion_df.py`

`usecols="D:F"`, `skiprows=6`, `nrows=8`, los índices de columna `4/5/6` y los `*12` están dispersos y sin constantes. Los comentarios `# ajusta` y `# si hay encabezados raros` son notas de desarrollo que delatan que estos valores son frágiles.

**Corrección:** extraer constantes al inicio del módulo (`SHEET`, `USECOLS`, `SKIPROWS`, `NROWS`, `COL_CU=4`, `COL_TA=5`, `COL_FACTOR=6`) y eliminar los comentarios provisionales.

---

### M2. `combo 2` es una copia exacta de `combo 1`
**Archivo:** `Transformacion.py:15-22`

```python
df["nombre"] = df.iloc[:, 0].copy()   # copia de la columna D
...
columnas_iniciales = ["combo 1", "combo 4", "combo 3", "combo 2"]
df.columns = columnas_iniciales
df = df[["combo 1", "combo 2", "combo 3", "combo 4"]]
```

El Excel aporta 3 columnas (D, E, F) y se fabrica una cuarta duplicando la D. El resultado es que **`combo 1` y `combo 2` contienen datos idénticos**. Si esto es intencional (el combo 2 comparte tarifa con el 1) conviene documentarlo; si no, es un error de datos. La asignación de nombres en orden D, E, F, copia como `1,4,3,2` es muy difícil de seguir.

**Acción:** confirmar con negocio si `combo 1 == combo 2` es correcto y dejarlo comentado explícitamente.

---

### M3. Inconsistencias de nombres entre archivos
**Archivos:** varios

- README menciona `sap_tarifas_mme.bat`, pero el archivo real es `sap_tarifas_mmeV2.bat`.
- Python genera `sap_tarifas_mme_<YYYYMM>.txt` (minúsculas); el `.bat` busca `SAP_TARIFAS_MME*.txt` (mayúsculas).
- El control es `sap_tarifas_mme.ctl`; el `.bat` referencia `SAP_TARIFAS_MME.ctl`.

En Windows el sistema de archivos no distingue mayúsculas, por lo que hoy "funciona", pero es frágil (rompería en cualquier ruta sensible a mayúsculas y confunde al mantenedor). **Acción:** unificar el nombre exacto en README, `.bat`, `.ctl` y el generador del `.txt`.

---

### M4. Contraseña visible al escribirla
**Archivo:** `sap_tarifas_mmeV2.bat:38-39`

```bat
@set /p contra="Ingrese contrasena INFOREG: "
```

`set /p` muestra la contraseña en pantalla mientras se teclea y queda en el buffer de la consola. Para un usuario de producción es un riesgo de exposición de credenciales.

**Mitigación:** usar un prompt enmascarado (PowerShell `Read-Host -AsSecureString`, o `runas`, o un wrapper). Como mínimo, hacer `@cls` inmediatamente después de capturarla.

---

### M5. Descripción del CLI engañosa
**Archivo:** `Acceder.py:8`

```python
parser = argparse.ArgumentParser(description='Procesa un archivo de registros separados por punto y coma.')
```

La entrada real es un Excel `.xlsx`, no un archivo separado por `;`. La ayuda induce a error. **Corrección:** ajustar el texto a "Procesa un archivo Excel de tarifas (.xlsx)".

---

## 🟢 Hallazgos de severidad baja / optimizaciones

- **B1. `Transformacion.py:34`** — `1-(df_tarifa.divide(df_cu)).round(7)`: se redondea el cociente y luego se resta de 1; el redondeo final efectivo queda en 7 decimales igual, pero es más claro `(1 - df_tarifa.divide(df_cu)).round(7)`.
- **B2. `Transformacion.py:30,32`** — estilos inconsistentes `0:4` vs `:4` para el mismo recorte. Unificar.
- **B3. `consolidacion_df.py`** — la función muta `df_final` in-place y no retorna nada; el patrón funciona pero es implícito. Mejor construir y asignar la columna completa (ver A2), más rápido y legible.
- **B4. `Main.py:9`** — `os.system("cls")` es solo Windows. Como el flujo es vía `.bat` está bien, pero impide pruebas locales en Linux/Mac. Envolver en `if os.name == "nt"`.
- **B5. `Transformacion.py:15`** — la columna intermedia `"nombre"` es un nombre temporal confuso; el comentario explica la intención pero el código se beneficiaría de nombres claros.
- **B6. Sin `requirements.txt`** — las dependencias (`pandas`, `openpyxl`) solo están en el README. Añadir `requirements.txt` facilita la instalación reproducible (`pip install -r requirements.txt`).

---

## Observaciones generales

1. **Validar la entrada, no asumir su forma.** El núcleo del riesgo (A2, A3) es que el código confía en que el Excel tenga exactamente la estructura esperada. Añadir 3-4 `assert`/validaciones con mensajes claros convierte fallos silenciosos en errores entendibles.
2. **Nombres positionales frágiles.** `df_final` se llena por posición (`iloc[fila, columna]`). Mientras `.ctl` y `df_final` mantengan el mismo orden de columnas funciona, pero cualquier reordenamiento rompe la carga sin aviso. Documentar el contrato de columnas (`mes, ano, sectusu/estrato, combo, CU, TA, Factor`).
3. **No hay pruebas.** Un único test con un Excel de muestra (o un DataFrame simulado) cubriría A2/A3 y daría red de seguridad para futuros cambios.
4. **Sin `.gitignore`.** Los artefactos generados (`*.txt`, `*.log`, `*.bad`, `__pycache__/`) deberían ignorarse para no ensuciar el repo.

---

## Prioridad de corrección sugerida

1. A1 (`rows=5000`) — corrección trivial, bloquea la carga.
2. A3 + A2 — evitan datos incorrectos o crash en producción.
3. A4 — mejora drástica de diagnóstico ante errores.
4. M1–M5 — robustez y mantenibilidad.
5. B1–B6 — limpieza y reproducibilidad.
