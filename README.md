# MT-RAG-PT: Tradução de Dataset de RAG Multi-Turno para Português

> Projeto opensource de tradução do dataset SemEval CLAPNQ para português brasileiro usando LangGraph e Gemini 2.5-Flash

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)
[![Academic](https://img.shields.io/badge/Context-Academic%20Research-blue.svg)](https://github.com/GuiiCorreia/MT-RAG-PT)

---

## 🎓 Contexto Acadêmico

Este projeto faz parte de uma **dissertação de mestrado** focada em processamento de linguagem natural e recuperação de informação aumentada (RAG) para o português brasileiro.

**Objetivo**: Criar um dataset de alta qualidade em português brasileiro para pesquisas em **RAG Multi-Turno**, contribuindo para a democratização de recursos de NLP em língua portuguesa.

**Por que isso é importante?**
- A maioria dos datasets de RAG está em inglês
- Recursos de qualidade em português brasileiro são escassos
- Pesquisadores brasileiros precisam de dados localizados para suas pesquisas
- Este projeto é 100% **open source** para beneficiar toda a comunidade acadêmica

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pipeline de Tradução](#pipeline-de-tradução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Uso](#uso)
- [Configuração](#configuração)
- [Resultados](#resultados)
- [Detalhes Técnicos](#detalhes-técnicos)

---

## 🎯 Visão Geral

Este projeto implementa um sistema de tradução de alto desempenho e pronto para produção para datasets acadêmicos de NLP. Traduz o **dataset SemEval CLAPNQ** (Conversational Long Answer Passage iN Question answering) do inglês para o português brasileiro usando modelos de IA avançados e melhores práticas de engenharia de software.

### O que é RAG Multi-Turno?

**RAG (Retrieval-Augmented Generation)** é uma técnica que combina recuperação de informação com geração de texto. **Multi-turno** refere-se a conversas com múltiplas interações, onde o contexto de perguntas anteriores é importante para responder perguntas subsequentes.

O dataset CLAPNQ contém:
- Passagens de texto longas e complexas
- Perguntas e respostas contextualizadas
- Metadados estruturados (IDs, URLs, títulos)
- Ideal para treinar e avaliar sistemas de QA conversacional

### Características Principais

- ✅ **Processamento em Batch**: Traduz 10 itens por requisição para throughput otimizado
- ✅ **Rate Limiting**: 9 requisições/segundo configuráveis para respeitar limites da API
- ✅ **Checkpoint/Resume**: Salvamento automático e retomada em caso de interrupção
- ✅ **Mecanismo de Retry**: Retry com backoff exponencial (até 3 tentativas)
- ✅ **Salvamento Progressivo**: Sem perda de dados em caso de erros
- ✅ **Prompts Avançados**: Engenharia de prompt para qualidade acadêmica
- ✅ **Arquitetura Limpa**: Código modular, manutenível e escalável

### Performance

- **Modelo**: Gemini 2.5-Flash
- **Taxa de Sucesso**: 90%+ nos testes
- **Velocidade**: ~0.3 itens/segundo (10.5s por batch de 10 itens)
- **Qualidade**: Traduções de alta confiança com fidelidade semântica

---

## 🏗️ Arquitetura

### Design do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                   PIPELINE DE TRADUÇÃO                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ENTRADA: Dataset em Inglês (clapnq_sample_500.jsonl)      │
│  Formato: {_id, id, url, text, title}                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSADOR DE BATCH                       │
│  • Agrupa itens (10 por batch)                             │
│  • Aplica rate limiting (9 req/s)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 MOTOR DE TRADUÇÃO                            │
│  ┌─────────────────────────────────────────────┐            │
│  │  1. Carrega Prompt definido                  │            │
│  │  2. Envia para Gemini 2.5-Flash via LangChain│           │
│  │  3. Parseia Resposta JSON                   │            │
│  │  4. Valida e Mescla com Original            │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              RETRY E TRATAMENTO DE ERROS                     │
│  • Backoff exponencial (2^n segundos)                       │
│  • Até 3 tentativas de retry                                │
│  • Degradação graciosa em caso de falha                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              CHECKPOINT E SALVAMENTO PROGRESSIVO             │
│  • Salva a cada 5 batches                                   │
│  • Retoma do último checkpoint ao reiniciar                 │
│  • Append progressivo no arquivo de saída                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SAÍDA: Dataset Traduzido                                   │
│  Formato: {_id, id, url, text, title, title_pt, text_pt}   │
└─────────────────────────────────────────────────────────────┘
```

### Grafo LangGraph

```
                    ┌──────────────────┐
                    │   ESTADO INICIAL │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   load_data      │  Carrega JSONL
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ create_batches   │  Cria batches
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  check_resume    │  Verifica checkpoint
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
              ┌────▶│   translate      │  Traduz batch
              │     └────────┬─────────┘
              │              │
              │              ▼
              │     ┌──────────────────┐
              │     │  save_progress   │  Salva itens
              │     └────────┬─────────┘
              │              │
              │              ▼
              │     ┌──────────────────┐
              │     │   checkpoint     │  Salva checkpoint
              │     └────────┬─────────┘
              │              │
              │              ▼
              │        ┌────────────┐
              │        │ Continuar? │
              │        └──┬──────┬──┘
              │           │      │
              └───────────┘      │ Finalizar
                    Sim          │
                                 ▼
                        ┌──────────────────┐
                        │    finalize      │  Limpa e finaliza
                        └────────┬─────────┘
                                 │
                                 ▼
                             [ FIM ]
```

---

## 🔄 Pipeline de Tradução

### Fase 1: Carregamento de Dados
```python
Arquivo de Entrada → Parse JSONL → Extração de Itens → Criação de Batches
```

### Fase 2: Tradução em Batch
```python
Para cada batch:
  1. Criar prompt com engenharia avançada
  2. Enviar para Gemini via LangChain
  3. Parsear e validar resposta JSON
  4. Mesclar traduções com dados originais
  5. Tratar erros com mecanismo de retry
```

### Fase 3: Controle de Qualidade
```python
• Validar fidelidade semântica
• Preservar elementos estruturais (\n, formatação)
• Verificar níveis de confiança
• Marcar erros para revisão
```

### Fase 4: Geração de Saída
```python
Dados Traduzidos → Pós-processamento → Múltiplos Formatos de Saída
```

---

## 📁 Estrutura do Projeto

```
SemEval-novo/
│
├── config/                      # Gerenciamento de configuração
│   └── settings.py              # Configurações centralizadas
│
├── src/                         # Código fonte
│   ├── main.py                  # Ponto de entrada principal
│   └── translation_agent.py     # Agente LangGraph com StateGraph
│
├── prompts/                     # Prompts engenhados
│   └── translation_prompt.py   # Prompts para tradução acadêmica
│
├── scripts/                     # Scripts utilitários
│   ├── create_comparison_md.py # Gerar relatório de comparação
│   ├── create_pt_br_dataset.py # Criar dataset PT-BR
│   ├── extract_translations.py # Extrair traduções válidas
│   ├── fix_newlines_pt_br.py   # Corrigir preservação de quebras de linha
│   └── check_models_langchain.py # Verificar modelos disponíveis
│
├── data/                        # Diretório de dados
│   ├── original/                # Datasets originais
│   │   └── clapnq.jsonl        # Dataset completo
│   ├── samples/                 # Amostras de datasets
│   │   └── clapnq_sample_500.jsonl
│   └── translated/              # Saídas traduzidas
│       ├── clapnq_translated_batch.jsonl
│       ├── clapnq_pt_br.jsonl
│       └── clapnq_sample_500_translated.jsonl
│
├── output/                      # Saídas geradas
│   ├── reports/                 # Relatórios de análise
│   │   ├── comparacao.md       # Comparação EN vs PT
│   │   └── clapnq_sample_500_translated.md
│   └── checkpoints/            # Checkpoints para retomada
│
├── .env                         # Variáveis de ambiente (chaves API)
├── requirements.txt             # Dependências Python
├── README.md                    # Este arquivo
└── QUICK_START.md              # Guia de início rápido
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Chave de API do Gemini

### Configuração

```bash
# 1. Clone ou navegue até o diretório do projeto
cd SemEval-novo

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure a chave de API
echo "GEMINI_API_KEY=sua_chave_aqui" > .env

# 4. Verifique a instalação
python scripts/check_models_langchain.py
```

---

## 💻 Uso

### Tradução Básica

Traduzir primeiros 100 itens:
```bash
python src/main.py --limit 100
```

### Tradução do Dataset Completo

Traduzir todas as 500 amostras:
```bash
python src/main.py --input data/samples/clapnq_sample_500.jsonl --output data/translated/saida.jsonl
```

### Opções Avançadas

```bash
python src/main.py \
  --input data/samples/clapnq_sample_500.jsonl \
  --output data/translated/saida_customizada.jsonl \
  --batch-size 15 \
  --rps 12 \
  --model gemini-2.5-pro \
  --limit 200
```

### Retomar a partir de Checkpoint

Se interrompido, simplesmente execute o mesmo comando novamente:
```bash
python src/main.py --limit 100
# Retoma automaticamente do último checkpoint
```

### Gerar Relatório de Comparação

```bash
python scripts/create_comparison_md.py
# Gera output/reports/comparacao.md
```

---

## ⚙️ Configuração

### Configurações de Tradução

Edite `config/settings.py`:

```python
@dataclass
class TranslationConfig:
    model_name: str = "gemini-2.5-flash"  # Modelo a usar
    temperature: float = 0.1               # Baixa para consistência
    batch_size: int = 10                   # Itens por requisição
    requests_per_second: int = 9           # Limite de taxa
    max_retries: int = 3                   # Tentativas de retry
    checkpoint_every: int = 5              # Frequência de checkpoint
```

### Engenharia de Prompt

Personalize prompts em `prompts/translation_prompt.py`:

- Modificar diretrizes de tradução
- Ajustar critérios de qualidade
- Alterar formato de saída

---

## 📊 Resultados

### Qualidade da Tradução

| Métrica | Inglês | Português | Diferença |
|---------|--------|-----------|-----------|
| Palavras Médias/Item | 115 | 108 | -7 |
| Caracteres Médios/Item | 590 | 615 | +25 |
| Preservação de Estrutura | ✓ | ✓ | 100% |

### Métricas de Performance

- **Total de Itens Traduzidos**: 90/100 (teste)
- **Taxa de Sucesso**: 90%
- **Tempo Médio por Item**: 10.5 segundos
- **Throughput**: 0.3 itens/segundo
- **Tempo Total**: ~6 minutos para 100 itens

### Indicadores de Qualidade

✅ **Fidelidade Semântica**: Alta - significado preservado
✅ **Terminologia**: Padrão acadêmico mantido
✅ **Nomes Próprios**: Corretamente preservados
✅ **Estrutura**: Quebras de linha e formatação intactas
✅ **Tom**: Estilo formal e enciclopédico

---

## 🔬 Detalhes Técnicos

### Técnicas de Engenharia de Prompt

1. **Prompting Baseado em Papéis**: Estabelece persona de tradutor especialista
2. **Definição de Contexto**: Define domínio acadêmico/pesquisa
3. **Instruções Passo a Passo**: Diretrizes claras e organizadas
4. **Princípios Few-Shot**: Exemplos implícitos nas instruções
5. **Critérios de Qualidade**: Métricas de avaliação explícitas
6. **Saída Estruturada**: Validação de schema Pydantic

### Estratégia de Tratamento de Erros

```python
Tentar Tradução
  ├─ Sucesso → Salvar e Continuar
  ├─ Falha → Retry (tentativa 1)
  │   ├─ Sucesso → Salvar e Continuar
  │   └─ Falha → Retry (tentativa 2)
  │       ├─ Sucesso → Salvar e Continuar
  │       └─ Falha → Retry (tentativa 3)
  │           ├─ Sucesso → Salvar e Continuar
  │           └─ Falha → Marcar Erro e Continuar
```

### Implementação de Rate Limiting

- **Estratégia**: Algoritmo token bucket
- **Taxa**: 9 requisições/segundo
- **Delay**: 111ms entre batches
- **Tratamento de Burst**: Sleep adaptativo baseado no tempo real do batch

### Sistema de Checkpoint

- **Frequência**: A cada 5 batches
- **Dados Salvos**: Número do batch, contadores, timestamp, config
- **Lógica de Retomada**: Pula batches processados, continua do último+1
- **Limpeza**: Remove checkpoint após conclusão bem-sucedida

---

## 📖 Citação

Se você usar este dataset traduzido ou o sistema de tradução em sua pesquisa, por favor cite:

```bibtex
@software{mt_rag_pt_2025,
  title={MT-RAG-PT: Tradução de Dataset de RAG Multi-Turno para Português},
  author={Guilherme Correia},
  year={2025},
  url={https://github.com/GuiiCorreia/MT-RAG-PT},
  description={Projeto opensource de tradução do dataset SemEval CLAPNQ para português brasileiro},
  model={Gemini 2.5-Flash},
  framework={LangGraph},
  note={Dissertação de Mestrado}
}
```

---

## 📝 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo LICENSE para detalhes.

**Este é um projeto 100% open source!** Sinta-se livre para usar, modificar e distribuir conforme necessário.

---

## 🤝 Contribuindo

**Contribuições são muito bem-vindas!** Este é um projeto acadêmico opensource e toda ajuda é apreciada.

Como contribuir:

1. **Fork** o repositório
2. Crie uma **branch de feature** (`git checkout -b feature/MinhaContribuicao`)
3. **Commit** suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/MinhaContribuicao`)
5. Abra um **Pull Request**

### Áreas onde você pode contribuir:

- Melhorias nos prompts de tradução
- Otimizações de performance
- Suporte para outros modelos de IA
- Documentação e tutoriais
- Análise de qualidade das traduções
- Testes e validação
- Correções de bugs

---

## 📧 Contato

**Guilherme Correia**
- GitHub: [@GuiiCorreia](https://github.com/GuiiCorreia)
- Repositório: [MT-RAG-PT](https://github.com/GuiiCorreia/MT-RAG-PT)

Para dúvidas, sugestões ou problemas, por favor abra uma [issue no repositório](https://github.com/GuiiCorreia/MT-RAG-PT/issues).

---

## 🌟 Agradecimentos

Este projeto é parte de uma dissertação de mestrado e visa contribuir para a comunidade de NLP em português brasileiro. Agradecemos a todos que contribuírem para tornar recursos de IA mais acessíveis em nossa língua.

---

**Desenvolvido com dedicação para a Pesquisa Acadêmica em NLP 🇧🇷**
**Projeto Open Source - Contribuições são bem-vindas!**
