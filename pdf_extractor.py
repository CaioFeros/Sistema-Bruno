"""
Módulo para extração de dados de recibos de venda de PDFs.
"""
import pdfplumber
import re
from typing import Dict, List, Optional


def _remove_duplicate_chars(text: str) -> str:
    """
    Remove caracteres duplicados consecutivos (ex: "TTIIRR" -> "TIR").
    
    Args:
        text: Texto com possíveis caracteres duplicados
        
    Returns:
        Texto limpo
    """
    if not text:
        return text
    
    # Detectar padrão de duplicação: caracteres repetidos em pares
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
    Remove frases duplicadas na descrição.
    Foca em remover duplicatas completas de frases, não palavras individuais.
    
    Args:
        text: Texto com possíveis frases duplicadas
        
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
    # Verificar se há uma sequência de palavras que se repete
    result_words = []
    i = 0
    
    while i < len(words):
        word = words[i]
        result_words.append(word)
        
        # Verificar se as próximas palavras formam uma frase que já apareceu
        # Procurar por duplicatas de 3-8 palavras
        found_duplicate = False
        for phrase_len in range(3, min(9, len(words) - i)):
            if i + phrase_len * 2 > len(words):
                break
            
            phrase1 = ' '.join(words[i:i+phrase_len])
            phrase2 = ' '.join(words[i+phrase_len:i+phrase_len*2])
            
            # Se as duas frases são iguais, é uma duplicata
            if phrase1.upper() == phrase2.upper() and len(phrase1) > 10:
                # Pular a segunda ocorrência
                i += phrase_len * 2
                found_duplicate = True
                break
        
        if not found_duplicate:
            i += 1
    
    return ' '.join(result_words)


def _clean_product_description(descricao: str) -> str:
    """
    Limpa a descrição do produto, removendo códigos e informações extras.
    Mantém apenas a parte principal: NOME + DOSAGEM + FORMA
    
    Exemplo:
        "TIRZEPATIDE 50 MG/2ML - SOL INJ (FRASCO) L- 2092369271700 C086A-B250901 FAB 09/2025 VAL- 09/2027 ANVISA"
        -> "TIRZEPATIDE 50 MG/2ML"
    
    Args:
        descricao: Descrição completa do produto
        
    Returns:
        Descrição limpa
    """
    if not descricao:
        return descricao
    
    # Padrões que indicam fim da descrição principal
    # Procurar por: "L-", "C086A-", "FAB", "VAL-", "ANVISA", códigos longos
    patterns_to_stop = [
        r'\s+L-\s+\d+',  # "L- 2092369271700"
        r'\s+C\d{3}[A-Z]?-[A-Z]\d+',  # "C086A-B250901"
        r'\s+FAB\s+\d{2}/\d{4}',  # "FAB 09/2025"
        r'\s+VAL-\s+\d{2}/\d{4}',  # "VAL- 09/2027"
        r'\s+ANVISA',  # "ANVISA"
        r'\s+\d{12,}',  # Códigos numéricos longos
    ]
    
    # Encontrar a primeira ocorrência de qualquer padrão de fim
    min_pos = len(descricao)
    for pattern in patterns_to_stop:
        match = re.search(pattern, descricao, re.IGNORECASE)
        if match:
            min_pos = min(min_pos, match.start())
    
    # Se encontrou um padrão, cortar a descrição
    if min_pos < len(descricao):
        descricao = descricao[:min_pos].strip()
    
    # Remover traços finais e espaços extras
    descricao = descricao.rstrip('-').strip()
    descricao = re.sub(r'\s+', ' ', descricao)
    
    return descricao


