"""
Create PT-BR dataset with original structure + translations
Merges translations into the original JSONL structure
"""

import json

def create_pt_br_dataset(translated_file, output_file):
    """
    Create PT-BR dataset maintaining original structure

    Args:
        translated_file: File with translations (clapnq_translated_batch.jsonl)
        output_file: Output file (clapnq_pt_br.jsonl)
    """

    print(f"\n{'='*80}")
    print(f"[CREATE] Creating PT-BR dataset")
    print(f"{'='*80}")
    print(f"  Input:  {translated_file}")
    print(f"  Output: {output_file}")
    print(f"{'='*80}\n")

    translated_items = []
    success_count = 0
    error_count = 0

    # Read all translated items
    with open(translated_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)

            # Check if translation was successful
            title_pt = item.get('title_pt', '')
            text_pt = item.get('text_pt', '')

            if title_pt and not title_pt.startswith('[ERROR'):
                # Create item with original structure + PT fields
                pt_item = {
                    '_id': item.get('_id'),
                    'id': item.get('id'),
                    'url': item.get('url'),
                    'text': item.get('text'),
                    'title': item.get('title'),
                    'title_pt': title_pt,
                    'text_pt': text_pt
                }
                translated_items.append(pt_item)
                success_count += 1
            else:
                error_count += 1
                print(f"[SKIP] Item {item.get('id')} - Translation error")

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in translated_items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"\n{'='*80}")
    print(f"[SUMMARY]")
    print(f"{'='*80}")
    print(f"  Successfully added:  {success_count} items")
    print(f"  Skipped (errors):    {error_count} items")
    print(f"  Total in output:     {success_count} items")
    print(f"{'='*80}")
    print(f"\n[OK] PT-BR dataset created: {output_file}\n")

    # Show sample
    if translated_items:
        sample = translated_items[0]
        print(f"[SAMPLE] First item structure:")
        print(f"  _id:      {sample['_id']}")
        print(f"  id:       {sample['id']}")
        print(f"  title:    {sample['title'][:50]}...")
        print(f"  title_pt: {sample['title_pt'][:50]}...")
        print(f"  text:     {sample['text'][:50]}...")
        print(f"  text_pt:  {sample['text_pt'][:50]}...")
        print()

    return success_count


if __name__ == "__main__":
    input_file = "clapnq_translated_batch.jsonl"
    output_file = "clapnq_pt_br.jsonl"

    count = create_pt_br_dataset(input_file, output_file)

    print(f"[DONE] {count} items with PT-BR translations ready for SemEval!")
