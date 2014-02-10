:: SimViz Post Install Script
echo off
:: Create the devdata.db database
FOR /F "skip=2 tokens=2,*" %%A IN ('%SystemRoot%\SysWoW64\REG.exe query "HKLM\software\META" /v "META_PATH"') DO "%%B\bin\Python27\Scripts\Paster.exe" setup-app development.ini

FOR /F "skip=2 tokens=2,*" %%A IN ('%SystemRoot%\SysWoW64\REG.exe query "HKLM\software\META" /v "META_PATH"') DO "%%B\bin\Python27\Scripts\Paster.exe" serve development.ini

:: Goto http://127.0.0.1:8585/simviz/dashboard.html
