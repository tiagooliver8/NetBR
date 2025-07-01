# build_all.ps1
# Limpa dist, build antigos
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# Compila o Nuvem.exe
pyinstaller launcher.spec

# Compila o Nuvem.Test.exe (pode ajustar para --onefile se desejar)
pyinstaller NuvemTest.spec

Write-Host "Build finalizada! Os executáveis estão na pasta dist."