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
        raise FileNotFoundError(f"Arquivo n├úo encontrado: {pdf_path}")
    except Exception as e:
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
    # Usar padr├úo mais flex├¡vel para capturar toda a se├º├úo at├® "TOTAL"
    
    # Primeiro, verificar se h├í se├º├úo de produtos neste texto
    # Procurar por "DADOS DO PRODUTO" que vem ANTES de "TOTAL DE MERCADORIAS" ou "TOTAIS" ou "PAGAMENTO"
    produtos_section = re.search(r'DADOS\s+DO\s+PRODUTO.*?(?=TOTAL\s+DE\s+MERCADORIAS|TOTAIS|PAGAMENTO|$)', text, re.IGNORECASE | re.DOTALL)
    
    if produtos_section:
        produtos_text = produtos_section.group(0)
        lines = produtos_text.split('\n')
        
        # Procurar por todas as ocorr├¬ncias de padr├Áes de produto
        # Padr├úo: linha com UNID (2-3 letras) seguido de QTD e V.UNIT├üRIO
        # Pode haver m├║ltiplos produtos na mesma se├º├úo
        
        i = 0
        produtos_encontrados = []
        linhas_processadas = set()  # Evitar processar a mesma linha duas vezes
        produtos_vistos = set()  # Evitar produtos duplicados
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Pular linha se j├í foi processada
            if i in linhas_processadas:
                i += 1
                continue
            
            # Procurar por linha com padr├úo UNID QTD V.UNIT├üRIO
            # Padr├úo mais espec├¡fico: 2-3 letras (UNID), espa├ºo, n├║mero com v├¡rgula/ponto (QTD), espa├ºo, n├║mero com v├¡rgula/ponto (VALOR)
            produto_match = re.search(r'([A-Z]{2,3})\s+([\d.,]+)\s+([\d.,]+)', line)
            
            if produto_match:
                # Verificar se n├úo ├® uma linha de total
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
                
                for j in range(i-1, max(-1, i-6), -1):  # De i-1 at├® i-5, de tr├ís para frente
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
            # Se n├úo encontrou produtos, garantir que a lista est├í vazia
            data['produtos'] = []
    else:
        # Se n├úo encontrou se├º├úo de produtos, garantir que a lista est├í vazia
        data['produtos'] = []
    
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
    if progress_callback:
        progress_callback(0, 0, "Extraindo texto do PDF...")
    text = extract_text_from_pdf(pdf_path, progress_callback)
    
    if progress_callback:
        progress_callback(0, 0, "Processando recibos...")
    
    # Detectar m├║ltiplos recibos (cada recibo come├ºa com "N┬║")
    # Dividir o texto em se├º├Áes de recibos
    receipts = []
    
    # Procurar por todos os n├║meros de recibo no texto
    numero_matches = list(re.finditer(r'N┬║\s*:?\s*(\d+)', text, re.IGNORECASE))
    
    total_recibos = len(numero_matches) if numero_matches else 1
    
    if len(numero_matches) == 0:
        # Nenhum recibo encontrado, tentar processar como um ├║nico recibo
        if progress_callback:
            progress_callback(1, 1, "Processando recibo ├║nico...")
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
            
            # Determinar fim do recibo (in├¡cio do pr├│ximo ou fim do texto)
            if i + 1 < len(numero_matches):
                end_pos = numero_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            # Extrair se├º├úo do recibo - garantir que est├í completamente isolada
            receipt_text = text[start_pos:end_pos]
            
            # Extrair n├║mero do recibo para valida├º├úo
            numero_recibo = match.group(1) if match.groups() else None
            
            # Limpar o texto para garantir que n├úo h├í res├¡duos de outros recibos
            # Mas N├âO remover se ainda n├úo processamos os produtos
            # Apenas remover se encontrarmos claramente o in├¡cio do pr├│ximo recibo
            if i + 1 < len(numero_matches):
                # Procurar por qualquer refer├¬ncia ao pr├│ximo recibo
                next_numero = numero_matches[i+1].group(1)
                # Procurar por padr├Áes que indiquem in├¡cio de novo recibo
                # Mas apenas se vier DEPOIS de "PAGAMENTO" ou "TOTAIS" (fim do recibo atual)
                patterns_to_check = [
                    f"\nN┬║ {next_numero}",
                    f"\nN┬║: {next_numero}",
                    f"\nN┬║{next_numero}",
                ]
                for pattern in patterns_to_check:
                    next_numero_pos = receipt_text.find(pattern)
                    if next_numero_pos > 0:
                        # Verificar se vem depois de indicadores de fim de recibo
                        texto_antes = receipt_text[:next_numero_pos]
                        if any(marker in texto_antes.upper() for marker in ['PAGAMENTO', 'TOTAIS', 'TOTAL DE MERCADORIAS']):
                            receipt_text = receipt_text[:next_numero_pos]
                            break
            
            # Extrair dados do recibo APENAS do texto desta se├º├úo isolada
            # Criar um novo dicion├írio limpo para este recibo
            data = extract_receipt_data(receipt_text)
            
            # Garantir que o n├║mero do recibo est├í correto e for├ºar
            if numero_recibo:
                data['numero'] = numero_recibo
            
            # Validar que os produtos extra├¡dos pertencem a este recibo
            # Se n├úo h├í produtos, garantir que a lista est├í vazia
            if 'produtos' not in data:
                data['produtos'] = []
            
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
            
            # N├âO usar _enhance_with_tables para m├║ltiplos recibos
            # pois pode misturar produtos entre recibos
            # Apenas usar extra├º├úo de texto que j├í est├í isolada por se├º├úo
            
            # Adicionar apenas se tiver dados v├ílidos
            if data.get('numero') or data.get('produtos') or data.get('vendedor'):
                receipts.append(data)
    
    return receipts if receipts else [extract_receipt_data(text)]


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
                            # ou se a tabela encontrou mais produtos (mais confi├ível)
                            if produtos_encontrados:
                                produtos_texto = data.get('produtos', [])
                                # Se tabela encontrou produtos e h├í mais produtos na tabela ou n├úo h├í produtos do texto
                                if len(produtos_encontrados) > len(produtos_texto) or not produtos_texto:
                                    data['produtos'] = produtos_encontrados
                                # Caso contr├írio, manter produtos do texto (j├í foram extra├¡dos corretamente)
                                break
    except Exception:
        # Se falhar ao extrair tabelas, usar dados do texto
        pass
    
    return data

