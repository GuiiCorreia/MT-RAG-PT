# Sistema de Tradução com LangGraph e Gemini 2.5-Flash

## Visão Geral

Sistema de tradução acadêmica de alta qualidade desenvolvido para o dataset SemEval usando:
- **Framework**: LangGraph (orquestração de workflows)
- **Modelo**: Gemini 2.5-Flash (modelo multimodal mais recente do Google)
- **Prompt Engineering**: Técnicas avançadas para tradução acadêmica

## Características Principais

### 1. Arquitetura com LangGraph

O sistema utiliza um **grafo de estados** (StateGraph) com os seguintes nós:

```
[Load Data] → [Translate] → [Should Continue?] → [Save Results]
                    ↑              |
                    └──────────────┘
                    (loop até processar todos)
```

### 2. Prompt Engineering Avançado

O prompt implementa múltiplas técnicas de engenharia de prompt:

- **Role-based prompting**: Persona de tradutor acadêmico especializado
- **Context setting**: Definição do domínio (SemEval, NLP research)
- **Step-by-step instructions**: Instruções detalhadas e organizadas
- **Quality criteria**: Critérios explícitos de avaliação
- **Output format specification**: Schema estruturado com Pydantic
- **Few-shot principles**: Exemplos de decisões de tradução

### 3. Tratamento Robusto de Erros

- **Retry automático**: Até 3 tentativas com exponential backoff
- **Graceful degradation**: Marca itens com erro e continua
- **Logging detalhado**: Rastreamento de progresso e erros
- **Error reporting**: Relatório final com taxa de sucesso

### 4. Controle de Qualidade

Cada tradução inclui:
- `title_pt`: Título traduzido
- `text_pt`: Texto completo traduzido
- `translation_confidence`: Nível de confiança (high/medium/low)
- `translation_notes`: Notas sobre decisões de tradução
- `translation_model`: Modelo utilizado
- `translation_timestamp`: Timestamp da tradução

## Uso

### Tradução Completa da Amostra (500 itens)

```bash
python translate_langgraph.py
```

### Tradução de Teste (primeiros 10 itens)

```bash
python translate_langgraph.py --limit 10 --output test_output.jsonl
```

### Usando Modelo Alternativo

```bash
python translate_langgraph.py --model gemini-2.5-pro
```

### Arquivo Customizado

```bash
python translate_langgraph.py --input meu_dataset.jsonl --output traducao.jsonl
```

## Modelos Disponíveis

Principais modelos recomendados:

| Modelo | Descrição | Uso Recomendado |
|--------|-----------|-----------------|
| `gemini-2.5-flash` | Rápido e eficiente | **Recomendado** - Melhor custo-benefício |
| `gemini-2.5-pro` | Alta qualidade | Traduções críticas ou complexas |
| `gemini-2.0-flash` | Versão anterior flash | Alternativa estável |

## Exemplo de Tradução

### Original (Inglês)
**Title**: Jack the Giant Slayer

**Text**: Jack the Giant Slayer (previously titled Jack the Giant Killer) is a 2013 American heroic fantasy adventure film based on the British fairy tales "Jack the Giant Killer" and "Jack and the Beanstalk". The film is directed by Bryan Singer with a screenplay written by Darren Lemke, Christopher McQuarrie and Dan Studney and stars Nicholas Hoult, Eleanor Tomlinson, Stanley Tucci, Ian McShane, Bill Nighy, and Ewan McGregor...

### Traduzido (Português Brasileiro)
**Título**: Jack the Giant Slayer

**Texto**: Jack the Giant Slayer (anteriormente intitulado Jack the Giant Killer) é um filme americano de aventura e fantasia heroica de 2013, baseado nos contos de fadas britânicos "Jack the Giant Killer" e "Jack and the Beanstalk". O filme é dirigido por Bryan Singer, com roteiro escrito por Darren Lemke, Christopher McQuarrie e Dan Studney, e estrelado por Nicholas Hoult, Eleanor Tomlinson, Stanley Tucci, Ian McShane, Bill Nighy e Ewan McGregor...

**Confiança**: high

## Diretrizes de Tradução Implementadas

O sistema segue rigorosas diretrizes acadêmicas:

1. **Fidelidade Semântica**
   - Preserva significado exato e nuances
   - Mantém densidade informacional
   - Mesmo nível de especificidade

2. **Tratamento Terminológico**
   - Nomes próprios preservados
   - Termos técnicos padronizados
   - Entidades nomeadas mantidas

3. **Qualidade Linguística**
   - Registro formal acadêmico
   - Gramática correta do português brasileiro
   - Tom objetivo e enciclopédico

4. **Preservação Estrutural**
   - Mesma estrutura de parágrafos
   - Fluxo informacional mantido
   - Ênfase preservada

## Métricas de Performance

Teste realizado (2 itens):
- **Taxa de sucesso**: 100%
- **Tempo médio por item**: ~10.5 segundos
- **Confiança média**: high
- **Erros**: 0

## Estrutura do Código

### Componentes Principais

```
translate_langgraph.py
├── TranslationConfig       # Configuração do sistema
├── TranslationOutput       # Schema Pydantic para saída
├── TranslationState        # Estado do workflow LangGraph
├── create_translation_prompt()  # Gerador de prompt avançado
├── load_data_node()        # Nó: carregamento de dados
├── translate_node()        # Nó: tradução com Gemini
├── save_results_node()     # Nó: salvamento de resultados
└── build_translation_graph()   # Construção do grafo
```

## Para o Paper

### Citação do Modelo

```
Modelo: Gemini 2.5 Flash
Desenvolvedor: Google DeepMind
API Version: v1beta
Data de Acesso: Dezembro 2025
```

### Descrição do Prompt (para Metodologia)

O prompt de tradução implementa uma abordagem multi-componente que inclui:
1) definição explícita de papel (expert academic translator), 2) contextualização
do domínio (NLP research, SemEval), 3) instruções passo-a-passo organizadas em
cinco categorias (fidelidade semântica, tratamento terminológico, qualidade
linguística, preservação estrutural, adaptação cultural), 4) critérios de
qualidade mensuráveis (acurácia, fluência, consistência, completude, registro
acadêmico), e 5) especificação de formato de saída estruturado com validação
via Pydantic schema.

### Técnicas de Engenharia de Prompt

As seguintes técnicas foram aplicadas:
- Role-based prompting (Wei et al., 2022)
- Chain-of-thought prompting (Kojima et al., 2022)
- Structured output specification (OpenAI, 2024)
- Few-shot learning principles (Brown et al., 2020)
- Domain-specific contextualization

## Troubleshooting

### Erro: "GEMINI_API_KEY not found"
Solução: Verifique se o arquivo `.env` contém a chave API

### Erro: "Model not found"
Solução: Use `python check_models_langchain.py` para listar modelos disponíveis

### Tradução lenta
Solução: O modelo Gemini tem rate limits. O delay de 0.5s entre requisições é intencional

## Próximos Passos

Para traduzir a amostra completa de 500 itens:

```bash
python translate_langgraph.py --output clapnq_sample_500_translated_final.jsonl
```

Tempo estimado: ~87 minutos (500 × 10.5 segundos)

---

**Desenvolvido para pesquisa SemEval**
**Framework**: LangGraph v1.0.0a4
**Modelo**: Gemini 2.5-Flash
**Data**: Dezembro 2025
