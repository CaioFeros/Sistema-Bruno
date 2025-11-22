"""
Sistema de log detalhado para rastreamento de processamento.
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class SistemaLogger:
    """Classe para gerenciar logs detalhados do sistema."""
    
    def __init__(self, log_file=None):
        """
        Inicializa o sistema de log.
        
        Args:
            log_file: Caminho do arquivo de log. Se None, usa log padrão.
        """
        if log_file is None:
            # Criar diretório de logs se não existir
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Criar arquivo de log com data/hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"sistema_log_{timestamp}.txt"
        
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger("SistemaBruno")
        self.logger.setLevel(logging.DEBUG)
        
        # Remover handlers existentes
        self.logger.handlers.clear()
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8', mode='a')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato de log detalhado
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 80)
        self.logger.info("SISTEMA INICIADO")
        self.logger.info(f"Arquivo de log: {self.log_file}")
        self.logger.info("=" * 80)
    
    def info(self, message: str):
        """Registra mensagem informativa."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Registra mensagem de debug."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Registra mensagem de aviso."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=None):
        """Registra mensagem de erro."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info=None):
        """Registra mensagem crítica."""
        self.logger.critical(message, exc_info=exc_info)
    
    def separador(self, titulo: str = ""):
        """Adiciona um separador visual no log."""
        if titulo:
            self.logger.info("-" * 80)
            self.logger.info(f"  {titulo}")
            self.logger.info("-" * 80)
        else:
            self.logger.info("-" * 80)
    
    def detalhes_arquivo(self, file_path: str):
        """Registra detalhes sobre um arquivo."""
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            size_mb = size / (1024 * 1024)
            self.logger.info(f"Arquivo: {path.name}")
            self.logger.info(f"Caminho completo: {file_path}")
            self.logger.info(f"Tamanho: {size:,} bytes ({size_mb:.2f} MB)")
        else:
            self.logger.warning(f"Arquivo não encontrado: {file_path}")
    
    def detalhes_texto(self, texto: str, max_chars: int = 500):
        """Registra detalhes sobre texto extraído."""
        num_chars = len(texto)
        num_lines = texto.count('\n')
        
        self.logger.info(f"Texto extraído: {num_chars:,} caracteres, {num_lines:,} linhas")
        
        # Mostrar amostra do texto
        if num_chars > max_chars:
            preview = texto[:max_chars] + "..."
        else:
            preview = texto
        
        self.logger.debug(f"Amostra do texto (primeiros {min(max_chars, num_chars)} caracteres):")
        self.logger.debug(preview)
    
    def detalhes_paginas(self, total_paginas: int, paginas_processadas: int):
        """Registra detalhes sobre processamento de páginas."""
        self.logger.info(f"Total de páginas: {total_paginas}")
        self.logger.info(f"Páginas processadas: {paginas_processadas}")
        if total_paginas > 0:
            porcentagem = (paginas_processadas / total_paginas) * 100
            self.logger.info(f"Progresso: {porcentagem:.1f}%")
    
    def detalhes_recibos(self, recibos_encontrados: int):
        """Registra detalhes sobre recibos encontrados."""
        self.logger.info(f"Recibos encontrados no PDF: {recibos_encontrados}")
    
    def detalhes_produtos(self, produtos: list, recibo_numero: str = None):
        """Registra detalhes sobre produtos encontrados."""
        if recibo_numero:
            self.logger.info(f"Produtos encontrados no recibo {recibo_numero}: {len(produtos)}")
        else:
            self.logger.info(f"Produtos encontrados: {len(produtos)}")
        
        if produtos:
            for idx, produto in enumerate(produtos, 1):
                descricao = produto.get('descricao', 'Sem descrição')
                qtd = produto.get('quantidade', 'N/A')
                valor = produto.get('valor_unitario', 'N/A')
                self.logger.info(f"  Produto {idx}: {descricao[:50]}... | Qtd: {qtd} | Valor: {valor}")
        else:
            self.logger.warning("Nenhum produto encontrado!")
    
    def detalhes_secao_produtos(self, start_idx: int, end_idx: int, total_lines: int):
        """Registra detalhes sobre a seção de produtos encontrada."""
        self.logger.info(f"Seção 'DADOS DO PRODUTO' encontrada:")
        self.logger.info(f"  Linha inicial: {start_idx}")
        self.logger.info(f"  Linha final: {end_idx}")
        self.logger.info(f"  Total de linhas na seção: {end_idx - start_idx}")
        self.logger.info(f"  Total de linhas no texto: {total_lines}")
        
        if end_idx - start_idx == 0:
            self.logger.warning("ATENÇÃO: Seção de produtos está vazia!")
    
    def detalhes_linhas_processadas(self, linhas_processadas: int, total_linhas: int):
        """Registra detalhes sobre linhas processadas."""
        self.logger.info(f"Linhas processadas: {linhas_processadas} de {total_linhas}")
        if total_linhas > 0:
            porcentagem = (linhas_processadas / total_linhas) * 100
            self.logger.info(f"Porcentagem processada: {porcentagem:.1f}%")
            
            if porcentagem < 50:
                self.logger.warning(f"ATENÇÃO: Menos de 50% das linhas foram processadas!")
    
    def get_log_file(self) -> str:
        """Retorna o caminho do arquivo de log."""
        return str(self.log_file)


# Instância global do logger (será inicializada quando necessário)
_logger_instance = None


def get_logger() -> SistemaLogger:
    """Obtém a instância global do logger."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SistemaLogger()
    return _logger_instance


def inicializar_log(log_file=None):
    """Inicializa o logger global."""
    global _logger_instance
    _logger_instance = SistemaLogger(log_file)
    return _logger_instance

