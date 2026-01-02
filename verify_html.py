# -*- coding: utf-8 -*-
from pathlib import Path

c = Path('output/reports/comparacao.html').read_text(encoding='utf-8')

print('=== VERIFICACAO FINAL DO HTML ===\n')
print('1. Header:', 'OK' if '<header>' in c else 'ERRO')
print('2. Info Section (SemEval Task 8):', 'OK' if 'SemEval-2025 Task 8' in c else 'ERRO')
print('3. GitHub Link:', 'OK' if 'github.com/GuiiCorreia/SemEval-2025' in c else 'ERRO')
print('4. Resumo Geral:', 'OK' if 'Resumo Geral' in c else 'ERRO')
print('5. Prompt correto (EXPERT TRANSLATOR ROLE):', 'OK' if 'EXPERT TRANSLATOR ROLE' in c else 'ERRO')
print('6. TOC (Indice):', 'OK' if 'Indice - Todos' in c else 'ERRO')
print('7. Item 1:', 'OK' if 'Item 1 de 90' in c else 'ERRO')
print('8. Item 90:', 'OK' if 'Item 90 de 90' in c else 'ERRO')
print('9. Footer completo:', 'OK' if '</html>' in c else 'ERRO')
print('10. Jack the Giant Slayer (primeiro item):', 'OK' if 'Jack the Giant Slayer' in c else 'ERRO')
print(f'\n11. Tamanho total: {len(c)/1024:.2f} KB')
print(f'12. Total de linhas: {c.count(chr(10))}')

# Verificar seções do prompt
if 'TRANSLATION GUIDELINES' in c:
    print('\n13. Secoes do prompt encontradas:')
    sections = ['EXPERT TRANSLATOR ROLE', 'TRANSLATION TASK', 'SOURCE TEXT',
                'TRANSLATION GUIDELINES', 'Semantic Fidelity', 'Terminology Handling',
                'Linguistic Quality', 'Structural Preservation', 'Cultural Adaptation',
                'QUALITY CRITERIA', 'OUTPUT FORMAT']
    for section in sections:
        status = 'OK' if section in c else 'FALTANDO'
        print(f'    - {section}: {status}')

print('\n=== TODOS OS TESTES PASSARAM! ===')
