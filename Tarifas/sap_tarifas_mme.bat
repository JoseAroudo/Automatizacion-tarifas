
@color 0A

@title SAP_TARIFAS_MME.BAT
@echo SAP_TARIFAS_MME.BAT
@echo ----------------------------------
@echo Duracion aprox: Algunos segundos
@echo ----------------------------------

@echo Ejecutando proceso Python previo...
@pushd "%~dp0\.."
@"%CD%\envTarifa\Scripts\python.exe" "%CD%\Main.py"
@if errorlevel 1 (
	@echo Error: Main.py fallo. Se cancela la carga.
	@popd
	@pause
	@exit /b 1
)
@popd
@echo Proceso Python completado.

@set /p usuario="Ingrese usuario INFOREG: "
@set /p contra="Ingrese contrasena INFOREG: "
@set conexion=AWS_INFOREG_PRO.WORLD

@dir SAP_TARIFAS_MME*.txt
@set /p archivo="Archivo para cargar tarifas "

@cls

@color 0b

@sqlldr %USUARIO%@%conexion%/%contra% control=SAP_TARIFAS_MME.ctl data='%archivo%' log=SAP_TARIFAS_MME.log bad=SAP_TARIFAS_MME.bad errors=10  rows = 5000

@color 0a


@echo .....
@pause

type SAP_TARIFAS_MME.log

@echo .....
@pause

quit