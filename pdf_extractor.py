"""
Módulo para extração de dados de recibos de venda de PDFs.
"""
import sys
import os

# Tentar importar pdfplumber com tratamento de erro melhorado
try:
    import pdfplumber
except ImportError as e:
    # Se for executável standalone, tentar adicionar _internal ao path
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        internal_path = os.path.join(base_path, '_internal')
        if os.path.exists(internal_path) and internal_path not in sys.path:
            sys.path.insert(0, internal_path)
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                f"Não foi possível importar pdfplumber.\n"
                f"Erro original: {e}\n"
                f"Verifique se pdfplumber está na pasta _internal do executável."
            ) from e
    else:
        raise

import re
from typing import Dict, List, Optional

# Importar logger
try:
    from logger import get_logger
    logger = get_logger()
except ImportError:
    # Se logger não estiver disponível, criar um logger silencioso
    class DummyLogger:
        def info(self, *args, **kwargs): pass
        def debug(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
        def separador(self, *args, **kwargs): pass
        def detalhes_arquivo(self, *args, **kwargs): pass
        def detalhes_texto(self, *args, **kwargs): pass
        def detalhes_paginas(self, *args, **kwargs): pass
        def detalhes_recibos(self, *args, **kwargs): pass
        def detalhes_produtos(self, *args, **kwargs): pass
        def detalhes_secao_produtos(self, *args, **kwargs): pass
        def detalhes_linhas_processadas(self, *args, **kwargs): pass
    logger = DummyLogger()


def _remove_duplicate_chars(text: str) -> str:
    """
    Remove caracteres duplicados consecutivos (ex: "TTIIRR" -> "TIR").
    
    Args:
        text: Texto com poss├¡veis caracteres duplicados
        
    Returns:
        Texto limpo
    """
    if not text:
        return text
    
    # Detectar padr├úo de duplica├º├úo: caracteres repetidos em pares
    # Exemplo: "TTIIRRZZ" -> "TIRZ"
    result = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i] == text[i + 1] and text[i].isalnum():
            # Caractere duplicado, adicionar apenas uma vez
            result.append(text[i])
            i += 2
        else:
            result.append(text[i])
            i += 1
    
    return ''.join(result)


def _remove_duplicate_phrases(text: str) -> str:
    """
    Remove frases duplicadas na descri├º├úo.
    Foca em remover duplicatas completas de frases, n├úo palavras individuais.
    
    Args:
        text: Texto com poss├¡veis frases duplicadas
        
    Returns:
        Texto limpo
    """
    if not text:
        return text
    
    # Dividir em palavras
    words = text.split()
    if len(words) < 4:
        return text
    
    # Procurar por frases duplicadas completas (ex: "TIRZEPATIDE 50 MG/2ML" aparecendo duas vezes)
    # Verificar se h├í uma sequ├¬ncia de palavras que se repete
    result_words = []
    i = 0
    
    while i < len(words):
        word = words[i]
        result_words.append(word)
        
        # Verificar se as pr├│ximas palavras formam uma frase que j├í apareceu
        # Procurar por duplicatas de 3-8 palavras
        found_duplicate = False
        for phrase_len in range(3, min(9, len(words) - i)):
            if i + phrase_len * 2 > len(words):
                break
            
            phrase1 = ' '.join(words[i:i+phrase_len])
            phrase2 = ' '.join(words[i+phrase_len:i+phrase_len*2])
            
            # Se as duas frases s├úo iguais, ├® uma duplicata
            if phrase1.upper() == phrase2.upper() and len(phrase1) > 10:
                # Pular a segunda ocorr├¬ncia
                i += phrase_len * 2
                found_duplicate = True
                break
        
        if not found_duplicate:
            i += 1
    
    return ' '.join(result_words)


def _clean_product_description(descricao: str) -> str:
    """
    Limpa a descri├º├úo do produto, removendo c├│digos e informa├º├Áes extras.
    Mant├®m apenas a parte principal: NOME + DOSAGEM + FORMA
    
    Exemplo:
        "TIRZEPATIDE 50 MG/2ML - SOL INJ (FRASCO) L- 2092369271700 C086A-B250901 FAB 09/2025 VAL- 09/2027 ANVISA"
        -> "TIRZEPATIDE 50 MG/2ML"
    
    Args:
        descricao: Descri├º├úo completa do produto
        
    Returns:
        Descri├º├úo limpa
    """
    if not descricao:
        return descricao
    
    # Padr├Áes que indicam fim da descri├º├úo principal
    # Procurar por: "L-", "C086A-", "FAB", "VAL-", "ANVISA", c├│digos longos
    patterns_to_stop = [
        r'\s+L-\s+\d+',  # "L- 2092369271700"
        r'\s+C\d{3}[A-Z]?-[A-Z]\d+',  # "C086A-B250901"
        r'\s+FAB\s+\d{2}/\d{4}',  # "FAB 09/2025"
        r'\s+VAL-\s+\d{2}/\d{4}',  # "VAL- 09/2027"
        r'\s+ANVISA',  # "ANVISA"
        r'\s+\d{12,}',  # C├│digos num├®ricos longos
    ]
    
    # Encontrar a primeira ocorr├¬ncia de qualquer padr├úo de fim
    min_pos = len(descricao)
    for pattern in patterns_to_stop:
        match = re.search(pattern, descricao, re.IGNORECASE)
        if match:
            min_pos = min(min_pos, match.start())
    
    # Se encontrou um padr├úo, cortar a descri├º├úo
    if min_pos < len(descricao):
        descricao = descricao[:min_pos].strip()
    
    # Remover tra├ºos finais e espa├ºos extras
    descricao = descricao.rstrip('-').strip()
    descricao = re.sub(r'\s+', ' ', descricao)
    
    return descricao


def extract_text_from_pdf(pdf_path: str, progress_callback=None) -> str:
    """
    Extrai todo o texto de um arquivo PDF.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        progress_callback: Fun├º├úo callback(opcional) chamada com (p├ígina_atual, total_p├íginas) durante o processamento
        
    Returns:
        String com todo o texto extra├¡do do PDF
        
    Raises:
        FileNotFoundError: Se o arquivo n├úo for encontrado
        Exception: Se houver erro ao processar o PDF
    """
    logger.separador("EXTRAÇÃO DE TEXTO DO PDF")
    logger.info(f"Iniciando extração de texto: {pdf_path}")
    
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"PDF aberto com sucesso. Total de páginas: {total_pages}")
            
            paginas_com_texto = 0
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    paginas_com_texto += 1
                
                # Log a cada 100 páginas para não sobrecarregar
                if page_num % 100 == 0 or page_num == total_pages:
                    logger.debug(f"Página {page_num}/{total_pages} processada. Páginas com texto: {paginas_com_texto}")
                
                # Chamar callback de progresso se fornecido
                if progress_callback:
                    progress_callback(page_num, total_pages)
            
            logger.detalhes_paginas(total_pages, paginas_com_texto)
            logger.detalhes_texto(text)
        
        return text
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {pdf_path}", exc_info=True)
        raise FileNotFoundError(f"Arquivo n├úo encontrado: {pdf_path}")
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {str(e)}", exc_info=True)
        raise Exception(f"Erro ao processar PDF: {str(e)}")


