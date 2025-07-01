# build_all.ps1
# Limpa dist, build antigos
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# Compila o Launcher
pyinstaller Launcher.spec

# Compila o Nuvem.Test.exe (pode ajustar para --onefile se desejar)
pyinstaller Nuvem.spec

Write-Host "Build finalizada! Os executáveis estão na pasta dist."