def extract_text_from_pdf(pdf_path: str, progress_callback=None) -> str:
    """
    Extrai todo o texto de um arquivo PDF.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        progress_callback: Função callback(opcional) chamada com (página_atual, total_páginas) durante o processamento
        
    Returns:
        String com todo o texto extraído do PDF
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado
        Exception: Se houver erro ao processar o PDF
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                # Chamar callback de progresso se fornecido
                if progress_callback:
                    progress_callback(page_num, total_pages)
        
        return text
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
    except Exception as e:
        raise Exception(f"Erro ao processar PDF: {str(e)}")


def extract_receipt_data(text: str) -> Dict:
    """
    Extrai dados estruturados de um recibo a partir do texto extraído.
    
    Args:
        text: Texto completo extraído do PDF
        
    Returns:
        Dicionário com os dados extraídos:
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
    
    # Extrair Nº do recibo - pode aparecer como "Nº 0000004510" ou "Nº: 0000004510"
    numero_match = re.search(r'Nº\s*:?\s*(\d+)', text, re.IGNORECASE)
    if numero_match:
        data['numero'] = numero_match.group(1).strip()
    
    # Extrair Vendedor - "Vendedor: NOME"
    vendedor_match = re.search(r'Vendedor:\s*([^\n]+)', text, re.IGNORECASE)
    if vendedor_match:
        data['vendedor'] = vendedor_match.group(1).strip()
    
    # Extrair Nome/Razão Social - pode estar na linha seguinte após "NOME/RAZÃO SOCIAL"
    # Dividir texto em linhas para busca mais precisa
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Procurar linha com "NOME/RAZÃO SOCIAL"
        if re.search(r'NOME/RAZÃO\s+SOCIAL', line, re.IGNORECASE):
            # Verificar se o nome está na mesma linha (com dois pontos)
            same_line_match = re.search(r'NOME/RAZÃO\s+SOCIAL\s*:\s*(.+)', line, re.IGNORECASE)
            if same_line_match:
                cliente_nome = same_line_match.group(1).strip()
                data['cliente'] = cliente_nome
                break
            else:
                # Procurar na próxima linha não vazia
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    # Ignorar linhas vazias e linhas que são outros campos
                    if next_line and 'NOME FANTASIA' not in next_line.upper() and 'CNPJ' not in next_line.upper() and 'EMAIL' not in next_line.upper():
                        # Se a linha tem conteúdo e não parece ser outro campo
                        if len(next_line) > 3:
                            data['cliente'] = next_line
                            break
                if data['cliente']:
                    break
    
    # Extrair produtos
    # Procurar pela seção "DADOS DO PRODUTO" APENAS dentro deste recibo
    # Usar padrão mais flexível para capturar toda a seção até "TOTAL"
    
    # Primeiro, verificar se há seção de produtos neste texto
    # Procurar por "DADOS DO PRODUTO" que vem ANTES de "TOTAL DE MERCADORIAS" ou "TOTAIS" ou "PAGAMENTO"
    produtos_section = re.search(r'DADOS\s+DO\s+PRODUTO.*?(?=TOTAL\s+DE\s+MERCADORIAS|TOTAIS|PAGAMENTO|$)', text, re.IGNORECASE | re.DOTALL)
    
    if produtos_section:
        produtos_text = produtos_section.group(0)
        lines = produtos_text.split('\n')
        
        # Procurar por todas as ocorrências de padrões de produto
        # Padrão: linha com UNID (2-3 letras) seguido de QTD e V.UNITÁRIO
        # Pode haver múltiplos produtos na mesma seção
        
        i = 0
        produtos_encontrados = []
        linhas_processadas = set()  # Evitar processar a mesma linha duas vezes
        produtos_vistos = set()  # Evitar produtos duplicados
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Pular linha se já foi processada
            if i in linhas_processadas:
                i += 1
                continue
            
            # Procurar por linha com padrão UNID QTD V.UNITÁRIO
            # Padrão mais específico: 2-3 letras (UNID), espaço, número com vírgula/ponto (QTD), espaço, número com vírgula/ponto (VALOR)
            produto_match = re.search(r'([A-Z]{2,3})\s+([\d.,]+)\s+([\d.,]+)', line)
            
            if produto_match:
                # Verificar se não é uma linha de total
                if 'TOTAL' in line.upper() or 'MERCADORIAS' in line.upper():
                    linhas_processadas.add(i)  # Marcar como processada
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
                
                # Validar que quantidade e valor contêm números
                # Aceitar se pelo menos um deles tem números
                qtd_clean = qtd.replace(',', '').replace('.', '').replace(' ', '')
                valor_clean = valor.replace(',', '').replace('.', '').replace(' ', '')
                
                # Verificar se tem pelo menos um dígito
                tem_numero = any(c.isdigit() for c in qtd_clean) or any(c.isdigit() for c in valor_clean)
                
                if not tem_numero:
                    linhas_processadas.add(i)  # Marcar como processada
                    i += 1
                    continue
                
                # Verificar se esta linha não é apenas uma descrição de produto (sem dados numéricos válidos)
                # Se a linha contém apenas texto descritivo sem padrão de produto válido, pular
                if len(line) > 50 and not any(c.isdigit() for c in qtd) and not any(c.isdigit() for c in valor):
                    # Pode ser uma linha de descrição, não um produto
                    linhas_processadas.add(i)
                    i += 1
                    continue
                
                # Procurar descrição nas linhas anteriores
                # IMPORTANTE: Não pegar linhas que já foram usadas como descrição de outro produto
                descricao_parts = []
                linhas_usadas_como_descricao = set()
                
                # Verificar linha atual (pode ter parte da descrição antes do UNID)
                before_unid = line[:produto_match.start()].strip()
                if before_unid and len(before_unid) > 5:
                    # Verificar se não é só números ou código
                    if not re.match(r'^[\d.,\s]+$', before_unid):
                        before_clean = before_unid.replace(' ', '').replace('-', '')
                        if not re.match(r'^\d{10,15}$', before_clean):
                            # Verificar se não é código alfanumérico curto
                            if not re.match(r'^[A-Z0-9]{8,15}$', before_clean):
                                descricao_parts.append(before_unid)
                
                # Verificar linhas anteriores (até 5 linhas para trás para capturar descrições longas)
                # IMPORTANTE: Processar de trás para frente (da mais próxima para a mais distante)
                # para garantir que pegamos a primeira linha válida (mais próxima do produto)
                linhas_validas = []
                linha_nome_produto = None  # Prioridade máxima: linha que começa com nome de produto
                
                for j in range(i-1, max(-1, i-6), -1):  # De i-1 até i-5, de trás para frente
                    if j < 0:
                        break
                    
                    # NÃO pegar linhas que já foram processadas como produto
                    if j in linhas_processadas:
                        continue
                    
                    # NÃO pegar linhas que já foram usadas como descrição de outro produto
                    if j in linhas_usadas_como_descricao:
                        continue
                    
                    prev_line = lines[j].strip()
                    
                    if not prev_line:
                        continue
                    
                    # NÃO pegar linhas que são números de recibo (4 dígitos)
                    if re.match(r'^\d{4}$', prev_line):
                        continue
                    
                    # Ignorar cabeçalhos
                    if any(keyword in prev_line.upper() for keyword in ['CÓDIGO', 'DESCRIÇÃO DOS PRODUTOS', 'UNID', 'QTD', 'V.UNITÁRIO']):
                        continue
                    
                    # Ignorar se é uma linha de produto (tem padrão UNID QTD VALOR)
                    if re.search(r'([A-Z]{2,3})\s+([\d.,]+)\s+([\d.,]+)', prev_line):
                        continue
                    
                    # Ignorar linhas que são apenas códigos
                    prev_clean = prev_line.replace(' ', '').replace('-', '')
                    if re.match(r'^\d{10,15}$', prev_clean) or re.match(r'^[A-Z0-9]{8,20}$', prev_clean):
                        continue
                    
                    prev_upper = prev_line.upper()
                    
                    # IGNORAR primeiro: linhas que são claramente códigos de produto (FAB, VAL, ANVISA, etc.)
                    # Isso evita que essas linhas sejam consideradas como descrição
                    if any(keyword in prev_upper for keyword in ['FAB', 'VAL-', 'VAL ', 'ANVISA']):
                        continue
                    
                    # Ignorar linhas que começam com "L-" seguido de código
                    if re.match(r'^L-\s*[A-Z0-9]', prev_line):
                        continue
                    
                    # PRIMEIRA PRIORIDADE: Linhas que começam com nome de produto conhecido
                    # Esta é a descrição mais importante - parar aqui se encontrarmos
                    eh_nome_produto = any(prev_upper.startswith(nome) for nome in ['TIRZEPATIDE', 'SEMAGLUTIDA', 'SEMAGLUTIDE', 'CANETA'])
                    
                    if eh_nome_produto:
                        # Encontrou linha que começa com nome de produto - usar APENAS esta como descrição
                        linha_nome_produto = prev_line
                        linhas_usadas_como_descricao.add(j)
                        break  # Parar busca - encontrou a descrição correta
                    
                    # Segunda prioridade: Linhas com palavras-chave de produto (mas não nome direto)
                    if len(prev_line) > 10:
                        # Deve conter palavras-chave de produto (MG, ML) E não ser código
                        tem_palavra_chave = any(keyword in prev_upper for keyword in ['MG', 'ML', 'SOL', 'INJ', 'FRASCO'])
                        
                        if tem_palavra_chave:
                            # Adicionar à lista de linhas válidas (da mais próxima para a mais distante)
                            if prev_line not in linhas_validas:
                                linhas_validas.append(prev_line)
                                linhas_usadas_como_descricao.add(j)
                
                # Se encontrou linha que começa com nome de produto, usar APENAS ela
                if linha_nome_produto:
                    descricao_parts = [linha_nome_produto]  # Substituir todas as outras partes
                elif linhas_validas:
                    # Se não encontrou nome de produto direto, usar linhas válidas encontradas
                    # Adicionar na ordem correta (primeira linha encontrada primeiro)
                    # Como processamos de trás para frente, a primeira linha válida (mais próxima) está no início da lista
                    for linha_valida in linhas_validas:
                        if linha_valida not in descricao_parts:
                            descricao_parts.insert(0, linha_valida)
                
                # Combinar partes da descrição
                descricao = ' '.join(descricao_parts).strip()
                descricao = re.sub(r'\s+', ' ', descricao)
                
                # Remover duplicatas de caracteres (problema de extração)
                # Se houver padrão de duplicação (ex: "TTIIRRZZ"), limpar
                descricao = _remove_duplicate_chars(descricao)
                
                # Remover duplicatas de palavras/frases inteiras
                descricao = _remove_duplicate_phrases(descricao)
                
                # Adicionar produto
                if 'TOTAL' not in descricao.upper() and 'MERCADORIAS' not in descricao.upper():
                    # Criar chave única para verificar duplicatas
                    # Usar quantidade e valor para identificar produtos únicos
                    produto_key = f"{qtd}|{valor}|{unid}"
                    
                    # Verificar se já existe um produto com mesma quantidade e valor
                    # (mesmo produto não deve aparecer duas vezes)
                    if produto_key not in produtos_vistos:
                        produto = {
                            'descricao': descricao if descricao else f'Produto {len(produtos_encontrados) + 1}',
                            'quantidade': qtd,
                            'valor_unitario': valor
                        }
                        produtos_encontrados.append(produto)
                        produtos_vistos.add(produto_key)
                        linhas_processadas.add(i)
                    else:
                        # Produto duplicado detectado - pular esta linha
                        linhas_processadas.add(i)
            
            i += 1
        
        # Adicionar todos os produtos encontrados
        if produtos_encontrados:
            data['produtos'] = produtos_encontrados
        else:
            # Se não encontrou produtos, garantir que a lista está vazia
            data['produtos'] = []
    else:
        # Se não encontrou seção de produtos, garantir que a lista está vazia
        data['produtos'] = []
    
    return data


