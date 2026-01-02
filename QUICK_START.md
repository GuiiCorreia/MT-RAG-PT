# Guia de Início Rápido

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar arquivo .env com chave da API
cat .env
# Deve mostrar: GEMINI_API_KEY=sua_chave_aqui
```

## Executar Tradução

### Teste com 10 itens
```bash
python src/main.py --limit 10
```

### Traduzir 100 itens
```bash
python src/main.py --limit 100
```

### Dataset completo de 500 amostras
```bash
python src/main.py
```

## Verificar Resultados

```bash
# Visualizar arquivo traduzido
head -n 1 data/translated/clapnq_translated_batch.jsonl | python -m json.tool

# Gerar relatório de comparação
python scripts/create_comparison_md.py
```

## Tarefas Comuns

### Retomar tradução interrompida
```bash
# Apenas execute o mesmo comando novamente - retoma automaticamente
python src/main.py --limit 100
```

### Usar modelo diferente
```bash
python src/main.py --model gemini-2.5-pro --limit 50
```

### Ajustar tamanho do batch
```bash
python src/main.py --batch-size 15 --rps 12
```

## Arquivos de Saída

- **Saída principal**: `data/translated/clapnq_translated_batch.jsonl`
- **Relatório de comparação**: `output/reports/comparacao.md`
- **Checkpoints**: `output/checkpoints/` (gerenciado automaticamente)

## Solução de Problemas

### Erro de Chave de API
```bash
# Verificar arquivo .env
cat .env

# Deve conter:
GEMINI_API_KEY=sua_chave_real_aqui
```

### Módulo Não Encontrado
```bash
# Instalar dependências faltantes
pip install langgraph langchain-google-genai

# Ou instalar todas de uma vez
pip install -r requirements.txt
```

### Problemas com Checkpoint
```bash
# Remover checkpoint para começar do zero
rm output/checkpoints/translation_checkpoint.json
```

## Próximos Passos

Consulte `README.md` para documentação completa.
