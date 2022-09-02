# for linux:
python -m PyInstaller --name scholastica --clean --add-data "*.yml:." --collect-data gui --log-level WARN src/__init__.py
# for Windows:
python -m PyInstaller --name scholastica --clean --log-level WARN --noconfirm --paths=C:\Users\User\Documents\GitHub\scholastica\src --add-data "*.yml;." --collect-data gui src\__init__.py