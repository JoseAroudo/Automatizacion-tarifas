# Automatización de Tarifas

Proyecto en Python para leer un archivo Excel de tarifas, transformar sus datos y generar un archivo plano para la carga en INFOREG con separador `|`.

## Qué hace

- Toma un archivo `.xlsx` de tarifas.
- Procesa y organiza los datos.
- Genera un `.txt` con el formato requerido para `sqlldr`.
- Ejecuta la carga final desde el archivo `.bat`.

## Requisitos

- Python 3.13 o superior.
- Instalar estas librerías en la PC donde se ejecute el proyecto:
	- `pandas`
	- `openpyxl`

## Instalación de librerías

Si la persona no tiene las librerías instaladas, debe abrir una terminal en la carpeta del proyecto y ejecutar:

```powershell
python -m pip install pandas openpyxl
```


## Estructura principal

- `sap_tarifas_mme.bat`: lanza el proceso Python y luego ejecuta `sqlldr`.
- `Tarifas/Main.py`: orquesta la lectura, transformación y exportación.
- `Tarifas/Acceder.py`: pide o valida la ruta del archivo Excel.
- `Tarifas/Transformacion.py`: transforma los datos del Excel.
- `Tarifas/consolidacion_df.py`: apoya la consolidación del `DataFrame` final.
- `Tarifas/carga_df_final.py`: exporta el resultado a un archivo `.txt`.

## Ejecución

### Opción automática en Windows

Doble clic sobre `sap_tarifas_mme.bat` desde la raíz del proyecto.



## Entrada y salida

- Entrada: archivo Excel `.xlsx` con la hoja `Tarifas Pub ADD`.
- Salida: archivo `sap_tarifas_mme_<YYYYMM>.txt` con separador `|`.

## Flujo general

1. El usuario selecciona o escribe la ruta del Excel.
2. Python transforma la información.
3. Se genera el TXT final.
4. El `.bat` solicita credenciales y ejecuta `sqlldr`.

## Nota

Si aparece un error de lectura del Excel, normalmente falta instalar `pandas` u `openpyxl` en la máquina donde se está ejecutando el proyecto.