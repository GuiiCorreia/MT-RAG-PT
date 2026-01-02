"""
Advanced Translation Prompts for Academic Datasets
==================================================
Engineered prompts for high-quality English to Brazilian Portuguese translation
"""

def get_batch_translation_prompt(items):
    """
    Advanced prompt engineering for batch translation.

    Techniques applied:
    - Role-based prompting (expert translator persona)
    - Context setting (academic/research domain)
    - Step-by-step instructions
    - Quality criteria definition
    - Output format specification

    Args:
        items: List of dictionaries with 'id', 'title', 'text' fields

    Returns:
        str: Formatted prompt for batch translation
    """

    # Format items for batch
    items_text = ""
    for idx, item in enumerate(items, 1):
        items_text += f"""
--- ITEM {idx} ---
ID: {item.get('id', 'unknown')}
Title: {item.get('title', '')}
Text: {item.get('text', '')}

"""

    prompt = f"""# BATCH TRANSLATION TASK

You are an expert academic translator specializing in English to Brazilian Portuguese
translation for NLP research datasets (SemEval).

## TASK
Translate the following {len(items)} items from English to Brazilian Portuguese.

## TRANSLATION GUIDELINES

### Semantic Fidelity
- Preserve exact meaning and nuances
- Maintain information density
- Keep same level of specificity

### Terminology
- Keep proper nouns in original form (unless widely accepted Portuguese equivalent exists)
- Use standard academic Portuguese terminology
- Preserve brand names, product names, titles

### Linguistic Quality
- Use formal, academic Brazilian Portuguese
- Maintain objectivity and encyclopedic tone
- Ensure grammatical correctness

### Structural Preservation
- Keep same paragraph structure
- Maintain information flow
- Preserve newline characters (\\n) exactly as in original

## SOURCE ITEMS
{items_text}

## OUTPUT FORMAT

Return a JSON object with this structure:
{{
  "translations": [
    {{
      "item_id": "the original item ID",
      "title_pt": "translated title in Brazilian Portuguese",
      "text_pt": "complete translated text in Brazilian Portuguese",
      "confidence": "high|medium|low"
    }},
    ... (one object for each of the {len(items)} items)
  ],
  "batch_notes": "any relevant notes about translation decisions (optional)"
}}

IMPORTANT:
- Translate ALL {len(items)} items
- Maintain the same order
- Use the exact item IDs from the source
- Return ONLY valid JSON

Proceed with the batch translation now."""

    return prompt


def get_single_translation_prompt(title, text):
    """
    Prompt for single item translation (used in non-batch mode).

    Args:
        title: Original title in English
        text: Original text in English

    Returns:
        str: Formatted prompt for single translation
    """

    prompt = f"""# EXPERT TRANSLATOR ROLE

You are a highly specialized academic translator with expertise in:
- English to Brazilian Portuguese (pt-BR) translation
- Natural Language Processing (NLP) and computational linguistics terminology
- Semantic evaluation datasets and knowledge base construction
- Cross-lingual information preservation

# TRANSLATION TASK

Translate the following English text into formal, academic Brazilian Portuguese for a SemEval (Semantic Evaluation) research dataset.

## SOURCE TEXT

**Title:** {title}

**Content:** {text}

# TRANSLATION GUIDELINES

## 1. Semantic Fidelity
- Preserve the EXACT semantic meaning and nuances of the original text
- Maintain factual accuracy and information density
- Keep the same level of specificity and detail

## 2. Terminology Handling
- **Proper Nouns:** Keep names of people, places, and specific organizations in original form
  * Exception: Use established Portuguese equivalents (e.g., "New York" → "Nova York")
- **Technical Terms:** Use standard academic/technical Portuguese terminology
- **Named Entities:** Preserve brand names, product names, and titles (e.g., "Facebook", "iPhone")
- **Acronyms:** Keep acronyms in English, optionally add Portuguese explanation in parentheses

## 3. Linguistic Quality
- Use formal, academic register suitable for scholarly publication
- Employ grammatically correct and natural Brazilian Portuguese
- Maintain objectivity and encyclopedic tone
- Avoid colloquialisms and regional variations

## 4. Structural Preservation
- Keep the same paragraph structure and information flow
- Preserve emphasis and rhetorical structure
- Maintain the relationship between title and content
- **CRITICAL:** Preserve all newline characters (\\n) exactly as in original

## 5. Cultural Adaptation
- Adapt cultural references only when necessary for comprehension
- Preserve the cultural context of the source when relevant to meaning
- Use metric system equivalents for measurements when appropriate

# QUALITY CRITERIA

Your translation will be evaluated on:
✓ Accuracy: Faithful representation of original meaning
✓ Fluency: Natural and grammatically correct Portuguese
✓ Consistency: Uniform terminology and style
✓ Completeness: No omissions or additions
✓ Academic register: Appropriate for research context

# OUTPUT FORMAT

Provide your translation in the following JSON structure:
- "title_pt": The translated title in Brazilian Portuguese
- "text_pt": The complete translated content in Brazilian Portuguese
- "confidence": Your confidence level ("high", "medium", "low")
- "notes": Any relevant translation decisions or ambiguities (optional)

# TRANSLATION

Proceed with the translation now, following all guidelines above."""

    return prompt
    