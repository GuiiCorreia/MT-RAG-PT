"""
Extract only translations from translated batch file
Creates a clean file with only Portuguese translations
"""

import json

def extract_translations(input_file, output_file):
    """Extract only PT-BR translations to a clean file"""

    translations = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)

            # Only include successfully translated items
            if item.get('title_pt') and not item['title_pt'].startswith('[ERROR'):
                translation_item = {
                    'id': item.get('id'),
                    'title_original': item.get('title'),
                    'text_original': item.get('text'),
                    'title_pt': item.get('title_pt'),
                    'text_pt': item.get('text_pt'),
                    'confidence': item.get('translation_confidence', 'unknown')
                }
                translations.append(translation_item)

    # Save to new file
    with open(output_file, 'w', encoding='utf-8') as f:
        for trans in translations:
            f.write(json.dumps(trans, ensure_ascii=False) + '\n')

    print(f"[OK] Extracted {len(translations)} translations")
    print(f"[OK] Saved to: {output_file}")

    return translations


if __name__ == "__main__":
    input_file = "clapnq_translated_batch.jsonl"
    output_file = "clapnq_translations_only.jsonl"

    translations = extract_translations(input_file, output_file)

    # Print sample
    if translations:
        print(f"\n[SAMPLE] First translation:")
        print(f"  Title (EN): {translations[0]['title_original'][:60]}...")
        print(f"  Title (PT): {translations[0]['title_pt'][:60]}...")
        print(f"  Confidence: {translations[0]['confidence']}")
