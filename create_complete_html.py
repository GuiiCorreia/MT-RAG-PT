"""
Script para gerar HTML completo com TODAS as 90 traduções
"""

import re
import json
from pathlib import Path

def parse_markdown_items(md_content):
    """Parse markdown para extrair todos os itens de tradução"""

    items = []

    # Dividir por separador ---
    sections = md_content.split('---')

    for section in sections:
        # Tentar extrair item
        item_match = re.search(r'## Item (\d+)', section)
        if not item_match:
            continue

        item_num = item_match.group(1)

        # Extrair ID
        id_match = re.search(r'\*\*ID\*\*: `([^`]+)`', section)
        if not id_match:
            continue
        item_id = id_match.group(1)

        # Extrair títulos da tabela
        title_match = re.search(r'\| ([^|]+) \| ([^|]+) \|\n\|\s*-+\s*\|\s*-+\s*\|\n\| ([^|]+) \| ([^|]+) \|', section)
        if not title_match:
            continue

        title_en = title_match.group(3).strip()
        title_pt = title_match.group(4).strip()

        # Extrair texto original
        text_en_match = re.search(r'#### 🇬🇧 Original \(Inglês\)\n\n(.*?)\n\n#### 🇧🇷 Tradução \(Português\)', section, re.DOTALL)
        if not text_en_match:
            continue
        text_en = text_en_match.group(1).strip()

        # Extrair texto traduzido
        text_pt_match = re.search(r'#### 🇧🇷 Tradução \(Português\)\n\n(.*?)\n\n#### 📊 Estatísticas', section, re.DOTALL)
        if not text_pt_match:
            continue
        text_pt = text_pt_match.group(1).strip()

        # Extrair estatísticas
        stats_match = re.search(
            r'\| Palavras \| (\d+) \| (\d+) \| ([+-]?\d+) \|.*?' +
            r'\| Caracteres \| (\d+) \| (\d+) \| ([+-]?\d+) \|.*?' +
            r'\| Quebras de linha \| (\d+) \| (\d+) \| ([+-]?\d+) \|',
            section, re.DOTALL
        )

        if not stats_match:
            continue

        item = {
            'number': item_num,
            'id': item_id,
            'title_en': title_en,
            'title_pt': title_pt,
            'text_en': text_en,
            'text_pt': text_pt,
            'stats': {
                'words_en': stats_match.group(1),
                'words_pt': stats_match.group(2),
                'words_diff': stats_match.group(3),
                'chars_en': stats_match.group(4),
                'chars_pt': stats_match.group(5),
                'chars_diff': stats_match.group(6),
                'lines_en': stats_match.group(7),
                'lines_pt': stats_match.group(8),
                'lines_diff': stats_match.group(9)
            }
        }
        items.append(item)

    return items

def get_diff_class(diff_str):
    """Retorna classe CSS baseada na diferença"""
    diff = int(diff_str)
    if diff > 0:
        return 'diff-positive'
    elif diff < 0:
        return 'diff-negative'
    else:
        return 'diff-neutral'

def create_item_html(item, total):
    """Cria HTML para um item individual"""

    # Criar ID para âncora
    item_id = f"item{item['number']}"

    html = f'''
            <!-- Item {item['number']} -->
            <div class="item" id="{item_id}">
                <div class="item-header">
                    <div class="item-number">Item {item['number']} de {total}</div>
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
                                <td>{item['title_en']}</td>
                                <td>{item['title_pt']}</td>
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
                            {item['text_en']}
                        </div>
                    </div>

                    <div class="language-block">
                        <div class="language-header">
                            <span class="flag">🇧🇷</span>
                            Tradução (Português)
                        </div>
                        <div class="text-content">
                            {item['text_pt']}
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
                                <td class="{get_diff_class(item['stats']['words_diff'])}">{item['stats']['words_diff']}</td>
                            </tr>
                            <tr>
                                <td>Caracteres</td>
                                <td>{item['stats']['chars_en']}</td>
                                <td>{item['stats']['chars_pt']}</td>
                                <td class="{get_diff_class(item['stats']['chars_diff'])}">{item['stats']['chars_diff']}</td>
                            </tr>
                            <tr>
                                <td>Quebras de linha</td>
                                <td>{item['stats']['lines_en']}</td>
                                <td>{item['stats']['lines_pt']}</td>
                                <td class="{get_diff_class(item['stats']['lines_diff'])}">{item['stats']['lines_diff']}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
'''
    return html

