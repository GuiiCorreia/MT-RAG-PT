"""
Script para gerar HTML a partir do relatório de comparação
"""

import re
from pathlib import Path

def markdown_to_html(md_content):
    """Converte markdown para HTML com formatação bonita"""

    # Substituir headers
    md_content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^## (.*?)$', r'<h2 id="\1">\1</h2>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', md_content, flags=re.MULTILINE)

    # Substituir bold
    md_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_content)

    # Substituir code blocks
    md_content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', md_content, flags=re.DOTALL)

    # Substituir links
    md_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', md_content)

    # Substituir parágrafos (linhas que não são headers)
    lines = md_content.split('\n')
    result = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append('')
        elif stripped.startswith('<h') or stripped.startswith('<pre>'):
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        else:
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)

    if in_paragraph:
        result.append('</p>')

    return '\n'.join(result)

def extract_toc_from_markdown(md_content):
    """Extrai títulos do markdown para criar índice"""
    toc = []
    lines = md_content.split('\n')

    for line in lines:
        # Apenas ## (h2) - itens principais
        if line.startswith('## ') and not line.startswith('###'):
            title = line[3:].strip()
            # Criar ID
            item_id = title.replace(' ', '-').replace('/', '-').lower()
            item_id = re.sub(r'[^\w\-]', '', item_id)
            toc.append({'title': title, 'id': item_id})

    return toc