def extract_receipt_data(text: str) -> Dict:
    """
    Extrai dados estruturados de um recibo a partir do texto extra├¡do.
    
    Args:
        text: Texto completo extra├¡do do PDF
        
    Returns:
        Dicion├írio com os dados extra├¡dos:
        {
            'numero': str,
            'vendedor': str,
            'cliente': str,
            'produtos': [
                {
                    'descricao': str,
                    'quantidade': str,
                    'valor_unitario': str
                }
            ]
        }
    """
    data = {
        'numero': None,
        'vendedor': None,
        'cliente': None,
        'produtos': []
    }
    
    # Extrair N┬║ do recibo - pode aparecer como "N┬║ 0000004510" ou "N┬║: 0000004510"
    numero_match = re.search(r'N┬║\s*:?\s*(\d+)', text, re.IGNORECASE)
    if numero_match:
        data['numero'] = numero_match.group(1).strip()
    
    # Extrair Vendedor - "Vendedor: NOME"
    vendedor_match = re.search(r'Vendedor:\s*([^\n]+)', text, re.IGNORECASE)
    if vendedor_match:
        data['vendedor'] = vendedor_match.group(1).strip()
    
    # Extrair Nome/Raz├úo Social - pode estar na linha seguinte ap├│s "NOME/RAZ├âO SOCIAL"
    # Dividir texto em linhas para busca mais precisa
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Procurar linha com "NOME/RAZ├âO SOCIAL"
        if re.search(r'NOME/RAZ├âO\s+SOCIAL', line, re.IGNORECASE):
            # Verificar se o nome est├í na mesma linha (com dois pontos)
            same_line_match = re.search(r'NOME/RAZ├âO\s+SOCIAL\s*:\s*(.+)', line, re.IGNORECASE)
            if same_line_match:
                cliente_nome = same_line_match.group(1).strip()
                data['cliente'] = cliente_nome
                break
            else:
                # Procurar na pr├│xima linha n├úo vazia
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    # Ignorar linhas vazias e linhas que s├úo outros campos
                    if next_line and 'NOME FANTASIA' not in next_line.upper() and 'CNPJ' not in next_line.upper() and 'EMAIL' not in next_line.upper():
                        # Se a linha tem conte├║do e n├úo parece ser outro campo
                        if len(next_line) > 3:
                            data['cliente'] = next_line
                            break
                if data['cliente']:
                    break
    
    # Extrair produtos
    # Procurar pela se├º├úo "DADOS DO PRODUTO" APENAS dentro deste recibo
    # Para arquivos grandes, usar busca linha por linha que é mais robusta
    
    logger.debug("Procurando seção 'DADOS DO PRODUTO'...")
    
    # Dividir texto em linhas primeiro para processar de forma mais eficiente
    all_lines = text.split('\n')
    total_lines = len(all_lines)
    logger.debug(f"Texto dividido em {total_lines} linhas")
    
    # Procurar pelo início da seção "DADOS DO PRODUTO"
    produtos_start_idx = -1
    produtos_end_idx = len(all_lines)
    
    for i, line in enumerate(all_lines):
        if re.search(r'DADOS\s+DO\s+PRODUTO', line, re.IGNORECASE):
            produtos_start_idx = i
            logger.info(f"Seção 'DADOS DO PRODUTO' encontrada na linha {i}")
            logger.debug(f"Linha encontrada: {line[:100]}...")
            break
    
    if produtos_start_idx >= 0:
        # Procurar pelo fim da seção - encontrar o próximo marcador de fim
        # IMPORTANTE: Não parar no primeiro marcador se houver pouco conteúdo antes
        # Isso evita parar em subtotais ou totais intermediários
        logger.debug("Procurando marcadores de fim da seção...")
        
        # Mínimo de linhas esperadas na seção de produtos (ajustável)
        # Para arquivos grandes, esperamos seções muito maiores
        # Se o texto tem muitas linhas, esperamos seção proporcionalmente maior
        min_linhas_secao = max(30, total_lines // 20)  # Pelo menos 30 linhas ou 5% do texto, o que for maior
        logger.debug(f"Mínimo de linhas esperadas na seção: {min_linhas_secao} (total de linhas: {total_lines})")
        
        # Procurar todos os possíveis marcadores de fim
        possiveis_fins = []
        
        for i in range(produtos_start_idx + 1, len(all_lines)):
            line = all_lines[i].upper().strip()
            
            # Verificar se encontramos um marcador de fim
            if re.search(r'TOTAL\s+DE\s+MERCADORIAS', line, re.IGNORECASE):
                # Verificar se a linha contém valores numéricos (indica total real)
                if re.search(r'[\d.,]+\s+[\d.,]+\s+[\d.,]+', line):
                    possiveis_fins.append((i, 'TOTAL_DE_MERCADORIAS', line))
            elif re.search(r'^TOTAIS', line, re.IGNORECASE):
                possiveis_fins.append((i, 'TOTAIS', line))
            elif re.search(r'^PAGAMENTO', line, re.IGNORECASE):
                possiveis_fins.append((i, 'PAGAMENTO', line))
        
        # Decidir qual marcador usar
        if possiveis_fins:
            # Se houver apenas um marcador ou o primeiro marcador já está longe o suficiente
            primeiro_fim = possiveis_fins[0]
            linhas_ate_primeiro = primeiro_fim[0] - produtos_start_idx
            
            # Se o primeiro marcador já está distante o suficiente, usar ele
            if linhas_ate_primeiro >= min_linhas_secao:
                produtos_end_idx = primeiro_fim[0]
                logger.info(f"Marcador de fim encontrado na linha {primeiro_fim[0]}: {primeiro_fim[2][:50]}... (tipo: {primeiro_fim[1]})")
            else:
                # Se o primeiro marcador está muito perto, pode ser subtotal
                # Procurar pelo próximo marcador que esteja mais distante
                logger.debug(f"Primeiro marcador muito próximo (linha {primeiro_fim[0]}, apenas {linhas_ate_primeiro} linhas). Procurando próximo marcador...")
                
                # Procurar pelo próximo marcador "PAGAMENTO" ou "TOTAIS" que indica fim real
                fim_real_encontrado = False
                for fim_idx, fim_tipo, fim_line in possiveis_fins:
                    linhas_ate_fim = fim_idx - produtos_start_idx
                    # PAGAMENTO e TOTAIS são mais prováveis de serem o fim real
                    if fim_tipo in ['PAGAMENTO', 'TOTAIS'] and linhas_ate_fim >= min_linhas_secao:
                        produtos_end_idx = fim_idx
                        logger.info(f"Marcador de fim REAL encontrado na linha {fim_idx}: {fim_line[:50]}... (tipo: {fim_tipo})")
                        fim_real_encontrado = True
                        break
                
                # Se não encontrou marcador de fim real, procurar mais adiante no texto
                # Por padrão, continuar procurando até encontrar "PAGAMENTO" ou outro marcador confiável
                if not fim_real_encontrado:
                    logger.debug("Procurando marcadores mais distantes no texto...")
                    
                    # Procurar mais adiante no texto (até 200 linhas além do último marcador ou fim do texto)
                    limite_busca = min(len(all_lines), (possiveis_fins[-1][0] if possiveis_fins else produtos_start_idx) + 200)
                    
                    for i in range(possiveis_fins[-1][0] + 1 if possiveis_fins else produtos_start_idx + min_linhas_secao, limite_busca):
                        line = all_lines[i].upper().strip()
                        
                        # Procurar por PAGAMENTO (sempre fim real)
                        if re.search(r'^PAGAMENTO', line, re.IGNORECASE):
                            produtos_end_idx = i
                            linhas_ate_fim = i - produtos_start_idx
                            logger.info(f"Marcador PAGAMENTO encontrado na linha {i} ({linhas_ate_fim} linhas do início) - fim real da seção")
                            fim_real_encontrado = True
                            break
                        # Procurar por TOTAIS mais distante
                        elif re.search(r'^TOTAIS', line, re.IGNORECASE):
                            linhas_ate_fim = i - produtos_start_idx
                            if linhas_ate_fim >= min_linhas_secao:
                                produtos_end_idx = i
                                logger.info(f"Marcador TOTAIS encontrado na linha {i} ({linhas_ate_fim} linhas do início)")
                                fim_real_encontrado = True
                                break
                    
                    # Se ainda não encontrou, usar o último marcador que esteja razoavelmente distante
                    if not fim_real_encontrado:
                        for fim_idx, fim_tipo, fim_line in reversed(possiveis_fins):
                            linhas_ate_fim = fim_idx - produtos_start_idx
                            # Se está pelo menos 20% mais longe que o mínimo, pode ser válido
                            if linhas_ate_fim >= min_linhas_secao * 0.8:
                                produtos_end_idx = fim_idx
                                logger.info(f"Usando marcador {fim_tipo} na linha {fim_idx} ({linhas_ate_fim} linhas do início)")
                                fim_real_encontrado = True
                                break
                    
                    # Último recurso: usar o último marcador disponível
                    if not fim_real_encontrado and possiveis_fins:
                        ultimo_fim = possiveis_fins[-1]
                        produtos_end_idx = ultimo_fim[0]
                        logger.warning(f"ATENÇÃO: Usando último marcador disponível na linha {ultimo_fim[0]} (apenas {ultimo_fim[0] - produtos_start_idx} linhas do início). Pode estar muito cedo!")
        else:
            # Nenhum marcador encontrado, usar até o fim do texto
            logger.warning("Nenhum marcador de fim encontrado, usando todas as linhas até o final do texto")
            produtos_end_idx = len(all_lines)
        
        # Extrair as linhas da seção de produtos
        lines = all_lines[produtos_start_idx:produtos_end_idx]
        logger.detalhes_secao_produtos(produtos_start_idx, produtos_end_idx, total_lines)
        
        # Log das primeiras 20 linhas para debug
        logger.debug("Primeiras 20 linhas da seção de produtos:")
        for idx, line in enumerate(lines[:20], produtos_start_idx):
            logger.debug(f"  Linha {idx} (índice {idx-produtos_start_idx}): {line[:100]}...")
        
        # Procurar por todas as ocorr├¬ncias de padr├Áes de produto
        # Padr├úo: linha com UNID (2-3 letras) seguido de QTD e V.UNIT├üRIO
        # Pode haver m├║ltiplos produtos na mesma se├º├úo
        
        i = 0
        produtos_encontrados = []
        linhas_processadas = set()  # Evitar processar a mesma linha duas vezes
        produtos_vistos = set()  # Evitar produtos duplicados
        
        # Log detalhado para debug
        linhas_com_padrao = 0
        linhas_ignoradas = 0
        linhas_sem_padrao = 0
        
        logger.debug(f"Iniciando busca de produtos nas {len(lines)} linhas da seção...")
        
        # Mostrar primeiras 15 linhas da seção para debug
        logger.debug("Primeiras 15 linhas da seção de produtos:")
        for idx, line in enumerate(lines[:15]):
            logger.debug(f"  Linha {idx}: {line[:120]}")
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Pular linha se j├í foi processada
            if i in linhas_processadas:
                i += 1
                continue
            
            # Procurar por linha com padr├úo UNID QTD V.UNIT├üRIO
            # Tentar múltiplos padrões para capturar todas as variações possíveis
            produto_match = None
            
            # Padrão 1: UNID (2-3 letras) + números (padrão mais comum)
            # Formato: UNI 10,000 900,000 ou UNI 10.000 900.000
            # Pode ter texto antes do UNID (códigos, etc.)
            produto_match = re.search(r'([A-Z]{2,3})\s+([\d.,]+\d)\s+([\d.,]+\d)', line)
            
            # Padrão 2: UNID (1-4 letras) + números com mais flexibilidade (permite mais espaços)
            # IMPORTANTE: Pode ter texto antes do UNID (códigos de produto, etc.)
            if not produto_match:
                produto_match = re.search(r'([A-Z]{1,4})\s+([\d.,]{2,})\s+([\d.,]{3,})', line)
            
            # Log de teste para linha 3 (debug)
            if i == 3 and not produto_match and 'ANVISA' in line.upper() and ('FR' in line or 'CN' in line):
                logger.debug(f"DEBUG Linha 3: Testando padrões... Linha: {line[:150]}")
                # Testar padrão 2b manualmente para debug
                teste_padrao = re.search(r'\b([A-Z]{2})\s+([\d.,]{3,})\s+([\d.,]{3,})', line)
                if teste_padrao:
                    logger.debug(f"DEBUG Linha 3: Padrão 2b ENCONTRADO! UNID={teste_padrao.group(1)}, QTD={teste_padrao.group(2)}, VALOR={teste_padrao.group(3)}")
                else:
                    logger.debug(f"DEBUG Linha 3: Padrão 2b NÃO encontrado")
            
            # Padrão 2b: Procurar UNID em qualquer lugar da linha seguido de dois números grandes
            # IMPORTANTE: Procurar por padrão "2 letras + espaço + número + espaço + número"
            # Exemplos: "...ANVISA FR 10,000 900,000" ou "...ANVISA CN 2,000 3.100,000"
            if not produto_match:
                # Buscar por: 2 letras maiúsculas isoladas + espaço + número grande + espaço + número grande
                # IMPORTANTE: Usar \b (word boundary) para garantir que não é parte de palavra maior
                # Procura por "FR" ou "CN" seguido de espaços e números
                # Simplificar: procurar por qualquer 2 letras maiúsculas seguidas de espaço e números
                produto_match = re.search(r'\b([A-Z]{2})\s+([\d.,]+)\s+([\d.,]+)', line)
                if produto_match:
                    unid_text = produto_match.group(1)
                    unid_pos = produto_match.start(1)
                    texto_antes = line[:unid_pos].strip().upper()
                    
                    # Log de debug para linha 3
                    if i == 3:
                        logger.debug(f"DEBUG Linha 3: Padrão 2b encontrado! UNID={unid_text}, pos={unid_pos}")
                        logger.debug(f"DEBUG Linha 3: Texto antes='{texto_antes[-20:]}'")
                    
                    # Ignorar se for parte de palavras conhecidas
                    palavras_ignorar = ['FRETE', 'FRET', 'FRENTE', 'FRANC', 'FRANCA', 'CNPJ', 'CNP']
                    if any(palavra in texto_antes[-15:] for palavra in palavras_ignorar):
                        if i == 3:
                            logger.debug(f"DEBUG Linha 3: REJEITADO - faz parte de palavra conhecida")
                        produto_match = None
                    # Se está depois de "ANVISA", é provavelmente válido (padrão comum)
                    elif 'ANVISA' in texto_antes:
                        # Aceitar - ANVISA geralmente vem antes do UNID de produto
                        if i == 3:
                            logger.debug(f"DEBUG Linha 3: ACEITO - está depois de ANVISA")
                        pass
                    # Se tem muitos códigos antes (indicando linha de produto), aceitar
                    elif len(texto_antes) > 30 and any(char.isdigit() for char in texto_antes[-10:]):
                        # Tem muitos caracteres e números antes, provavelmente é válido
                        if i == 3:
                            logger.debug(f"DEBUG Linha 3: ACEITO - tem muitos códigos antes")
                        pass
                    else:
                        if i == 3:
                            logger.debug(f"DEBUG Linha 3: REJEITADO - não passou nas validações")
                        # Se não passou nas validações, mas está em contexto de produto, aceitar mesmo assim
                        # (melhor aceitar falso positivo do que perder produto)
                        pass  # Aceitar mesmo assim se encontrou o padrão
            
            # Padrão 3: Procurar por linhas que tenham descrição de produto na linha anterior
            # e UNID QTD VALOR na linha atual (produtos podem estar em múltiplas linhas)
            if not produto_match and i > 0:
                # Verificar se a linha anterior tem descrição de produto
                linha_anterior = lines[i-1].strip()
                tem_descricao_produto = (
                    any(nome in linha_anterior.upper() for nome in ['TIRZEPATIDE', 'SEMAGLUTIDA', 'SEMAGLUTIDE', 'CANETA']) or
                    (len(linha_anterior) > 20 and any(keyword in linha_anterior.upper() for keyword in ['MG', 'ML', 'SOL', 'INJ', 'FRASCO']))
                )
                
                if tem_descricao_produto:
                    # Esta linha pode ter UNID QTD VALOR
                    produto_match = re.search(r'([A-Z]{2,3})\s+([\d.,]+\d)\s+([\d.,]+\d)', line)
                    if not produto_match:
                        # Tentar padrão mais flexível
                        produto_match = re.search(r'([A-Z]{1,4})\s*([\d.,]{2,})\s+([\d.,]{3,})', line)
            
            # Log detalhado quando encontrar padrão (apenas primeiras vezes para não sobrecarregar)
            if produto_match:
                linhas_com_padrao += 1
                if linhas_com_padrao <= 5:
                    logger.debug(f"Linha {i} COM PADRÃO ENCONTRADO: UNID={produto_match.group(1)}, QTD={produto_match.group(2)}, VALOR={produto_match.group(3)}")
                    logger.debug(f"  Linha completa: {line[:120]}")
            
            if produto_match:
                # Verificar se n├úo ├® uma linha de total
                if 'TOTAL' in line.upper() or 'MERCADORIAS' in line.upper():
                    linhas_processadas.add(i)  # Marcar como processada
                    linhas_ignoradas += 1
                    logger.debug(f"Linha {i} ignorada (é linha de total): {line[:60]}...")
                    i += 1
                    continue
                
                unid = produto_match.group(1)
                qtd = produto_match.group(2)
                valor = produto_match.group(3)
                
                # Verificar duplicata ANTES de processar (usando valores brutos)
                produto_key_temp = f"{qtd}|{valor}|{unid}"
                if produto_key_temp in produtos_vistos:
                    linhas_processadas.add(i)  # Marcar como processada
                    i += 1
                    continue
                
                # Validar que quantidade e valor cont├¬m n├║meros
                # Aceitar se pelo menos um deles tem n├║meros
                qtd_clean = qtd.replace(',', '').replace('.', '').replace(' ', '')
                valor_clean = valor.replace(',', '').replace('.', '').replace(' ', '')
                
                # Verificar se tem pelo menos um d├¡gito
                tem_numero = any(c.isdigit() for c in qtd_clean) or any(c.isdigit() for c in valor_clean)
                
                if not tem_numero:
                    linhas_processadas.add(i)  # Marcar como processada
                    i += 1
                    continue
                
                # Verificar se esta linha n├úo ├® apenas uma descri├º├úo de produto (sem dados num├®ricos v├ílidos)
                # Se a linha cont├®m apenas texto descritivo sem padr├úo de produto v├ílido, pular
                if len(line) > 50 and not any(c.isdigit() for c in qtd) and not any(c.isdigit() for c in valor):
                    # Pode ser uma linha de descri├º├úo, n├úo um produto
                    linhas_processadas.add(i)
                    i += 1
                    continue
                
                # Procurar descri├º├úo nas linhas anteriores
                # IMPORTANTE: N├úo pegar linhas que j├í foram usadas como descri├º├úo de outro produto
                descricao_parts = []
                linhas_usadas_como_descricao = set()
                
                # Verificar linha atual (pode ter parte da descri├º├úo antes do UNID)
                before_unid = line[:produto_match.start()].strip()
                if before_unid and len(before_unid) > 5:
                    # Verificar se n├úo ├® s├│ n├║meros ou c├│digo
                    if not re.match(r'^[\d.,\s]+$', before_unid):
                        before_clean = before_unid.replace(' ', '').replace('-', '')
                        if not re.match(r'^\d{10,15}$', before_clean):
                            # Verificar se n├úo ├® c├│digo alfanum├®rico curto
                            if not re.match(r'^[A-Z0-9]{8,15}$', before_clean):
                                descricao_parts.append(before_unid)
                
                # Verificar linhas anteriores (at├® 5 linhas para tr├ís para capturar descri├º├Áes longas)
                # IMPORTANTE: Processar de tr├ís para frente (da mais pr├│xima para a mais distante)
                # para garantir que pegamos a primeira linha v├ílida (mais pr├│xima do produto)
                linhas_validas = []
                linha_nome_produto = None  # Prioridade m├íxima: linha que come├ºa com nome de produto
                
                # Aumentar o alcance para até 10 linhas anteriores (para arquivos grandes com múltiplas linhas de descrição)
                for j in range(i-1, max(-1, i-11), -1):  # De i-1 at├® i-10, de tr├ís para frente
                    if j < 0:
                        break
                    
                    # N├âO pegar linhas que j├í foram processadas como produto
                    if j in linhas_processadas:
                        continue
                    
                    # N├âO pegar linhas que j├í foram usadas como descri├º├úo de outro produto
                    if j in linhas_usadas_como_descricao:
                        continue
                    
                    prev_line = lines[j].strip()
                    
                    if not prev_line:
                        continue
                    
                    # N├âO pegar linhas que s├úo n├║meros de recibo (4 d├¡gitos)
                    if re.match(r'^\d{4}$', prev_line):
                        continue
                    
                    # Ignorar cabe├ºalhos
                    if any(keyword in prev_line.upper() for keyword in ['C├ôDIGO', 'DESCRI├ç├âO DOS PRODUTOS', 'UNID', 'QTD', 'V.UNIT├üRIO']):
                        continue
                    
                    # Ignorar se ├® uma linha de produto (tem padr├úo UNID QTD VALOR)
                    if re.search(r'([A-Z]{2,3})\s+([\d.,]+)\s+([\d.,]+)', prev_line):
                        continue
                    
                    # Ignorar linhas que s├úo apenas c├│digos
                    prev_clean = prev_line.replace(' ', '').replace('-', '')
                    if re.match(r'^\d{10,15}$', prev_clean) or re.match(r'^[A-Z0-9]{8,20}$', prev_clean):
                        continue
                    
                    prev_upper = prev_line.upper()
                    
                    # IGNORAR primeiro: linhas que s├úo claramente c├│digos de produto (FAB, VAL, ANVISA, etc.)
                    # Isso evita que essas linhas sejam consideradas como descri├º├úo
                    if any(keyword in prev_upper for keyword in ['FAB', 'VAL-', 'VAL ', 'ANVISA']):
                        continue
                    
                    # Ignorar linhas que come├ºam com "L-" seguido de c├│digo
                    if re.match(r'^L-\s*[A-Z0-9]', prev_line):
                        continue
                    
                    # PRIMEIRA PRIORIDADE: Linhas que come├ºam com nome de produto conhecido
                    # Esta ├® a descri├º├úo mais importante - parar aqui se encontrarmos
                    eh_nome_produto = any(prev_upper.startswith(nome) for nome in ['TIRZEPATIDE', 'SEMAGLUTIDA', 'SEMAGLUTIDE', 'CANETA'])
                    
                    if eh_nome_produto:
                        # Encontrou linha que come├ºa com nome de produto - usar APENAS esta como descri├º├úo
                        linha_nome_produto = prev_line
                        linhas_usadas_como_descricao.add(j)
                        break  # Parar busca - encontrou a descri├º├úo correta
                    
                    # Segunda prioridade: Linhas com palavras-chave de produto (mas n├úo nome direto)
                    if len(prev_line) > 10:
                        # Deve conter palavras-chave de produto (MG, ML) E n├úo ser c├│digo
                        tem_palavra_chave = any(keyword in prev_upper for keyword in ['MG', 'ML', 'SOL', 'INJ', 'FRASCO'])
                        
                        if tem_palavra_chave:
                            # Adicionar ├á lista de linhas v├ílidas (da mais pr├│xima para a mais distante)
                            if prev_line not in linhas_validas:
                                linhas_validas.append(prev_line)
                                linhas_usadas_como_descricao.add(j)
                
                # Se encontrou linha que come├ºa com nome de produto, usar APENAS ela
                if linha_nome_produto:
                    descricao_parts = [linha_nome_produto]  # Substituir todas as outras partes
                elif linhas_validas:
                    # Se n├úo encontrou nome de produto direto, usar linhas v├ílidas encontradas
                    # Adicionar na ordem correta (primeira linha encontrada primeiro)
                    # Como processamos de tr├ís para frente, a primeira linha v├ílida (mais pr├│xima) est├í no in├¡cio da lista
                    for linha_valida in linhas_validas:
                        if linha_valida not in descricao_parts:
                            descricao_parts.insert(0, linha_valida)
                
                # Combinar partes da descri├º├úo
                descricao = ' '.join(descricao_parts).strip()
                descricao = re.sub(r'\s+', ' ', descricao)
                
                # Remover duplicatas de caracteres (problema de extra├º├úo)
                # Se houver padr├úo de duplica├º├úo (ex: "TTIIRRZZ"), limpar
                descricao = _remove_duplicate_chars(descricao)
                
                # Remover duplicatas de palavras/frases inteiras
                descricao = _remove_duplicate_phrases(descricao)
                
                # Log detalhado ANTES de adicionar o produto
                logger.debug(f"=== ADICIONANDO PRODUTO (linha {i}) ===")
                logger.debug(f"  Descrição ANTES limpeza: '{' '.join(descricao_parts).strip()}'")
                logger.debug(f"  Descrição DEPOIS limpeza: '{descricao}'")
                logger.debug(f"  UNID: '{unid}'")
                logger.debug(f"  Quantidade: '{qtd}'")
                logger.debug(f"  Valor Unitário: '{valor}'")
                logger.debug(f"  Linha completa: '{line[:150]}'")
                
                # Adicionar produto
                if 'TOTAL' not in descricao.upper() and 'MERCADORIAS' not in descricao.upper():
                    # Criar chave ├║nica para verificar duplicatas
                    # Usar quantidade e valor para identificar produtos ├║nicos
                    produto_key = f"{qtd}|{valor}|{unid}"
                    
                    # Verificar se j├í existe um produto com mesma quantidade e valor
                    # (mesmo produto n├úo deve aparecer duas vezes)
                    if produto_key not in produtos_vistos:
                        produto = {
                            'descricao': descricao if descricao else f'Produto {len(produtos_encontrados) + 1}',
                            'quantidade': qtd,
                            'valor_unitario': valor
                        }
                        logger.debug(f"  ✓ PRODUTO ADICIONADO ao array:")
                        logger.debug(f"    - Descrição: '{produto['descricao']}'")
                        logger.debug(f"    - Quantidade: '{produto['quantidade']}'")
                        logger.debug(f"    - Valor Unitário: '{produto['valor_unitario']}'")
                        produtos_encontrados.append(produto)
                        produtos_vistos.add(produto_key)
                        linhas_processadas.add(i)
                    else:
                        # Produto duplicado detectado - pular esta linha
                        logger.debug(f"  ✗ PRODUTO DUPLICADO - ignorado (já existe: {produto_key})")
                        linhas_processadas.add(i)
                else:
                    logger.debug(f"  ✗ PRODUTO REJEITADO - contém TOTAL/MERCADORIAS na descrição")
            
            else:
                # Linha sem padrão de produto reconhecido
                linhas_sem_padrao += 1
                # Log de amostra das linhas sem padrão - especialmente linhas que parecem ter dados
                # Verificar se a linha tem números que parecem QTD e VALOR
                tem_numeros = re.search(r'[\d.,]{4,}', line)
                if tem_numeros and ('ANVISA' in line.upper() or 'FR ' in line.upper() or 'CN ' in line.upper() or i < 10):
                    logger.debug(f"Linha {i} sem padrão de produto (mas tem números): {line[:120]}...")
                elif i < 10:
                    logger.debug(f"Linha {i} sem padrão de produto: {line[:80]}...")
            
            i += 1
        
        # Log detalhado do processamento
        logger.debug(f"Estatísticas de processamento:")
        logger.debug(f"  Linhas com padrão encontrado: {linhas_com_padrao}")
        logger.debug(f"  Linhas ignoradas (totais, etc.): {linhas_ignoradas}")
        logger.debug(f"  Linhas sem padrão: {linhas_sem_padrao}")
        logger.debug(f"  Linhas processadas como produtos: {len(produtos_encontrados)}")
        
        # Adicionar todos os produtos encontrados
        if produtos_encontrados:
            data['produtos'] = produtos_encontrados
            logger.detalhes_produtos(produtos_encontrados, data.get('numero'))
            logger.detalhes_linhas_processadas(len(linhas_processadas), len(lines))
        else:
            # Se n├úo encontrou produtos, garantir que a lista est├í vazia
            data['produtos'] = []
            logger.warning("Nenhum produto encontrado na seção de produtos!")
            logger.detalhes_linhas_processadas(0, len(lines))
    else:
        # Se n├úo encontrou se├º├úo de produtos, garantir que a lista est├í vazia
        data['produtos'] = []
        logger.warning("Seção 'DADOS DO PRODUTO' não encontrada no texto!")
    
    return data


def extract_from_pdf(pdf_path: str, progress_callback=None) -> List[Dict]:
    """
    Fun├º├úo principal para extrair dados de um PDF.
    Suporta m├║ltiplos recibos no mesmo PDF.
    Usa tanto extra├º├úo de texto quanto de tabelas para maior precis├úo.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        progress_callback: Fun├º├úo callback(opcional) chamada com (p├ígina_atual, total_p├íginas, mensagem) durante o processamento
        
    Returns:
        Lista de dicion├írios com os dados extra├¡dos de cada recibo
    """
    logger.separador("EXTRACTION FROM PDF")
    logger.info(f"Processando arquivo: {pdf_path}")
    
    if progress_callback:
        progress_callback(0, 0, "Extraindo texto do PDF...")
    text = extract_text_from_pdf(pdf_path, progress_callback)
    
    if progress_callback:
        progress_callback(0, 0, "Processando recibos...")
    
    logger.info("Procurando recibos no texto extraído...")
    
    # Detectar múltiplos recibos usando múltiplos critérios
    receipts = []
    
    # Critério 1: Procurar por padrão "RECIBO DE VENDA" seguido de data (mais confiável)
    # Formato: "RECIBO DE VENDA DD/MM/YYYY HH:MM:SS"
    recibo_pattern = r'RECIBO\s+DE\s+VENDA\s+\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}'
    recibo_matches = list(re.finditer(recibo_pattern, text, re.IGNORECASE))
    
    # Critério 2: Procurar por todos os números de recibo no texto (padrão "Nº", "N°", etc.)
    # Tentar múltiplas variações do caractere "º"
    numero_patterns = [
        r'N[º°]\s*:?\s*(\d+)',  # Nº ou N°
        r'N\.\s*:?\s*(\d+)',     # N.
        r'Numero\s*:?\s*(\d+)',  # Numero
        r'Número\s*:?\s*(\d+)',  # Número
    ]
    numero_matches = []
    for pattern in numero_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        numero_matches.extend(matches)
    
    # Remover duplicatas (mesma posição)
    numero_matches = list({m.start(): m for m in numero_matches}.values())
    numero_matches.sort(key=lambda m: m.start())
    
    # Critério 3: Procurar por padrão "Página X de Y" para identificar início de novos recibos
    # Se o padrão "Página 1 de" aparece múltiplas vezes, pode ser múltiplos recibos
    pagina_pattern = r'P[áa]gina\s+1\s+de\s+\d+'
    pagina_matches = list(re.finditer(pagina_pattern, text, re.IGNORECASE))
    
    # Decidir qual critério usar
    all_positions = []
    
    # Se encontrou padrão "RECIBO DE VENDA", usar ele (mais confiável)
    if recibo_matches:
        logger.info(f"Encontrados {len(recibo_matches)} recibos pelo padrão 'RECIBO DE VENDA'")
        for match in recibo_matches:
            # Procurar número do recibo após o padrão (próximas 300 caracteres)
            texto_apos = text[match.end():match.end()+300]
            numero_apos = None
            for pattern in numero_patterns:
                numero_match = re.search(pattern, texto_apos, re.IGNORECASE)
                if numero_match:
                    numero_apos = numero_match.group(1) if numero_match.groups() else None
                    break
            
            all_positions.append({
                'pos': match.start(),
                'tipo': 'RECIBO',
                'numero': numero_apos,
                'match': match
            })
    # Se não encontrou "RECIBO DE VENDA", mas encontrou padrões "Nº", usar eles
    elif numero_matches:
        logger.info(f"Encontrados {len(numero_matches)} recibos pelo padrão 'Nº'")
        for match in numero_matches:
            numero_recibo = match.group(1) if match.groups() else None
            all_positions.append({
                'pos': match.start(),
                'tipo': 'Nº',
                'numero': numero_recibo,
                'match': match
            })
    # Se ainda não encontrou, tentar padrão de páginas
    elif len(pagina_matches) > 1:
        logger.info(f"Encontradas {len(pagina_matches)} ocorrências de 'Página 1 de X', possivelmente múltiplos recibos")
        for match in pagina_matches:
            all_positions.append({
                'pos': match.start(),
                'tipo': 'PÁGINA',
                'numero': None,
                'match': match
            })
    
    # Ordenar por posição no texto
    all_positions.sort(key=lambda x: x['pos'])
    total_recibos = len(all_positions) if all_positions else 1
    logger.info(f"Total de recibos encontrados: {total_recibos}")
    
    if len(all_positions) == 0:
        # Nenhum padrão encontrado, tentar detectar por divisão de páginas
        logger.warning("Nenhum padrão claro encontrado, tentando detectar por páginas...")
        
        # Verificar se há múltiplas páginas no PDF
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"PDF tem {total_pages} páginas")
            
            # Se tem mais de 1 página, tentar processar cada página separadamente
            if total_pages > 1:
                logger.info(f"Processando cada página como um recibo separado...")
                texto_por_pagina = text.split('\n')
                # Dividir texto por páginas (aproximadamente)
                caracteres_por_pagina = len(text) // total_pages
                
                for page_num in range(total_pages):
                    start_pos = page_num * caracteres_por_pagina
                    end_pos = (page_num + 1) * caracteres_por_pagina if page_num < total_pages - 1 else len(text)
                    
                    if progress_callback:
                        progress_callback(page_num + 1, total_pages, f"Processando página {page_num + 1} de {total_pages}...")
                    
                    page_text = text[start_pos:end_pos]
                    
                    # Extrair dados da página
                    data = extract_receipt_data(page_text)
                    
                    # Adicionar número de página como identificador
                    if not data.get('numero'):
                        data['numero'] = f"PAGINA_{page_num + 1}"
                    
                    if data.get('produtos') or data.get('vendedor'):
                        receipts.append(data)
                        logger.info(f"Página {page_num + 1}: {len(data.get('produtos', []))} produtos encontrados")
            else:
                # Apenas 1 página, processar como recibo único
                logger.warning("Apenas 1 página encontrada, processando como recibo único...")
                if progress_callback:
                    progress_callback(1, 1, "Processando recibo único...")
                data = extract_receipt_data(text)
                data = _enhance_with_tables(pdf_path, data, progress_callback)
                if data.get('numero') or data.get('produtos'):
                    receipts.append(data)
    else:
        # Processar cada recibo separadamente
        logger.info(f"Processando {total_recibos} recibos separadamente...")
        for i, recibo_info in enumerate(all_positions):
            numero_recibo = recibo_info.get('numero')
            start_pos = recibo_info['pos']
            tipo_recibo = recibo_info['tipo']
            
            logger.info(f"Processando recibo {i + 1}/{total_recibos}: Tipo={tipo_recibo}, Nº={numero_recibo}")
            
            if progress_callback:
                progress_callback(i + 1, total_recibos, f"Processando recibo {i + 1} de {total_recibos}...")
            
            # Determinar fim do recibo (início do próximo ou fim do texto)
            if i + 1 < len(all_positions):
                end_pos = all_positions[i + 1]['pos']
            else:
                end_pos = len(text)
            
            # Extrair seção do recibo - garantir que está completamente isolada
            receipt_text = text[start_pos:end_pos]
            logger.debug(f"Recibo {i + 1}: Texto extraído tem {len(receipt_text)} caracteres")
            
            # Limpar o texto para garantir que não há resíduos de outros recibos
            # Procurar por marcadores de fim de recibo (PAGAMENTO, TOTAIS) antes do próximo recibo
            if i + 1 < len(all_positions):
                # Procurar por padrões que indiquem fim do recibo atual
                # Procurar por "PAGAMENTO" ou "TOTAIS" que venham antes do próximo recibo
                texto_antes_proximo = text[start_pos:end_pos]
                
                # Procurar por marcadores de fim
                fim_markers = ['PAGAMENTO', 'TOTAIS', 'TOTAL DE MERCADORIAS']
                ultimo_fim = -1
                
                for marker in fim_markers:
                    # Procurar todas as ocorrências do marcador
                    marker_pattern = re.compile(re.escape(marker), re.IGNORECASE)
                    for marker_match in marker_pattern.finditer(texto_antes_proximo):
                        marker_pos = marker_match.end()
                        # Verificar se este marcador está mais próximo do fim que o último encontrado
                        if marker_pos > ultimo_fim and marker_pos < len(texto_antes_proximo) - 100:
                            # Verificar se depois deste marcador há mais conteúdo do recibo (linhas de pagamento)
                            texto_depois_marker = texto_antes_proximo[marker_pos:]
                            # Se tem mais de 200 caracteres depois, pode ser que ainda seja parte do recibo
                            if len(texto_depois_marker) < 500:
                                ultimo_fim = marker_pos
                
                # Se encontrou um marcador de fim válido, usar ele
                if ultimo_fim > 0:
                    # Buscar próxima ocorrência de "RECIBO DE VENDA" ou "Página 1" após o fim
                    proximo_inicio = texto_antes_proximo[ultimo_fim:].find('RECIBO DE VENDA')
                    if proximo_inicio > 0:
                        receipt_text = texto_antes_proximo[:ultimo_fim + proximo_inicio]
                    elif proximo_inicio == -1:
                        # Procurar por "Página 1" que indica início do próximo recibo
                        proximo_inicio = re.search(r'P[áa]gina\s+1\s+de', texto_antes_proximo[ultimo_fim:], re.IGNORECASE)
                        if proximo_inicio:
                            receipt_text = texto_antes_proximo[:ultimo_fim + proximo_inicio.start()]
            
            # Extrair dados do recibo APENAS do texto desta seção isolada
            # Criar um novo dicionário limpo para este recibo
            logger.debug(f"Recibo {i + 1}: Extraindo dados do texto...")
            data = extract_receipt_data(receipt_text)
            
            # Garantir que o número do recibo está correto e forçar
            if numero_recibo:
                data['numero'] = numero_recibo
            elif not data.get('numero'):
                # Se não tem número, usar índice do recibo
                data['numero'] = f"RECIBO_{i + 1}"
            
            # Validar que os produtos extra├¡dos pertencem a este recibo
            # Se n├úo h├í produtos, garantir que a lista est├í vazia
            if 'produtos' not in data:
                data['produtos'] = []
            
            logger.debug(f"Recibo {i + 1}: Produtos encontrados antes da validação: {len(data.get('produtos', []))}")
            
            # Validar produtos: garantir que t├¬m dados v├ílidos e n├úo s├úo duplicados
            produtos_validos = []
            produtos_vistos = set()  # Para evitar duplicatas
            
            for produto in data.get('produtos', []):
                # Validar que o produto tem dados v├ílidos
                qtd = produto.get('quantidade', '').strip()
                valor = produto.get('valor_unitario', '').strip()
                desc = produto.get('descricao', '').strip()
                
                # Aceitar produto se tiver quantidade OU valor (descri├º├úo pode estar vazia)
                if qtd or valor:
                    # Criar chave ├║nica para evitar duplicatas
                    produto_key = f"{desc}|{qtd}|{valor}"
                    if produto_key not in produtos_vistos:
                        produtos_validos.append(produto)
                        produtos_vistos.add(produto_key)
            
            data['produtos'] = produtos_validos
            
            logger.info(f"Recibo {i + 1}: {len(produtos_validos)} produtos válidos após validação")
            
            # Log detalhado dos produtos que serão enviados para processamento
            if produtos_validos:
                logger.debug(f"Recibo {i + 1}: Produtos que serão processados:")
                for pidx, produto in enumerate(produtos_validos, 1):
                    logger.debug(f"  Produto {pidx} para processar:")
                    logger.debug(f"    Descrição original: '{produto.get('descricao', '')}'")
                    logger.debug(f"    Quantidade original: '{produto.get('quantidade', '')}'")
                    logger.debug(f"    Valor Unitário original: '{produto.get('valor_unitario', '')}'")
            
            # N├âO usar _enhance_with_tables para m├║ltiplos recibos
            # pois pode misturar produtos entre recibos
            # Apenas usar extra├º├úo de texto que j├í est├í isolada por se├º├úo
            
            # Adicionar apenas se tiver dados v├ílidos
            if data.get('numero') or data.get('produtos') or data.get('vendedor'):
                receipts.append(data)
                logger.info(f"Recibo {i + 1}: Adicionado à lista de recibos processados")
            else:
                logger.warning(f"Recibo {i + 1}: Não foi adicionado (sem dados válidos)")
    
    logger.separador("FIM DA EXTRAÇÃO")
    logger.info(f"Total de recibos processados com sucesso: {len(receipts)}")
    
    if not receipts:
        logger.warning("Nenhum recibo processado com sucesso, tentando extrair como recibo único...")
        return [extract_receipt_data(text)]
    
    return receipts


