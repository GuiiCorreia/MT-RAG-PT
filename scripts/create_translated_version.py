"""
Create translated version with same variable names
Replaces text and title content with Portuguese translation
"""

import json
import os

def create_translated_version(pt_br_file, output_jsonl, output_md):
    """
    Create version where text and title contain Portuguese translations

    Args:
        pt_br_file: File with both EN and PT fields
        output_jsonl: Output JSONL with PT content in original field names
        output_md: Output Markdown file for visualization
    """

    print(f"\n{'='*80}")
    print(f"[CREATE] Creating translated version for benchmark")
    print(f"{'='*80}")
    print(f"  Input:       {pt_br_file}")
    print(f"  Output JSONL: {output_jsonl}")
    print(f"  Output MD:    {output_md}")
    print(f"{'='*80}\n")

    translated_items = []
    md_content = []

    # Add markdown header
    md_content.append("# Dataset Traduzido - Português Brasileiro\n")
    md_content.append("## SemEval - CLAPNQ Dataset (PT-BR)\n\n")
    md_content.append(f"Total de itens: ")

    with open(pt_br_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            item = json.loads(line)

            # Create new item with same structure but PT content
            translated_item = {
                '_id': item.get('_id'),
                'id': item.get('id'),
                'url': item.get('url'),
                'text': item.get('text_pt'),  # PT content in 'text' field
                'title': item.get('title_pt')  # PT content in 'title' field
            }

            translated_items.append(translated_item)

            # Add to markdown (first 5 items)
            if i <= 5:
                md_content.append(f"---\n\n")
                md_content.append(f"### Item {i}\n\n")
                md_content.append(f"**ID**: `{translated_item['id']}`\n\n")
                md_content.append(f"**Título**: {translated_item['title']}\n\n")
                md_content.append(f"**Texto**:\n\n{translated_item['text']}\n\n")

    # Update count in markdown
    md_content[2] = f"Total de itens: {len(translated_items)}\n\n"

    # Add summary at the end of markdown
    md_content.append(f"\n---\n\n")
    md_content.append(f"## Resumo\n\n")
    md_content.append(f"- **Total de itens traduzidos**: {len(translated_items)}\n")
    md_content.append(f"- **Idioma**: Português Brasileiro (PT-BR)\n")
    md_content.append(f"- **Modelo de tradução**: Gemini 2.5-Flash\n")
    md_content.append(f"- **Framework**: LangGraph\n")
    md_content.append(f"- **Estrutura**: Idêntica ao original (mesmas variáveis)\n\n")

    # Write JSONL
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for item in translated_items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    # Write Markdown
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(''.join(md_content))

    print(f"[OK] Created JSONL: {output_jsonl}")
    print(f"[OK] Created Markdown: {output_md}")
    print(f"\n{'='*80}")
    print(f"[SUMMARY]")
    print(f"{'='*80}")
    print(f"  Items translated:  {len(translated_items)}")
    print(f"  Structure:         Same as original")
    print(f"  Variable names:    text, title (Portuguese content)")
    print(f"{'='*80}\n")

    # Show sample
    if translated_items:
        sample = translated_items[0]
        print(f"[SAMPLE] First item:")
        print(f"  _id:   {sample['_id']}")
        print(f"  id:    {sample['id']}")
        print(f"  title: {sample['title'][:60]}...")
        print(f"  text:  {sample['text'][:60]}...")
        print()

    return len(translated_items)


if __name__ == "__main__":
    pt_br_file = "clapnq_pt_br.jsonl"
    output_jsonl = "clapnq_sample_500_translated.jsonl"
    output_md = "clapnq_sample_500_translated.md"

    count = create_translated_version(pt_br_file, output_jsonl, output_md)

    print(f"[DONE] {count} items ready for benchmark testing!")
    print(f"\nFiles created:")
    print(f"  1. {output_jsonl} - JSONL for benchmark")
    print(f"  2. {output_md} - Markdown for visualization")