def main():
    # Ler markdown
    md_path = Path('output/reports/comparacao.md')
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Ler prompt
    prompt_path = Path('prompts/translation_prompt.py')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    # Extrair apenas a função get_single_translation_prompt
    prompt_match = re.search(
        r'def get_single_translation_prompt\(.*?\):\s*""".*?"""(.*?)(?=\ndef |\Z)',
        prompt_content,
        re.DOTALL
    )

    if prompt_match:
        prompt_code = prompt_match.group(0)
    else:
        prompt_code = "# Prompt não encontrado"

    # Extrair índice
    toc = extract_toc_from_markdown(md_content)

    # Criar HTML do índice
    toc_html = '<ul class="toc">\n'
    for item in toc:
        toc_html += f'  <li><a href="#{item["id"]}">{item["title"]}</a></li>\n'
    toc_html += '</ul>'

    # Converter markdown para HTML
    # Ajustar IDs nos headers
    md_with_ids = md_content
    for item in toc:
        original_title = item['title']
        md_with_ids = md_with_ids.replace(
            f"## {original_title}",
            f'<h2 id="{item["id"]}">{original_title}</h2>'
        )

    # Processar o resto do markdown
    html_content = markdown_to_html(md_with_ids)

    # Template HTML
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparação de Traduções - SemEval CLAPNQ Dataset</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary-color: #2563eb;
            --secondary-color: #0ea5e9;
            --success-color: #10b981;
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --code-bg: #f1f5f9;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--background);
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: var(--shadow-lg);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .info-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .info-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary-color);
        }}

        .info-card h3 {{
            color: var(--primary-color);
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}

        .info-card p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}

        .info-card a {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }}

        .info-card a:hover {{
            text-decoration: underline;
        }}

        .sidebar {{
            position: sticky;
            top: 2rem;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            max-height: calc(100vh - 4rem);
            overflow-y: auto;
        }}

        .sidebar h2 {{
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }}

        .toc {{
            list-style: none;
        }}

        .toc li {{
            margin: 0.5rem 0;
        }}

        .toc a {{
            color: var(--text-secondary);
            text-decoration: none;
            display: block;
            padding: 0.5rem;
            border-radius: 6px;
            transition: all 0.2s;
        }}

        .toc a:hover {{
            background: var(--background);
            color: var(--primary-color);
            padding-left: 1rem;
        }}

        .main-layout {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 2rem;
            margin-top: 2rem;
        }}

        .content {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: var(--shadow);
        }}

        .content h2 {{
            color: var(--primary-color);
            font-size: 1.8rem;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--primary-color);
        }}

        .content h3 {{
            color: var(--text-primary);
            font-size: 1.4rem;
            margin: 1.5rem 0 0.8rem 0;
        }}

        .content h4 {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin: 1rem 0 0.5rem 0;
        }}

        .content p {{
            margin: 0.8rem 0;
            color: var(--text-primary);
        }}

        .prompt-section {{
            background: var(--code-bg);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
            border-left: 4px solid var(--success-color);
        }}

        .prompt-section h2 {{
            color: var(--success-color);
            border-bottom: 3px solid var(--success-color);
        }}

        pre {{
            background: var(--code-bg);
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
            border: 1px solid var(--border-color);
        }}

        code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            color: #d63384;
        }}

        .translation-item {{
            margin: 2rem 0;
            padding: 1.5rem;
            background: var(--background);
            border-radius: 8px;
        }}

        .flag {{
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
            padding: 1rem;
            background: white;
            border-radius: 8px;
        }}

        .stat-item {{
            text-align: center;
            padding: 0.5rem;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .stat-value {{
            color: var(--primary-color);
            font-size: 1.3rem;
            font-weight: 700;
        }}

        .footer {{
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
        }}

        @media (max-width: 1024px) {{
            .main-layout {{
                grid-template-columns: 1fr;
            }}

            .sidebar {{
                position: relative;
                top: 0;
                max-height: none;
            }}
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}

            .info-cards {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Comparação de Traduções</h1>
        <p>SemEval-2025 Task 8: CLAPNQ Dataset - English to Brazilian Portuguese</p>
    </div>

    <div class="container">
        <div class="info-cards">
            <div class="info-card">
                <h3>🎯 SemEval-2025 Task 8</h3>
                <p><strong>RAG Multi-Turno em Inglês e Português</strong></p>
                <p>Este projeto faz parte da Task 8 do SemEval-2025, focada em sistemas de Retrieval-Augmented Generation (RAG) multi-turno para conversas em múltiplos idiomas.</p>
            </div>

            <div class="info-card">
                <h3>📁 Repositório</h3>
                <p><strong>Código Fonte Completo</strong></p>
                <p><a href="https://github.com/GuiiCorreia/SemEval-2025/tree/main/corpora" target="_blank">github.com/GuiiCorreia/SemEval-2025/tree/main/corpora</a></p>
                <p>Sistema completo de tradução usando LangGraph e Google Gemini 2.5-Flash</p>
            </div>

            <div class="info-card">
                <h3>🤖 Modelo de Tradução</h3>
                <p><strong>Google Gemini 2.5-Flash</strong></p>
                <p>Tradução acadêmica especializada com prompt engineering avançado para preservação semântica e terminológica</p>
            </div>
        </div>

        <div class="main-layout">
            <aside class="sidebar">
                <h2>📑 Índice</h2>
                {toc_html}
            </aside>

            <main>
                <div class="content">
                    {html_content}
                </div>

                <div class="prompt-section">
                    <h2>🔧 Prompt de Tradução Utilizado</h2>
                    <p>Função <code>get_single_translation_prompt</code> do arquivo <code>prompts/translation_prompt.py</code></p>
                    <pre><code>{prompt_code}</code></pre>
                </div>
            </main>
        </div>
    </div>

    <footer class="footer">
        <p><strong>SemEval-2025 Task 8 - CLAPNQ Dataset Translation</strong></p>
        <p>Desenvolvido por Guilherme Correia | <a href="https://github.com/GuiiCorreia/SemEval-2025" target="_blank">GitHub Repository</a></p>
        <p>Gerado automaticamente a partir do relatório de comparação</p>
    </footer>
</body>
</html>"""

    # Salvar HTML
    output_path = Path('output/reports/comparacao.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML gerado com sucesso!")
    print(f"Arquivo: {output_path}")
    print(f"Itens no indice: {len(toc)}")

if __name__ == '__main__':
    main()
