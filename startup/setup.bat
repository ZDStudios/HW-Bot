@echo off
setlocal

:: Define paths
set "desktop=%USERPROFILE%\Desktop"
set "target=%desktop%\HW-Bot"
set "outfile=%target%\downloaded_file"

:: Create folder if it doesn't exist
if not exist "%target%" (
    mkdir "%target%"
)

:: Use PowerShell to download the file
powershell -Command "Invoke-WebRequest -Uri 'https://drive.usercontent.google.com/download?id=1_93JJzFZwfzV9CHMUoyT8w8Zmu1pt8wS&export=download&authuser=0&confirm=t&uuid=e360caef-cd1f-4928-be9b-c4d0c12864c0&at=AKSUxGPc61h9CTRjXkVGq8e6BfmB%3A1761990717017' -OutFile '%outfile%'"

:: Confirm success
echo Download complete. File saved to HW-Bot.
timeout /t 2 >nul

endlocal
exit
