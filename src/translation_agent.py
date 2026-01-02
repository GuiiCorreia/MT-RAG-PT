"""
LangGraph Translation Agent
===========================
Sistema de tradução usando LangGraph StateGraph
"""

import json
import time
import os
from typing import TypedDict, Annotated, List, Dict, Any
from datetime import datetime
from pathlib import Path
import operator

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import TranslationConfig
from prompts.translation_prompt import get_batch_translation_prompt


# ============================================================================
# Estado do Agente LangGraph
# ============================================================================

class TranslationState(TypedDict):
    """Estado compartilhado entre todos os nós do grafo"""

    # Dados de entrada
    input_file: str
    output_file: str
    items: List[Dict[str, Any]]

    # Processamento
    batches: List[List[Dict]]
    current_batch_num: int
    total_batches: int

    # Resultados
    translated_items: Annotated[List[Dict], operator.add]

    # Estatísticas
    translated_count: int
    error_count: int

    # Checkpoint
    checkpoint_file: str
    should_checkpoint: bool

    # Configuração
    config: TranslationConfig

    # Controle de fluxo
    completed: bool


# ============================================================================
# Nós do Grafo LangGraph
# ============================================================================

def load_data_node(state: TranslationState) -> TranslationState:
    """Nó: Carregar dados do arquivo JSONL"""

    print(f"\n{'='*80}")
    print(f"[NÓ: LOAD_DATA] Carregando dados")
    print(f"{'='*80}")
    print(f"  Arquivo: {state['input_file']}")

    with open(state['input_file'], 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]

    # Aplicar limite se configurado
    limit = getattr(state['config'], 'limit', None)
    if limit:
        items = items[:limit]

    print(f"  Itens carregados: {len(items)}")
    print(f"{'='*80}\n")

    return {
        **state,
        "items": items
    }


def create_batches_node(state: TranslationState) -> TranslationState:
    """Nó: Criar batches de processamento"""

    print(f"[NÓ: CREATE_BATCHES] Criando batches")

    items = state['items']
    batch_size = state['config'].batch_size

    batches = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batches.append(batch)

    total_batches = len(batches)

    print(f"  Total de batches: {total_batches}")
    print(f"  Tamanho do batch: {batch_size}\n")

    return {
        **state,
        "batches": batches,
        "total_batches": total_batches,
        "current_batch_num": 0
    }


def check_resume_node(state: TranslationState) -> TranslationState:
    """Nó: Verificar se deve retomar de checkpoint"""

    checkpoint_file = state.get('checkpoint_file', 'output/checkpoints/translation_checkpoint.json')

    if not state['config'].resume or not os.path.exists(checkpoint_file):
        print(f"[NÓ: CHECK_RESUME] Iniciando do zero\n")
        return {
            **state,
            "current_batch_num": 0,
            "translated_count": 0,
            "error_count": 0
        }

    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)

        print(f"[NÓ: CHECK_RESUME] Checkpoint encontrado")
        print(f"  Último batch: {checkpoint['last_completed_batch']}")
        print(f"  Itens traduzidos: {checkpoint.get('translated_count', 0)}\n")

        return {
            **state,
            "current_batch_num": checkpoint['last_completed_batch'],
            "translated_count": checkpoint.get('translated_count', 0),
            "error_count": checkpoint.get('error_count', 0)
        }
    except Exception as e:
        print(f"[NÓ: CHECK_RESUME] Erro ao carregar checkpoint: {e}")
        print(f"  Iniciando do zero\n")
        return {
            **state,
            "current_batch_num": 0,
            "translated_count": 0,
            "error_count": 0
        }


def translate_batch_node(state: TranslationState) -> TranslationState:
    """Nó: Traduzir batch atual"""

    current = state['current_batch_num']
    batches = state['batches']
    total = state['total_batches']

    # Verificar se há batches para processar
    if current >= total:
        return {
            **state,
            "completed": True
        }

    batch = batches[current]
    batch_num = current + 1  # Display as 1-indexed

    print(f"\n[NÓ: TRANSLATE] Batch {batch_num}/{total}")
    print(f"  Itens no batch: {len(batch)}")

    # Inicializar LLM
    config = state['config']
    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        google_api_key=config.api_key,
        temperature=config.temperature
    )

    # Tentar tradução com retry
    for attempt in range(1, config.max_retries + 1):
        try:
            # Criar prompt
            prompt = get_batch_translation_prompt(batch)

            # Mensagens
            system_msg = SystemMessage(
                content="Você é um tradutor acadêmico especialista para datasets de NLP. "
                        "Traduz inglês para português brasileiro com alta precisão. "
                        "Sempre retorna JSON válido."
            )
            human_msg = HumanMessage(content=prompt)

            # Invocar modelo
            start = time.time()
            response = llm.invoke([system_msg, human_msg])
            elapsed = time.time() - start

            # Parse JSON
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            batch_result = json.loads(content)
            translations = batch_result.get('translations', [])

            # Mesclar com dados originais
            translated_items = []
            trans_dict = {t['item_id']: t for t in translations}

            for original_item in batch:
                item_id = original_item.get('id', 'unknown')
                translation = trans_dict.get(item_id)

                if translation:
                    translated_item = {
                        **original_item,
                        'title_pt': translation.get('title_pt', ''),
                        'text_pt': translation.get('text_pt', ''),
                        'translation_confidence': translation.get('confidence', 'medium'),
                        'translation_model': config.model_name,
                        'translation_timestamp': datetime.now().isoformat(),
                        'batch_number': batch_num
                    }
                    translated_items.append(translated_item)
                else:
                    # Item não traduzido
                    error_item = {
                        **original_item,
                        'title_pt': '[ERROR: NOT_TRANSLATED]',
                        'text_pt': '[ERROR: NOT_TRANSLATED]',
                        'translation_confidence': 'error'
                    }
                    translated_items.append(error_item)

            print(f"  Sucesso em {elapsed:.2f}s")
            print(f"  Traduzidos: {len(translated_items)}/{len(batch)}")

            # Rate limiting
            time.sleep(config.delay_between_requests)

            return {
                **state,
                "translated_items": translated_items,
                "current_batch_num": current + 1,
                "translated_count": state['translated_count'] + len(translated_items),
                "should_checkpoint": (batch_num % config.checkpoint_every == 0)
            }

        except Exception as e:
            if attempt < config.max_retries:
                wait = 2 ** attempt
                print(f"  Erro (tentativa {attempt}): {e}")
                print(f"  Aguardando {wait}s antes de retry...")
                time.sleep(wait)
            else:
                print(f"  Falha após {config.max_retries} tentativas")
                # Criar itens de erro
                error_items = []
                for item in batch:
                    error_item = {
                        **item,
                        'title_pt': '[ERROR]',
                        'text_pt': f'[ERROR: {str(e)}]',
                        'translation_confidence': 'error'
                    }
                    error_items.append(error_item)

                return {
                    **state,
                    "translated_items": error_items,
                    "current_batch_num": current + 1,
                    "error_count": state['error_count'] + len(error_items),
                    "should_checkpoint": (batch_num % config.checkpoint_every == 0)
                }