def extract_from_pdf(pdf_path: str, progress_callback=None) -> List[Dict]:
    """
    Função principal para extrair dados de um PDF.
    Suporta múltiplos recibos no mesmo PDF.
    Usa tanto extração de texto quanto de tabelas para maior precisão.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        progress_callback: Função callback(opcional) chamada com (página_atual, total_páginas, mensagem) durante o processamento
        
    Returns:
        Lista de dicionários com os dados extraídos de cada recibo
    """
    if progress_callback:
        progress_callback(0, 0, "Extraindo texto do PDF...")
    text = extract_text_from_pdf(pdf_path, progress_callback)
    
    if progress_callback:
        progress_callback(0, 0, "Processando recibos...")
    
    # Detectar múltiplos recibos (cada recibo começa com "Nº")
    # Dividir o texto em seções de recibos
    receipts = []
    
    # Procurar por todos os números de recibo no texto
    numero_matches = list(re.finditer(r'Nº\s*:?\s*(\d+)', text, re.IGNORECASE))
    
    total_recibos = len(numero_matches) if numero_matches else 1
    
    if len(numero_matches) == 0:
        # Nenhum recibo encontrado, tentar processar como um único recibo
        if progress_callback:
            progress_callback(1, 1, "Processando recibo único...")
        data = extract_receipt_data(text)
        data = _enhance_with_tables(pdf_path, data, progress_callback)
        if data.get('numero') or data.get('produtos'):
            receipts.append(data)
    else:
        # Processar cada recibo separadamente
        for i, match in enumerate(numero_matches):
            if progress_callback:
                progress_callback(i + 1, total_recibos, f"Processando recibo {i + 1} de {total_recibos}...")
            
            start_pos = match.start()
            
            # Determinar fim do recibo (início do próximo ou fim do texto)
            if i + 1 < len(numero_matches):
                end_pos = numero_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            # Extrair seção do recibo - garantir que está completamente isolada
            receipt_text = text[start_pos:end_pos]
            
            # Extrair número do recibo para validação
            numero_recibo = match.group(1) if match.groups() else None
            
            # Limpar o texto para garantir que não há resíduos de outros recibos
            # Mas NÃO remover se ainda não processamos os produtos
            # Apenas remover se encontrarmos claramente o início do próximo recibo
            if i + 1 < len(numero_matches):
                # Procurar por qualquer referência ao próximo recibo
                next_numero = numero_matches[i+1].group(1)
                # Procurar por padrões que indiquem início de novo recibo
                # Mas apenas se vier DEPOIS de "PAGAMENTO" ou "TOTAIS" (fim do recibo atual)
                patterns_to_check = [
                    f"\nNº {next_numero}",
                    f"\nNº: {next_numero}",
                    f"\nNº{next_numero}",
                ]
                for pattern in patterns_to_check:
                    next_numero_pos = receipt_text.find(pattern)
                    if next_numero_pos > 0:
                        # Verificar se vem depois de indicadores de fim de recibo
                        texto_antes = receipt_text[:next_numero_pos]
                        if any(marker in texto_antes.upper() for marker in ['PAGAMENTO', 'TOTAIS', 'TOTAL DE MERCADORIAS']):
                            receipt_text = receipt_text[:next_numero_pos]
                            break
            
            # Extrair dados do recibo APENAS do texto desta seção isolada
            # Criar um novo dicionário limpo para este recibo
            data = extract_receipt_data(receipt_text)
            
            # Garantir que o número do recibo está correto e forçar
            if numero_recibo:
                data['numero'] = numero_recibo
            
            # Validar que os produtos extraídos pertencem a este recibo
            # Se não há produtos, garantir que a lista está vazia
            if 'produtos' not in data:
                data['produtos'] = []
            
            # Validar produtos: garantir que têm dados válidos e não são duplicados
            produtos_validos = []
            produtos_vistos = set()  # Para evitar duplicatas
            
            for produto in data.get('produtos', []):
                # Validar que o produto tem dados válidos
                qtd = produto.get('quantidade', '').strip()
                valor = produto.get('valor_unitario', '').strip()
                desc = produto.get('descricao', '').strip()
                
                # Aceitar produto se tiver quantidade OU valor (descrição pode estar vazia)
                if qtd or valor:
                    # Criar chave única para evitar duplicatas
                    produto_key = f"{desc}|{qtd}|{valor}"
                    if produto_key not in produtos_vistos:
                        produtos_validos.append(produto)
                        produtos_vistos.add(produto_key)
            
            data['produtos'] = produtos_validos
            
            # NÃO usar _enhance_with_tables para múltiplos recibos
            # pois pode misturar produtos entre recibos
            # Apenas usar extração de texto que já está isolada por seção
            
            # Adicionar apenas se tiver dados válidos
            if data.get('numero') or data.get('produtos') or data.get('vendedor'):
                receipts.append(data)
    
    return receipts if receipts else [extract_receipt_data(text)]


