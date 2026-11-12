@echo off
REM Regenera los eventos de FDI-Z. Cerrar GDevelop antes. Correr desde cualquier lugar.
cd /d "%~dp0\..\.."
set STAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set STAMP=%STAMP: =0%
if not exist gdevelop\respaldos mkdir gdevelop\respaldos
copy gdevelop\FDI-Z\FDI-Z.json gdevelop\respaldos\FDI-Z_respaldo_%STAMP%.json >nul
python gdevelop\scripts\fase5_jugadores.py gdevelop\FDI-Z\FDI-Z.json generado\sprites\atlas.json mapa\final\mapa_fdiz_datos.json gdevelop\scripts\Gamepads.json || goto error
python gdevelop\scripts\fases_6_a_11.py gdevelop\FDI-Z\FDI-Z.json mapa\final\mapa_fdiz_datos.json || goto error
python gdevelop\scripts\fase12_mejoras.py gdevelop\FDI-Z\FDI-Z.json mapa\final\mapa_fdiz_datos.json mapa\final\mapa_fdiz_props.json || goto error
echo Listo. Respaldo en gdevelop\respaldos\FDI-Z_respaldo_%STAMP%.json
pause
exit /b 0
:error
echo Hubo un error: el respaldo esta en gdevelop\respaldos\FDI-Z_respaldo_%STAMP%.json
pause
