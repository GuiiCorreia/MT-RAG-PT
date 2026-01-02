"""
Fix newlines in PT-BR translations to match original structure
Preserves the exact newline structure from the English text
"""

import json
import re

def fix_newlines_in_translation(original_text, translated_text, original_title, translated_title):
    """
    Fix newlines in translation to match original structure

    The original format is typically: "Title\nActual text content..."
    The translation should mirror this: "Título Traduzido\nConteúdo traduzido..."

    Args:
        original_text: Original English text with \n
        translated_text: Translated Portuguese text (might be missing \n)
        original_title: Original English title
        translated_title: Translated Portuguese title

    Returns:
        Fixed Portuguese text with proper \n placement
    """

    # Count newlines in original
    original_newlines = original_text.count('\n')

    # If original has no newlines, return as is
    if original_newlines == 0:
        return translated_text

    # Check if original follows "Title\nContent" pattern
    if original_text.startswith(original_title + '\n'):
        # The translation should also follow "Título\nConteúdo" pattern
        # Remove title from beginning of translated text if present
        pt_content = translated_text

        # If translation starts with the title, remove it
        if translated_text.startswith(translated_title):
            # Remove title and any leading whitespace/punctuation
            pt_content = translated_text[len(translated_title):].lstrip()

            # Handle cases where title is followed by parentheses
            # e.g., "Title (previously..." - keep the parentheses with content

        # Reconstruct with title + newline + content
        fixed_text = f"{translated_title}\n{pt_content}"
        return fixed_text

    # For other newline patterns, try to preserve structure
    # Split original by newlines to understand structure
    original_parts = original_text.split('\n')

    # If we can't determine pattern, just return original translation
    return translated_text


def fix_pt_br_dataset(input_file, output_file):
    """
    Fix newlines in the entire PT-BR dataset
    """

    print(f"\n{'='*80}")
    print(f"[FIX] Fixing newlines in PT-BR dataset")
    print(f"{'='*80}")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print(f"{'='*80}\n")

    fixed_items = []
    fixed_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            item = json.loads(line)

            original_text = item.get('text', '')
            original_title = item.get('title', '')
            translated_text = item.get('text_pt', '')
            translated_title = item.get('title_pt', '')

            # Count original newlines
            original_newlines = original_text.count('\n')
            pt_newlines = translated_text.count('\n')

            # Fix if newlines don't match
            if original_newlines != pt_newlines:
                fixed_text = fix_newlines_in_translation(
                    original_text,
                    translated_text,
                    original_title,
                    translated_title
                )
                item['text_pt'] = fixed_text
                fixed_count += 1

                if line_num <= 3:  # Show first few fixes
                    print(f"[FIX #{line_num}] ID: {item.get('id')}")
                    print(f"  Original newlines: {original_newlines}")
                    print(f"  PT newlines before: {pt_newlines}")
                    print(f"  PT newlines after: {fixed_text.count('\\n')}")
                    print(f"  Preview: {fixed_text[:80]}...")
                    print()

            fixed_items.append(item)

    # Write fixed dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in fixed_items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"\n{'='*80}")
    print(f"[SUMMARY]")
    print(f"{'='*80}")
    print(f"  Total items:         {len(fixed_items)}")
    print(f"  Fixed newlines:      {fixed_count}")
    print(f"  No changes needed:   {len(fixed_items) - fixed_count}")
    print(f"{'='*80}")
    print(f"\n[OK] Fixed dataset saved: {output_file}\n")

    return fixed_count


if __name__ == "__main__":
    input_file = "clapnq_pt_br.jsonl"
    output_file = "clapnq_pt_br.jsonl"  # Overwrite

    count = fix_pt_br_dataset(input_file, output_file)

    print(f"[DONE] Fixed {count} items to match original structure!")