def _enhance_with_tables(pdf_path: str, data: Dict, text_start: int = 0, text_end: int = None, progress_callback=None) -> Dict:
    """
    Melhora os dados extraídos usando tabelas do PDF quando disponível.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        data: Dicionário com dados já extraídos
        text_start: Posição inicial do texto do recibo (para múltiplos recibos)
        text_end: Posição final do texto do recibo (para múltiplos recibos)
        
    Returns:
        Dicionário com dados melhorados
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Procurar tabelas na página
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    # Procurar pela tabela de produtos
                    header_found = False
                    header_row_idx = -1
                    
                    for idx, row in enumerate(table):
                        if row and any(cell and ('DESCRIÇÃO' in str(cell).upper() or 'QTD' in str(cell).upper() or 'V.UNITÁRIO' in str(cell).upper() or 'V.UNITARIO' in str(cell).upper()) for cell in row):
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
                                if 'DESCRIÇÃO' in cell_str or 'PRODUTO' in cell_str:
                                    desc_col = col_idx
                                elif 'QTD' in cell_str:
                                    qtd_col = col_idx
                                elif 'V.UNITÁRIO' in cell_str or 'V.UNITARIO' in cell_str or 'UNITÁRIO' in cell_str or 'UNITARIO' in cell_str:
                                    valor_col = col_idx
                        
                        # Extrair produtos das linhas após o cabeçalho
                        if desc_col >= 0 or qtd_col >= 0 or valor_col >= 0:
                            produtos_encontrados = []
                            
                            for row_idx in range(header_row_idx + 1, len(table)):
                                row = table[row_idx]
                                if not row:
                                    continue
                                
                                # Verificar se é linha de total (não adicionar)
                                row_text = ' '.join([str(cell) for cell in row if cell]).upper()
                                if 'TOTAL' in row_text or 'MERCADORIAS' in row_text:
                                    continue
                                
                                # Extrair dados da linha
                                descricao = ''
                                qtd = ''
                                valor = ''
                                
                                # Tentar extrair descrição da coluna de descrição ou primeira coluna
                                if desc_col >= 0 and desc_col < len(row) and row[desc_col]:
                                    descricao = str(row[desc_col]).strip()
                                elif len(row) > 0 and row[0]:
                                    first_cell = str(row[0]).strip()
                                    # Verificar se primeira célula não é numérica
                                    if first_cell and not re.match(r'^[\d.,\s]+$', first_cell):
                                        descricao = first_cell
                                
                                # Extrair quantidade
                                if qtd_col >= 0 and qtd_col < len(row) and row[qtd_col]:
                                    qtd = str(row[qtd_col]).strip()
                                
                                # Extrair valor unitário
                                if valor_col >= 0 and valor_col < len(row) and row[valor_col]:
                                    valor = str(row[valor_col]).strip()
                                
                                # Se não encontrou descrição na linha atual, verificar linhas anteriores
                                if not descricao or len(descricao) < 10:
                                    # Verificar até 3 linhas anteriores
                                    for prev_idx in range(max(header_row_idx + 1, row_idx - 3), row_idx):
                                        prev_row = table[prev_idx]
                                        if prev_row:
                                            # Verificar se linha anterior não foi processada como produto
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
                                
                                # Verificar se quantidade ou valor são números válidos
                                qtd_valid = qtd and (qtd.replace(',', '').replace('.', '').replace(' ', '').isdigit() or any(c.isdigit() for c in qtd))
                                valor_valid = valor and (valor.replace(',', '').replace('.', '').replace(' ', '').isdigit() or any(c.isdigit() for c in valor))
                                
                                # Se encontrou quantidade ou valor válidos, é um produto
                                if qtd_valid or valor_valid:
                                    # Filtrar linhas de total
                                    if 'TOTAL' not in descricao.upper() and 'MERCADORIAS' not in descricao.upper():
                                        produto = {
                                            'descricao': descricao if descricao else f'Produto {len(produtos_encontrados) + 1}',
                                            'quantidade': qtd,
                                            'valor_unitario': valor
                                        }
                                        produtos_encontrados.append(produto)
                            
                            # Se encontrou produtos na tabela, usar apenas se não houver produtos extraídos do texto
                            # ou se a tabela encontrou mais produtos (mais confiável)
                            if produtos_encontrados:
                                produtos_texto = data.get('produtos', [])
                                # Se tabela encontrou produtos e há mais produtos na tabela ou não há produtos do texto
                                if len(produtos_encontrados) > len(produtos_texto) or not produtos_texto:
                                    data['produtos'] = produtos_encontrados
                                # Caso contrário, manter produtos do texto (já foram extraídos corretamente)
                                break
    except Exception:
        # Se falhar ao extrair tabelas, usar dados do texto
        pass
    
    return data

