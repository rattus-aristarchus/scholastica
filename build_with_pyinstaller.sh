python -m PyInstaller --name scholastica --clean --onefile --add-data "*.yml:." --collect-data gui --log-level WARN src/__init__.py
