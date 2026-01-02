from pathlib import Path

content = Path('output/reports/comparacao.html').read_text(encoding='utf-8')
lines = content.split('\n')

print(f'Total de linhas: {len(lines)}')
print('\nUltimas 10 linhas:')
for l in lines[-10:]:
    print(l)

# Verificar se tem todos os elementos necessários
has_header = '<header>' in content
has_footer = '</footer>' in content
has_toc = 'toc' in content
has_prompt = 'get_single_translation_prompt' in content
item_count = content.count('<!-- Item ')

print(f'\n\nVerificacao:')
print(f'  Header: {has_header}')
print(f'  Footer: {has_footer}')
print(f'  TOC (Indice): {has_toc}')
print(f'  Prompt incluido: {has_prompt}')
print(f'  Total de items: {item_count}')