def create_toc(items):
    """Cria índice com todos os itens"""

    toc_html = '<ul>\n'
    for item in items:
        item_id = f"item{item['number']}"
        toc_html += f'                    <li><a href="#{item_id}">{item["number"]}. {item["title_en"]}</a></li>\n'
    toc_html += '                </ul>'

    return toc_html

def main():
    # Ler markdown completo
    md_path = Path('output/reports/comparacao.md')
    print(f"Lendo arquivo markdown: {md_path}")

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print(f"Tamanho do arquivo: {len(md_content)} caracteres")

    # Parse dos itens
    print("Parseando itens...")
    items = parse_markdown_items(md_content)
    print(f"Itens encontrados: {len(items)}")

    if len(items) == 0:
        print("ERRO: Nenhum item foi encontrado! Verificando padrão...")
        # Tentar encontrar padrão alternativo
        sample = md_content[:2000]
        print(f"Primeiros 2000 caracteres:\n{sample}")
        return

    # Ler prompt
    prompt_path = Path('prompts/translation_prompt.py')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    # Extrair função get_single_translation_prompt
    prompt_match = re.search(
        r'(def get_single_translation_prompt\(.*?\):\s*""".*?""".*?return prompt)',
        prompt_content,
        re.DOTALL
    )

    if prompt_match:
        prompt_code = prompt_match.group(1)
        # Escapar HTML
        prompt_code = prompt_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    else:
        prompt_code = "# Prompt não encontrado"

    # Criar TOC
    toc_html = create_toc(items)

    # Criar HTML dos itens
    items_html = ''
    for item in items:
        items_html += create_item_html(item, len(items))

    # Template HTML completo
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparação de Traduções - EN vs PT-BR - SemEval-2025 Task 8</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .info-section {{
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #667eea;
        }}

        .info-section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}

        .info-card h3 {{
            color: #667eea;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}

        .info-card p {{
            color: #666;
            margin-bottom: 8px;
            line-height: 1.6;
        }}

        .info-card a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            word-break: break-all;
        }}

        .info-card a:hover {{
            text-decoration: underline;
        }}

        .summary {{
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #667eea;
        }}

        .summary h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .summary-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .summary-item h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}

        .summary-item p {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}

        .prompt-section {{
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #28a745;
            margin-bottom: 0;
        }}

        .prompt-section h2 {{
            color: #28a745;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .prompt-section p {{
            color: #666;
            margin-bottom: 15px;
        }}

        .prompt-section pre {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #28a745;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .prompt-section code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.5;
            color: #333;
        }}

        .items-container {{
            padding: 30px;
        }}

        .item {{
            margin-bottom: 50px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }}

        .item-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }}

        .item-number {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}

        .item-id {{
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            opacity: 0.8;
        }}

        .title-comparison {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 2px solid #dee2e6;
        }}

        .title-comparison table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .title-comparison th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        .title-comparison td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}

        .content-section {{
            padding: 20px;
        }}

        .language-block {{
            margin-bottom: 25px;
        }}

        .language-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }}

        .flag {{
            font-size: 1.5em;
        }}

        .text-content {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .stats-section {{
            background: #e9ecef;
            padding: 20px;
            border-top: 2px solid #dee2e6;
        }}

        .stats-section h4 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 5px;
            overflow: hidden;
        }}

        .stats-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        .stats-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }}

        .stats-table tr:last-child td {{
            border-bottom: none;
        }}

        .diff-positive {{
            color: #28a745;
            font-weight: bold;
        }}

        .diff-negative {{
            color: #dc3545;
            font-weight: bold;
        }}

        .diff-neutral {{
            color: #6c757d;
        }}

        footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}

        footer p {{
            margin: 5px 0;
        }}

        footer a {{
            color: #667eea;
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            .summary-grid {{
                grid-template-columns: 1fr;
            }}

            .stats-table {{
                font-size: 0.9em;
            }}

            .toc ul {{
                column-count: 1;
            }}
        }}

        .toc {{
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}

        .toc h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .toc ul {{
            list-style: none;
            column-count: 3;
            column-gap: 20px;
        }}

        .toc li {{
            margin-bottom: 8px;
        }}

        .toc a {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .toc a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        @media (max-width: 992px) {{
            .toc ul {{
                column-count: 2;
            }}
        }}

        @media (max-width: 576px) {{
            .toc ul {{
                column-count: 1;
            }}
        }}
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
                    <p>Este projeto faz parte da Task 8 do SemEval-2025, focada em sistemas de Retrieval-Augmented Generation (RAG) multi-turno para conversas em múltiplos idiomas, especificamente inglês e português brasileiro.</p>
                    <p>A tarefa visa desenvolver e avaliar sistemas capazes de manter contexto em conversas de múltiplos turnos enquanto recuperam e utilizam informações relevantes de uma base de conhecimento.</p>
                </div>

                <div class="info-card">
                    <h3>📁 Repositório no GitHub</h3>
                    <p><strong>Código Fonte Completo</strong></p>
                    <p><a href="https://github.com/GuiiCorreia/SemEval-2025/tree/main/corpora" target="_blank">https://github.com/GuiiCorreia/SemEval-2025/tree/main/corpora</a></p>
                    <p>Sistema completo de tradução desenvolvido com LangGraph e Google Gemini 2.5-Flash, incluindo pipeline de processamento em batch, sistema de checkpoints e recuperação automática de erros.</p>
                </div>

                <div class="info-card">
                    <h3>🤖 Modelo e Tecnologia</h3>
                    <p><strong>Google Gemini 2.5-Flash</strong></p>
                    <p>Tradução acadêmica especializada utilizando prompt engineering avançado para preservação semântica, terminológica e estrutural. O sistema implementa técnicas de role-based prompting, definição de critérios de qualidade e especificação rigorosa de formato de saída.</p>
                </div>
            </div>
        </div>

        <div class="summary">
            <h2>📈 Resumo Geral</h2>

            <div class="summary-grid">
                <div class="summary-item">
                    <h3>Total de Itens</h3>
                    <p>{len(items)}</p>
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
                    <h3>Modelo de Tradução</h3>
                    <p>Gemini 2.5-Flash</p>
                </div>
            </div>
        </div>

        <div class="prompt-section">
            <h2>🔧 Prompt de Tradução Utilizado</h2>
            <p><strong>Função:</strong> <code>get_single_translation_prompt</code></p>
            <p><strong>Arquivo:</strong> <code>prompts/translation_prompt.py</code></p>
            <p>Este prompt implementa técnicas avançadas de engenharia de prompt para garantir traduções acadêmicas de alta qualidade, incluindo:</p>
            <ul style="margin-left: 20px; margin-bottom: 15px; color: #666;">
                <li>Role-based prompting (persona de tradutor especialista)</li>
                <li>Instruções detalhadas passo a passo</li>
                <li>Definição clara de critérios de qualidade</li>
                <li>Especificação de formato de saída estruturado</li>
                <li>Diretrizes para preservação semântica e terminológica</li>
            </ul>
            <pre><code>{prompt_code}</code></pre>
        </div>

        <div class="items-container">
            <div class="toc">
                <h3>📑 Índice - Todos os {len(items)} Itens</h3>
{toc_html}
            </div>

{items_html}
        </div>

        <footer>
            <p><strong>SemEval-2025 Task 8 - CLAPNQ Dataset Translation Project</strong></p>
            <p>Desenvolvido por Guilherme Correia</p>
            <p><a href="https://github.com/GuiiCorreia/SemEval-2025" target="_blank">GitHub Repository</a></p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                Documento gerado automaticamente • {len(items)} itens • EN → PT-BR • Google Gemini 2.5-Flash
            </p>
        </footer>
    </div>
</body>
</html>'''

    # Salvar HTML
    output_path = Path('output/reports/comparacao.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nHTML gerado com sucesso!")
    print(f"Arquivo: {output_path}")
    print(f"Total de itens: {len(items)}")
    print(f"Tamanho do arquivo: {output_path.stat().st_size / 1024:.2f} KB")

if __name__ == '__main__':
    main()
