"""
Main Translation Pipeline - LangGraph Agent
===========================================
Entry point usando agente LangGraph
"""

import argparse
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.settings import TranslationConfig, ensure_directories
from src.translation_agent import build_translation_graph, TranslationState


def main():
    """Ponto de entrada principal"""

    parser = argparse.ArgumentParser(
        description="Pipeline de Tradução SemEval usando LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Traduzir primeiros 100 itens
  python src/main.py --limit 100

  # Traduzir com batch size customizado
  python src/main.py --batch-size 15

  # Usar modelo diferente
  python src/main.py --model gemini-2.5-pro
        """
    )

    parser.add_argument(
        "--input",
        default="data/samples/clapnq_sample_500.jsonl",
        help="Arquivo JSONL de entrada"
    )
    parser.add_argument(
        "--output",
        default="data/translated/clapnq_translated_batch.jsonl",
        help="Arquivo JSONL de saída"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limitar número de itens a traduzir"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Itens por batch"
    )
    parser.add_argument(
        "--rps",
        type=int,
        default=9,
        help="Requisições por segundo"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Modelo Gemini a usar"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Não retomar de checkpoint"
    )

    args = parser.parse_args()

    # Garantir que diretórios existem
    ensure_directories()

    # Criar configuração
    config = TranslationConfig(
        model_name=args.model,
        batch_size=args.batch_size,
        requests_per_second=args.rps,
        resume=not args.no_resume
    )
    config.limit = args.limit  # Adicionar limite

    # Validar chave de API
    if not config.api_key:
        print("[ERRO] GEMINI_API_KEY não encontrada nas variáveis de ambiente")
        print("Configure no arquivo .env")
        return

    # Banner
    print("\n" + "="*80)
    print("[AGENTE LANGGRAPH] Pipeline de Tradução SemEval")
    print("="*80)
    print(f"  Modelo:       {config.model_name}")
    print(f"  Entrada:      {args.input}")
    print(f"  Saída:        {args.output}")
    print(f"  Batch size:   {config.batch_size}")
    print(f"  Rate limit:   {config.requests_per_second} req/s")
    if args.limit:
        print(f"  Limite:       {args.limit} itens")
    print("="*80)

    # Construir grafo LangGraph
    print("\n[GRAFO] Construindo agente LangGraph...")
    app = build_translation_graph(config)

    # Estado inicial
    initial_state = TranslationState(
        input_file=args.input,
        output_file=args.output,
        items=[],
        batches=[],
        current_batch_num=0,
        total_batches=0,
        translated_items=[],
        translated_count=0,
        error_count=0,
        checkpoint_file="output/checkpoints/translation_checkpoint.json",
        should_checkpoint=False,
        config=config,
        completed=False
    )

    # Executar grafo
    print("[GRAFO] Iniciando execução do agente...\n")
    start_time = time.time()

    try:
        final_state = app.invoke(initial_state)

        elapsed = time.time() - start_time
        print(f"\n[TEMPO] Execução total: {elapsed:.2f}s")

        if final_state['translated_count'] > 0:
            avg = elapsed / final_state['translated_count']
            print(f"[TEMPO] Média por item: {avg:.2f}s")

    except KeyboardInterrupt:
        print("\n\n[AVISO] Tradução interrompida pelo usuário")
        print("Resultados parciais foram salvos")
        print("Execute novamente para retomar do checkpoint")
    except Exception as e:
        print(f"\n\n[ERRO] Erro fatal: {e}")
        raise


if __name__ == "__main__":
    main()
