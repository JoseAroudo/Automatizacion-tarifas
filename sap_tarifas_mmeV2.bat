
@color 0A

@title SAP_TARIFAS_MME.BAT
@echo SAP_TARIFAS_MME.BAT
@echo ----------------------------------
@echo Duracion aprox: 5 segundos
@echo ----------------------------------

@echo Ejecutando proceso Python previo...
set "PROJDIR=%~dp0Tarifas"
pushd "%PROJDIR%"

where py >nul 2>nul
if not errorlevel 1 (
	py -3 "%PROJDIR%\Main.py"
) else (
	where python >nul 2>nul
	if not errorlevel 1 (
		python "%PROJDIR%\Main.py"
	) else (
		echo Error: No se encontro Python en el sistema.
		popd
		pause
		exit /b 1
	)
)

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

@dir "%~dp0SAP_TARIFAS_MME*.txt"
@set /p archivo="Archivo para cargar tarifas (en la carpeta raiz): "
@set "archivo=%~dp0%archivo%"

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