def save_progress_node(state: TranslationState) -> TranslationState:
    """Nó: Salvar progresso"""

    output_file = state['output_file']
    translated_items = state.get('translated_items', [])

    if not translated_items:
        return state

    # Salvar itens traduzidos
    mode = 'a' if os.path.exists(output_file) else 'w'
    with open(output_file, mode, encoding='utf-8') as f:
        for item in translated_items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"  Progresso salvo: {len(translated_items)} itens")

    return state


def checkpoint_node(state: TranslationState) -> TranslationState:
    """Nó: Criar checkpoint"""

    if not state.get('should_checkpoint', False):
        return state

    checkpoint_file = state.get('checkpoint_file', 'output/checkpoints/translation_checkpoint.json')

    # Criar diretório se não existir
    os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)

    checkpoint_data = {
        'last_completed_batch': state['current_batch_num'],
        'total_batches': state['total_batches'],
        'translated_count': state['translated_count'],
        'error_count': state['error_count'],
        'timestamp': datetime.now().isoformat(),
        'output_file': state['output_file']
    }

    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

    print(f"  Checkpoint salvo: batch {state['current_batch_num']}/{state['total_batches']}")

    return {
        **state,
        "should_checkpoint": False
    }


def should_continue(state: TranslationState) -> str:
    """Edge condicional: Verificar se deve continuar"""

    if state.get('completed', False) or state['current_batch_num'] >= state['total_batches']:
        return "finalize"
    return "translate"


def finalize_node(state: TranslationState) -> TranslationState:
    """Nó: Finalizar tradução"""

    # Limpar checkpoint
    checkpoint_file = state.get('checkpoint_file', 'output/checkpoints/translation_checkpoint.json')
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        print(f"\n[NÓ: FINALIZE] Checkpoint removido")

    # Estatísticas finais
    total = len(state['items'])
    success = state['translated_count'] - state['error_count']
    errors = state['error_count']

    print(f"\n{'='*80}")
    print(f"[RESUMO] Tradução Concluída")
    print(f"{'='*80}")
    print(f"  Total de itens:     {total}")
    print(f"  Traduzidos com sucesso: {success}")
    print(f"  Com erros:          {errors}")
    print(f"  Taxa de sucesso:    {(success/total*100):.1f}%")
    print(f"  Arquivo de saída:   {state['output_file']}")
    print(f"{'='*80}\n")

    return {
        **state,
        "completed": True
    }


# ============================================================================
# Construtor do Grafo LangGraph
# ============================================================================

def build_translation_graph(config: TranslationConfig) -> StateGraph:
    """Constrói o grafo LangGraph de tradução"""

    # Criar grafo
    workflow = StateGraph(TranslationState)

    # Adicionar nós
    workflow.add_node("load_data", load_data_node)
    workflow.add_node("create_batches", create_batches_node)
    workflow.add_node("check_resume", check_resume_node)
    workflow.add_node("translate", translate_batch_node)
    workflow.add_node("save_progress", save_progress_node)
    workflow.add_node("checkpoint", checkpoint_node)
    workflow.add_node("finalize", finalize_node)

    # Definir fluxo
    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "create_batches")
    workflow.add_edge("create_batches", "check_resume")
    workflow.add_edge("check_resume", "translate")
    workflow.add_edge("translate", "save_progress")
    workflow.add_edge("save_progress", "checkpoint")

    # Edge condicional após checkpoint
    workflow.add_conditional_edges(
        "checkpoint",
        should_continue,
        {
            "translate": "translate",
            "finalize": "finalize"
        }
    )

    workflow.add_edge("finalize", END)

    return workflow.compile()
