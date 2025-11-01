@echo off
setlocal

:: Get desktop path
set "desktop=%USERPROFILE%\Desktop"

:: Create HW-Bot folder
set "target=%desktop%\HW-Bot"
if not exist "%target%" (
    mkdir "%target%"
)

:: Download file using bitsadmin
set "url=https://drive.usercontent.google.com/download?id=1_93JJzFZwfzV9CHMUoyT8w8Zmu1pt8wS&export=download&authuser=0&confirm=t&uuid=e360caef-cd1f-4928-be9b-c4d0c12864c0&at=AKSUxGPc61h9CTRjXkVGq8e6BfmB%3A1761990717017"
set "outfile=%target%\downloaded_file"

bitsadmin /transfer "HWBotDownload" "%url%" "%outfile%" >nul 2>&1

:: Confirm success
echo Download complete. File saved to HW-Bot.
timeout /t 2 >nul

endlocal
exit
