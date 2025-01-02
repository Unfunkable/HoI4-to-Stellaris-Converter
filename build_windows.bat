@echo off
rmdir /s /q dist\windows
python -m PyInstaller --onefile --console --add-binary "ImageMagick\magick.exe;." Converter.py --name HoI4ToStellaris --distpath "dist\windows"
xcopy /E /I "files" "dist\windows\files"
xcopy /E /I "outputMod_base" "dist\windows\outputMod_base"
copy "configuration.txt" "dist\windows\"
mkdir "dist\windows\output"
move "dist\windows\files\outputMod.mod" "dist\windows\output\"
