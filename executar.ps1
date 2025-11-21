# Script PowerShell para executar o Sistema de Extração de Recibos PDF

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sistema de Extração de Recibos PDF" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando o sistema..." -ForegroundColor Green
Write-Host ""

try {
    python main.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERRO: O programa não pode ser executado." -ForegroundColor Red
        Write-Host "Verifique se o Python está instalado e se todas as dependências estão instaladas." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Para instalar as dependências, execute:" -ForegroundColor Yellow
        Write-Host "pip install -r requirements.txt" -ForegroundColor Cyan
        Write-Host ""
        Read-Host "Pressione Enter para sair"
    }
} catch {
    Write-Host ""
    Write-Host "ERRO: Não foi possível executar o programa." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
}
