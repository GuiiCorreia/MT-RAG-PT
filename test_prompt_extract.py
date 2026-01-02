import re
from pathlib import Path

# Ler arquivo
prompt_path = Path('prompts/translation_prompt.py')
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_content = f.read()

# Tentar extrair
prompt_match = re.search(
    r'prompt = f"""(.*?)"""',
    prompt_content,
    re.DOTALL
)

if prompt_match:
    prompt_text = prompt_match.group(1).strip()
    print("Prompt extraido com sucesso!")
    print(f"Tamanho: {len(prompt_text)} caracteres")
    print("\nPrimeiros 500 caracteres:")
    print(prompt_text[:500])
else:
    print("Prompt NAO encontrado")
    print("\nTentando encontrar a linha 'prompt = f\"\"\"'...")
    if 'prompt = f"""' in prompt_content:
        print("Linha encontrada no arquivo!")
        idx = prompt_content.find('prompt = f"""')
        print(f"Posicao: {idx}")
        print("Contexto:")
        print(prompt_content[idx:idx+200])
    else:
        print("Linha NAO encontrada no arquivo")
