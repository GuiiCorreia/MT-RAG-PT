# -*- coding: utf-8 -*-
"""
Script para gerar HTML completo com todas as traduções
"""

import re
from pathlib import Path

def extract_items_from_markdown(md_file):
    """Extrai itens do markdown de forma robusta"""

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    items = []
    # Dividir por separador ---
    sections = content.split('\n---\n')

    for section in sections:
        if '## Item' not in section:
            continue

        try:
            # Número do item
            num_match = re.search(r'## Item (\d+)', section)
            if not num_match:
                continue
            item_num = num_match.group(1)

            # ID
            id_match = re.search(r'\*\*ID\*\*: `([^`]+)`', section)
            if not id_match:
                continue
            item_id = id_match.group(1)

            # Títulos - formato tabela markdown
            title_lines = section.split('### Título / Title')[1].split('### Texto / Text')[0]
            title_rows = [l.strip() for l in title_lines.split('\n') if l.strip().startswith('|') and '---' not in l]

            if len(title_rows) >= 2:
                # Segunda linha tem os valores
                title_vals = [c.strip() for c in title_rows[1].split('|') if c.strip()]
                if len(title_vals) >= 2:
                    title_en = title_vals[0]
                    title_pt = title_vals[1]
                else:
                    continue
            else:
                continue

            # Texto original (entre "#### 🇬🇧 Original (Inglês)" e "#### 🇧🇷 Tradução")
            en_parts = section.split('#### 🇬🇧 Original (Inglês)')
            if len(en_parts) < 2:
                continue
            en_section = en_parts[1].split('#### 🇧🇷 Tradução (Português)')[0]
            text_en = en_section.strip()

            # Texto traduzido (entre "#### 🇧🇷 Tradução (Português)" e "#### 📊 Estatísticas")
            pt_parts = section.split('#### 🇧🇷 Tradução (Português)')
            if len(pt_parts) < 2:
                continue
            pt_section = pt_parts[1].split('#### 📊 Estatísticas')[0]
            text_pt = pt_section.strip()

            # Estatísticas
            stats_section = section.split('#### 📊 Estatísticas')[1] if '#### 📊 Estatísticas' in section else ''

            # Extrair valores das estatísticas
            words_match = re.search(r'\| Palavras \| (\d+) \| (\d+) \| ([+-]?\d+)', stats_section)
            chars_match = re.search(r'\| Caracteres \| (\d+) \| (\d+) \| ([+-]?\d+)', stats_section)
            lines_match = re.search(r'\| Quebras de linha \| (\d+) \| (\d+) \| ([+-]?\d+)', stats_section)

            if not (words_match and chars_match and lines_match):
                continue

            item = {
                'number': item_num,
                'id': item_id,
                'title_en': title_en,
                'title_pt': title_pt,
                'text_en': text_en,
                'text_pt': text_pt,
                'stats': {
                    'words_en': words_match.group(1),
                    'words_pt': words_match.group(2),
                    'words_diff': words_match.group(3),
                    'chars_en': chars_match.group(1),
                    'chars_pt': chars_match.group(2),
                    'chars_diff': chars_match.group(3),
                    'lines_en': lines_match.group(1),
                    'lines_pt': lines_match.group(2),
                    'lines_diff': lines_match.group(3),
                }
            }

            items.append(item)

        except Exception as e:
            print(f"Erro ao processar item: {e}")
            continue

    return items


def get_diff_class(diff):
    """Retorna classe CSS baseada na diferença"""
    try:
        d = int(diff)
        if d > 0:
            return 'diff-positive'
        elif d < 0:
            return 'diff-negative'
        else:
            return 'diff-neutral'
    except:
        return 'diff-neutral'


