# Limpa build, dist, __pycache__ e arquivos .pyc do projeto
Remove-Item -Recurse -Force build, dist, __pycache__ -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Limpeza concluída. Pronto para reempacotar."
