rm -rf dist/linux
python3 -m PyInstaller --onefile --console --add-binary "ImageMagick/magick:." Converter.py --name HoI4ToStellaris --distpath "dist/linux"
cp -r "files" "dist/linux/files"
cp -r "outputMod_base" "dist/linux/outputMod_base"
cp "configuration.txt" "dist/linux/"
mkdir -p "dist/linux/output"