def escape_html(text):
    """Escapa caracteres HTML"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    print("Iniciando geracao do HTML...")

    # Extrair itens
    md_path = Path('output/reports/comparacao.md')
    items = extract_items_from_markdown(md_path)
    print(f"Total de itens extraidos: {len(items)}")

    if len(items) == 0:
        print("ERRO: Nenhum item foi extraido!")
        return

    # Ler prompt
    prompt_path = Path('prompts/translation_prompt.py')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    # Extrair apenas o conteúdo da string do prompt get_single_translation_prompt
    # Primeiro encontrar a função
    func_match = re.search(
        r'def get_single_translation_prompt\(.*?\):(.*?)(?=\ndef |\Z)',
        prompt_content,
        re.DOTALL
    )

    if func_match:
        func_content = func_match.group(1)
        # Agora extrair o prompt dentro desta função
        prompt_match = re.search(r'prompt = f"""(.*?)"""', func_content, re.DOTALL)
        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            # Substituir variáveis por placeholders mais legíveis
            prompt_text = prompt_text.replace('{title}', '[título do texto]')
            prompt_text = prompt_text.replace('{text}', '[conteúdo do texto]')
            prompt_code = escape_html(prompt_text)
        else:
            prompt_code = "Prompt não encontrado na função"
    else:
        prompt_code = "Função get_single_translation_prompt não encontrada"

    # Gerar TOC
    toc_items = '\n'.join([
        f'                    <li><a href="#item{item["number"]}">{item["number"]}. {escape_html(item["title_en"])}</a></li>'
        for item in items
    ])

    # Gerar HTML dos itens
    items_html = []
    for item in items:
        diff_words = get_diff_class(item['stats']['words_diff'])
        diff_chars = get_diff_class(item['stats']['chars_diff'])
        diff_lines = get_diff_class(item['stats']['lines_diff'])

        item_html = f'''
            <!-- Item {item['number']} -->
            <div class="item" id="item{item['number']}">
                <div class="item-header">
                    <div class="item-number">Item {item['number']} de {len(items)}</div>
                    <div class="item-id">ID: {item['id']}</div>
                </div>

                <div class="title-comparison">
                    <table>
                        <thead>
                            <tr>
                                <th>🇬🇧 Inglês (EN)</th>
                                <th>🇧🇷 Português (PT-BR)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{escape_html(item['title_en'])}</td>
                                <td>{escape_html(item['title_pt'])}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="content-section">
                    <div class="language-block">
                        <div class="language-header">
                            <span class="flag">🇬🇧</span>
                            Original (Inglês)
                        </div>
                        <div class="text-content">
{escape_html(item['text_en'])}
                        </div>
                    </div>

                    <div class="language-block">
                        <div class="language-header">
                            <span class="flag">🇧🇷</span>
                            Tradução (Português)
                        </div>
                        <div class="text-content">
{escape_html(item['text_pt'])}
                        </div>
                    </div>
                </div>

                <div class="stats-section">
                    <h4>📊 Estatísticas</h4>
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>Métrica</th>
                                <th>Inglês</th>
                                <th>Português</th>
                                <th>Diferença</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Palavras</td>
                                <td>{item['stats']['words_en']}</td>
                                <td>{item['stats']['words_pt']}</td>
                                <td class="{diff_words}">{item['stats']['words_diff']}</td>
                            </tr>
                            <tr>
                                <td>Caracteres</td>
                                <td>{item['stats']['chars_en']}</td>
                                <td>{item['stats']['chars_pt']}</td>
                                <td class="{diff_chars}">{item['stats']['chars_diff']}</td>
                            </tr>
                            <tr>
                                <td>Quebras de linha</td>
                                <td>{item['stats']['lines_en']}</td>
                                <td>{item['stats']['lines_pt']}</td>
                                <td class="{diff_lines}">{item['stats']['lines_diff']}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>'''

        items_html.append(item_html)

    all_items_html = '\n'.join(items_html)

    # Template HTML (continuação no próximo bloco devido ao tamanho)
    html_part1 = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparação de Traduções - EN vs PT-BR - SemEval-2025 Task 8</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .info-section {
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #667eea;
        }

        .info-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .info-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }

        .info-card h3 {
            color: #667eea;
            font-size: 1.1em;
            margin-bottom: 10px;
        }

        .info-card p {
            color: #666;
            margin-bottom: 8px;
            line-height: 1.6;
        }

        .info-card a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            word-break: break-all;
        }

        .info-card a:hover {
            text-decoration: underline;
        }

        .summary {
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #667eea;
        }

        .summary h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .summary-item {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .summary-item h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .summary-item p {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }

        .prompt-section {
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #28a745;
        }

        .prompt-section h2 {
            color: #28a745;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        .prompt-section p {
            color: #666;
            margin-bottom: 10px;
        }

        .prompt-section ul {
            margin-bottom: 15px;
        }

        .prompt-section pre {
            background: white;
            padding: 25px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #28a745;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            max-height: 600px;
            overflow-y: auto;
        }

        .prompt-section code {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.8;
            color: #2d3748;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .prompt-section pre::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        .prompt-section pre::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 5px;
        }

        .prompt-section pre::-webkit-scrollbar-thumb {
            background: #28a745;
            border-radius: 5px;
        }

        .prompt-section pre::-webkit-scrollbar-thumb:hover {
            background: #218838;
        }

        .items-container {
            padding: 30px;
        }

        .item {
            margin-bottom: 50px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .item:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }

        .item-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }

        .item-number {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .item-id {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            opacity: 0.8;
        }

        .title-comparison {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 2px solid #dee2e6;
        }

        .title-comparison table {
            width: 100%;
            border-collapse: collapse;
        }

        .title-comparison th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        .title-comparison td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }

        .content-section {
            padding: 20px;
        }

        .language-block {
            margin-bottom: 25px;
        }

        .language-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }

        .flag {
            font-size: 1.5em;
        }

        .text-content {
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .stats-section {
            background: #e9ecef;
            padding: 20px;
            border-top: 2px solid #dee2e6;
        }

        .stats-section h4 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .stats-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 5px;
            overflow: hidden;
        }

        .stats-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        .stats-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }

        .stats-table tr:last-child td {
            border-bottom: none;
        }

        .diff-positive {
            color: #28a745;
            font-weight: bold;
        }

        .diff-negative {
            color: #dc3545;
            font-weight: bold;
        }

        .diff-neutral {
            color: #6c757d;
        }

        footer {
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }

        footer p {
            margin: 5px 0;
        }

        footer a {
            color: #667eea;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        .toc {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }

        .toc h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .toc ul {
            list-style: none;
            column-count: 3;
            column-gap: 20px;
        }

        .toc li {
            margin-bottom: 8px;
        }

        .toc a {
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .toc a:hover {
            color: #764ba2;
            text-decoration: underline;
        }

        @media (max-width: 992px) {
            .toc ul {
                column-count: 2;
            }
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }

            .summary-grid, .info-grid {
                grid-template-columns: 1fr;
            }

            .stats-table {
                font-size: 0.9em;
            }

            .toc ul {
                column-count: 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Comparação de Traduções</h1>
            <p>SemEval-2025 Task 8: CLAPNQ Dataset</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Inglês (EN) ➜ Português Brasileiro (PT-BR)</p>
        </header>

        <div class="info-section">
            <h2>ℹ️ Informações do Projeto</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>🎯 SemEval-2025 Task 8</h3>
                    <p><strong>RAG Multi-Turno em Inglês e Português</strong></p>
                    <p>Este projeto faz parte da Task 8 do SemEval-2025, focada em sistemas de Retrieval-Augmented Generation (RAG) multi-turno para conversas em múltiplos idiomas.</p>
                    <p>A tarefa visa desenvolver sistemas capazes de manter contexto em conversas multi-turno enquanto recuperam informações relevantes de uma base de conhecimento.</p>
                </div>
                <div class="info-card">
                    <h3>📁 Repositório GitHub</h3>
                    <p><strong>Código Fonte Completo</strong></p>
                    <p><a href="https://github.com/GuiiCorreia/SemEval-2025/tree/main/corpora" target="_blank">github.com/GuiiCorreia/SemEval-2025/tree/main/corpora</a></p>
                    <p>Sistema completo desenvolvido com LangGraph e Google Gemini 2.5-Flash, incluindo processamento em batch, checkpoints e recuperação de erros.</p>
                </div>
                <div class="info-card">
                    <h3>🤖 Modelo e Tecnologia</h3>
                    <p><strong>Google Gemini 2.5-Flash</strong></p>
                    <p>Tradução acadêmica com prompt engineering avançado para preservação semântica, terminológica e estrutural.</p>
                </div>
            </div>
        </div>

        <div class="summary">
            <h2>📈 Resumo Geral</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>Total de Itens</h3>
                    <p>''' + str(len(items)) + '''</p>
                </div>
                <div class="summary-item">
                    <h3>Idioma Fonte</h3>
                    <p>🇬🇧 Inglês</p>
                </div>
                <div class="summary-item">
                    <h3>Idioma Alvo</h3>
                    <p>🇧🇷 Português BR</p>
                </div>
                <div class="summary-item">
                    <h3>Modelo</h3>
                    <p>Gemini 2.5-Flash</p>
                </div>
            </div>
        </div>

        <div class="prompt-section">
            <h2>🔧 Prompt de Tradução Utilizado</h2>
            <p><strong>Função:</strong> <code>get_single_translation_prompt</code> | <strong>Arquivo:</strong> <code>prompts/translation_prompt.py</code></p>
            <p style="margin-top: 10px;">Este prompt implementa técnicas avançadas de engenharia de prompt para garantir traduções acadêmicas de alta qualidade:</p>
            <ul style="margin-left: 20px; color: #666;">
                <li><strong>Role-based prompting:</strong> Define persona de tradutor especialista acadêmico</li>
                <li><strong>Instruções estruturadas:</strong> Guidelines organizadas em seções claras</li>
                <li><strong>Critérios de qualidade:</strong> Métricas objetivas para avaliação</li>
                <li><strong>Formato de saída estruturado:</strong> Especificação JSON com campos obrigatórios</li>
                <li><strong>Preservação semântica e terminológica:</strong> Regras explícitas para manter significado</li>
            </ul>
            <p style="margin-top: 15px; margin-bottom: 10px;"><strong>Conteúdo completo do prompt:</strong></p>
            <pre><code>''' + prompt_code + '''</code></pre>
        </div>

        <div class="items-container">
            <div class="toc">
                <h3>📑 Índice - Todos os ''' + str(len(items)) + ''' Itens</h3>
                <ul>
''' + toc_items + '''
                </ul>
            </div>

''' + all_items_html + '''
        </div>

        <footer>
            <p><strong>SemEval-2025 Task 8 - CLAPNQ Dataset Translation Project</strong></p>
            <p>Desenvolvido por Guilherme Correia</p>
            <p><a href="https://github.com/GuiiCorreia/SemEval-2025" target="_blank">GitHub Repository</a></p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                Documento gerado automaticamente • ''' + str(len(items)) + ''' itens • EN → PT-BR • Google Gemini 2.5-Flash
            </p>
        </footer>
    </div>
</body>
</html>'''

    # Salvar HTML
    output_path = Path('output/reports/comparacao.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_part1)

    file_size = output_path.stat().st_size / 1024
    print(f"\nSucesso!")
    print(f"Arquivo: {output_path}")
    print(f"Tamanho: {file_size:.2f} KB")

if __name__ == '__main__':
    main()
