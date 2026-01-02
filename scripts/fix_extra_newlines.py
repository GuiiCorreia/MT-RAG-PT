"""
Remove extra newlines from translations to match original structure
"""

import json

def remove_extra_newlines(text_pt, target_newline_count):
    """
    Remove extra newlines from PT text

    Keep only the first N newlines (usually 1: between title and content)
    Replace other newlines with spaces
    """

    if '\n' not in text_pt:
        return text_pt

    parts = text_pt.split('\n')

    if target_newline_count == 1:
        # Keep first newline (title separator), join rest with spaces
        if len(parts) >= 2:
            title = parts[0]
            content = ' '.join(parts[1:])
            return f"{title}\n{content}"

    return text_pt


def fix_extra_newlines_in_dataset(input_file, output_file):
    """Fix items with extra newlines"""

    print(f"\n{'='*80}")
    print(f"[FIX] Removing extra newlines from PT-BR dataset")
    print(f"{'='*80}\n")

    items = []
    fixed_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            item = json.loads(line)

            en_newlines = item['text'].count('\n')
            pt_newlines = item['text_pt'].count('\n')

            if pt_newlines > en_newlines:
                # Remove extra newlines
                fixed_text = remove_extra_newlines(item['text_pt'], en_newlines)
                item['text_pt'] = fixed_text
                fixed_count += 1

                print(f"[FIX] Item {i} ({item['id']})")
                print(f"  Before: {pt_newlines} newlines")
                print(f"  After:  {fixed_text.count(chr(10))} newlines")
                print()

            items.append(item)

    # Write fixed file
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"{'='*80}")
    print(f"[SUMMARY] Fixed {fixed_count} items")
    print(f"{'='*80}\n")

    return fixed_count


if __name__ == "__main__":
    count = fix_extra_newlines_in_dataset("clapnq_pt_br.jsonl", "clapnq_pt_br.jsonl")
    print(f"[DONE] Removed extra newlines from {count} items!")