def _enhance_with_tables(pdf_path: str, data: Dict, text_start: int = 0, text_end: int = None, progress_callback=None) -> Dict:
    """
    Melhora os dados extra├¡dos usando tabelas do PDF quando dispon├¡vel.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        data: Dicion├írio com dados j├í extra├¡dos
        text_start: Posi├º├úo inicial do texto do recibo (para m├║ltiplos recibos)
        text_end: Posi├º├úo final do texto do recibo (para m├║ltiplos recibos)
        
    Returns:
        Dicion├írio com dados melhorados
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Procurar tabelas na p├ígina
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    # Procurar pela tabela de produtos
                    header_found = False
                    header_row_idx = -1
                    
                    for idx, row in enumerate(table):
                        if row and any(cell and ('DESCRI├ç├âO' in str(cell).upper() or 'QTD' in str(cell).upper() or 'V.UNIT├üRIO' in str(cell).upper() or 'V.UNITARIO' in str(cell).upper()) for cell in row):
                            header_found = True
                            header_row_idx = idx
                            break
                    
                    if header_found and header_row_idx >= 0:
                        # Encontrar colunas relevantes
                        header_row = table[header_row_idx]
                        desc_col = -1
                        qtd_col = -1
                        valor_col = -1
                        
                        for col_idx, cell in enumerate(header_row):
                            if cell:
                                cell_str = str(cell).upper()
                                if 'DESCRI├ç├âO' in cell_str or 'PRODUTO' in cell_str:
                                    desc_col = col_idx
                                elif 'QTD' in cell_str:
                                    qtd_col = col_idx
                                elif 'V.UNIT├üRIO' in cell_str or 'V.UNITARIO' in cell_str or 'UNIT├üRIO' in cell_str or 'UNITARIO' in cell_str:
                                    valor_col = col_idx
                        
                        # Extrair produtos das linhas ap├│s o cabe├ºalho
                        if desc_col >= 0 or qtd_col >= 0 or valor_col >= 0:
                            produtos_encontrados = []
                            
                            for row_idx in range(header_row_idx + 1, len(table)):
                                row = table[row_idx]
                                if not row:
                                    continue
                                
                                # Verificar se ├® linha de total (n├úo adicionar)
                                row_text = ' '.join([str(cell) for cell in row if cell]).upper()
                                if 'TOTAL' in row_text or 'MERCADORIAS' in row_text:
                                    continue
                                
                                # Extrair dados da linha
                                descricao = ''
                                qtd = ''
                                valor = ''
                                
                                # Tentar extrair descri├º├úo da coluna de descri├º├úo ou primeira coluna
                                if desc_col >= 0 and desc_col < len(row) and row[desc_col]:
                                    descricao = str(row[desc_col]).strip()
                                elif len(row) > 0 and row[0]:
                                    first_cell = str(row[0]).strip()
                                    # Verificar se primeira c├®lula n├úo ├® num├®rica
                                    if first_cell and not re.match(r'^[\d.,\s]+$', first_cell):
                                        descricao = first_cell
                                
                                # Extrair quantidade
                                if qtd_col >= 0 and qtd_col < len(row) and row[qtd_col]:
                                    qtd = str(row[qtd_col]).strip()
                                
                                # Extrair valor unit├írio
                                if valor_col >= 0 and valor_col < len(row) and row[valor_col]:
                                    valor = str(row[valor_col]).strip()
                                
                                # Se n├úo encontrou descri├º├úo na linha atual, verificar linhas anteriores
                                if not descricao or len(descricao) < 10:
                                    # Verificar at├® 3 linhas anteriores
                                    for prev_idx in range(max(header_row_idx + 1, row_idx - 3), row_idx):
                                        prev_row = table[prev_idx]
                                        if prev_row:
                                            # Verificar se linha anterior n├úo foi processada como produto
                                            prev_row_text = ' '.join([str(cell) for cell in prev_row if cell])
                                            if prev_row_text and not re.search(r'([A-Z]{2,3})\s+([\d.,]+)\s+([\d.,]+)', prev_row_text):
                                                if desc_col >= 0 and desc_col < len(prev_row) and prev_row[desc_col]:
                                                    prev_desc = str(prev_row[desc_col]).strip()
                                                    if prev_desc and len(prev_desc) > 10 and 'TOTAL' not in prev_desc.upper():
                                                        descricao = prev_desc
                                                        break
                                                elif len(prev_row) > 0 and prev_row[0]:
                                                    prev_first = str(prev_row[0]).strip()
                                                    if prev_first and len(prev_first) > 10 and not re.match(r'^[\d.,\s]+$', prev_first):
                                                        descricao = prev_first
                                                        break
                                
                                # Verificar se quantidade ou valor s├úo n├║meros v├ílidos
                                qtd_valid = qtd and (qtd.replace(',', '').replace('.', '').replace(' ', '').isdigit() or any(c.isdigit() for c in qtd))
                                valor_valid = valor and (valor.replace(',', '').replace('.', '').replace(' ', '').isdigit() or any(c.isdigit() for c in valor))
                                
                                # Se encontrou quantidade ou valor v├ílidos, ├® um produto
                                if qtd_valid or valor_valid:
                                    # Filtrar linhas de total
                                    if 'TOTAL' not in descricao.upper() and 'MERCADORIAS' not in descricao.upper():
                                        produto = {
                                            'descricao': descricao if descricao else f'Produto {len(produtos_encontrados) + 1}',
                                            'quantidade': qtd,
                                            'valor_unitario': valor
                                        }
                                        produtos_encontrados.append(produto)
                            
                            # Se encontrou produtos na tabela, usar apenas se n├úo houver produtos extra├¡dos do texto
                            # ou se a tabela encontrou mais produtos COM VALORES UNIT├üRIOS (mais confi├ível)
                            if produtos_encontrados:
                                produtos_texto = data.get('produtos', [])
                                
                                logger.debug(f"=== _enhance_with_tables: Produtos encontrados ===")
                                logger.debug(f"  Produtos do TEXTO: {len(produtos_texto)}")
                                for pidx, p in enumerate(produtos_texto, 1):
                                    logger.debug(f"    Texto {pidx}: Desc='{p.get('descricao', '')[:50]}', Qtd='{p.get('quantidade', '')}', Valor='{p.get('valor_unitario', '')}'")
                                
                                logger.debug(f"  Produtos da TABELA: {len(produtos_encontrados)}")
                                for pidx, p in enumerate(produtos_encontrados, 1):
                                    logger.debug(f"    Tabela {pidx}: Desc='{p.get('descricao', '')[:50]}', Qtd='{p.get('quantidade', '')}', Valor='{p.get('valor_unitario', '')}'")
                                
                                # Validar qualidade dos produtos: contar produtos com valor unitário
                                produtos_texto_com_valor = sum(1 for p in produtos_texto if p.get('valor_unitario', '').strip())
                                produtos_tabela_com_valor = sum(1 for p in produtos_encontrados if p.get('valor_unitario', '').strip())
                                
                                # Validar se produtos da tabela têm descrições válidas (sem caracteres duplicados)
                                produtos_tabela_validos = sum(1 for p in produtos_encontrados 
                                                             if not any(c1 == c2 for c1, c2 in zip(p.get('descricao', ''), p.get('descricao', '')[1:]) 
                                                                      if c1.isalpha() and c2.isalpha()))
                                
                                # DECISÃO: Substituir apenas se:
                                # 1. Não há produtos do texto OU
                                # 2. Tabela tem mais produtos COM VALOR UNITÁRIO E descrições válidas
                                deve_substituir = False
                                razao = ""
                                
                                if not produtos_texto:
                                    deve_substituir = True
                                    razao = "Não há produtos do texto"
                                elif produtos_tabela_com_valor > produtos_texto_com_valor and produtos_tabela_validos == len(produtos_encontrados):
                                    deve_substituir = True
                                    razao = f"Tabela tem {produtos_tabela_com_valor} produtos com valor unitário (Texto tem {produtos_texto_com_valor})"
                                elif produtos_texto_com_valor == 0 and produtos_tabela_com_valor > 0 and produtos_tabela_validos == len(produtos_encontrados):
                                    # Texto não tem produtos com valor, tabela tem
                                    deve_substituir = True
                                    razao = f"Texto não tem produtos com valor unitário, tabela tem {produtos_tabela_com_valor}"
                                
                                if deve_substituir:
                                    logger.warning(f"  ⚠ SUBSTITUINDO produtos do TEXTO pelos produtos da TABELA!")
                                    logger.warning(f"    Razão: {razao}")
                                    data['produtos'] = produtos_encontrados
                                else:
                                    logger.debug(f"  ✓ Mantendo produtos do TEXTO (não substituindo pela tabela)")
                                    logger.debug(f"    Razão: Texto tem {produtos_texto_com_valor} produtos com valor, Tabela tem {produtos_tabela_com_valor}")
                                    if produtos_tabela_validos < len(produtos_encontrados):
                                        logger.debug(f"    Tabela tem {len(produtos_encontrados) - produtos_tabela_validos} produtos com descrições inválidas (caracteres duplicados)")
                                # Caso contr├írio, manter produtos do texto (j├í foram extra├¡dos corretamente)
                                break
    except Exception:
        # Se falhar ao extrair tabelas, usar dados do texto
        pass
    
    return data

