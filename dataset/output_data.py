import pandas as pd
import random
import re
from typing import List, Tuple, Dict

# --- Konfiguracja plików ---
VALUES_FILE = "anonymizer_values_55k.csv"
TEMPLATES_FILE = "szablony_zdan.csv"
OUTPUT_CONLL_FILE = "output_data.txt"

# 🚀 NOWA ZMIENNA KONTROLNA 
# Ustawia, ile razy każdy szablon (zdanie) ma zostać użyty do generowania unikatowych rekordów.
# Przykłady:
# 1. Jeśli masz 26 szablonów i ustawisz 30, otrzymasz 780 rekordów (26 * 30).
# 2. Jeśli masz 50 szablonów i ustawisz 10, otrzymasz 500 rekordów.
RECORDS_PER_TEMPLATE = 50 # TUTAJ KONTROLUJESZ LICZBĘ GENEROWANYCH ZDAŃ

# Regex do ekstrakcji placeholderów (np. [name])
PLACEHOLDER_RE = re.compile(r"\[([^\]]+)\]")

# --- Funkcje pomocnicze ---

def simple_tokenize(text: str) -> List[str]:
    """
    Prosta tokenizacja na potrzeby CoNLL.
    Rozdziela po spacji, ale zachowuje znaki interpunkcyjne jako oddzielne tokeny.
    """
    # Znajduje ciągi znaków (słowa, cyfry, złożone ciągi jak e-maile/numery) ORAZ pojedyncze znaki interpunkcyjne.
    tokens = re.findall(r"\w[\w\.\-\+@]*|\S", text)
    return tokens

def load_data():
    """Ładuje wartości i szablony."""
    try:
        df_vals = pd.read_csv(VALUES_FILE)
        values_by_cat = df_vals.groupby("category")["value"].apply(list).to_dict()
        
        df_templates = pd.read_csv(TEMPLATES_FILE)
        templates = df_templates["template"].tolist()
        
        return values_by_cat, templates
    except FileNotFoundError as e:
        print(f"Błąd: Nie znaleziono pliku: {e.filename}")
        return None, None
    except Exception as e:
        print(f"Wystąpił błąd podczas ładowania danych: {e}")
        return None, None

def tokenize_and_tag(
    template_part: str, 
    value: str = None, 
    category: str = None
) -> List[Tuple[str, str]]:
    """
    Tokenizuje fragment tekstu i przypisuje tagi BIO.
    Jeśli podana jest wartość i kategoria, fragment tekstu jest traktowany jako encja.
    """
    if value and category:
        # Tokenizujemy wstawioną wartość
        entity_tokens = simple_tokenize(value)
        tagged_tokens = []
        tag_prefix = category.upper()
        
        # Przypisujemy tagi B- i I-
        for i, token in enumerate(entity_tokens):
            tag = f"B-{tag_prefix}" if i == 0 else f"I-{tag_prefix}"
            tagged_tokens.append((token, tag))
        
        return tagged_tokens

    else:
        # Tokenizujemy standardowy tekst szablonu (bez encji)
        untagged_tokens = simple_tokenize(template_part)
        return [(token, "O") for token in untagged_tokens]

def generate_conll(templates: List[str], values_by_cat: Dict[str, List[str]]) -> List[str]:
    """
    Generuje dane CoNLL przez przetwarzanie szablonów i wstawianie wartości.
    """
    all_conll_lines = []
    
    for template in templates:
        # Znajdujemy wszystkie placeholdery w szablonie
        placeholders = PLACEHOLDER_RE.findall(template)
        
        # Wypełniamy wartościami i jednocześnie śledzimy granice
        parts = PLACEHOLDER_RE.split(template)
        
        current_conll_entry = []
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # To jest tekst, który NIE jest placeholderem (część O-tagowana)
                if part:
                    current_conll_entry.extend(tokenize_and_tag(part))
            else:
                # To jest nazwa placeholdera (np. 'phone', 'name')
                category = part
                
                # Wylosuj wartość
                # Używamy .get() i listy awaryjnej, aby obsłużyć brakujące kategorie (MISSING-...)
                value = random.choice(values_by_cat.get(category, [f"<MISSING-{category}>"]))
                
                # Dodaj tokeny wstawionej encji
                current_conll_entry.extend(tokenize_and_tag(value, value, category))
        
        # Zapisz linie CoNLL dla bieżącego zdania
        for token, tag in current_conll_entry:
            all_conll_lines.append(f"{token}\t{tag}")
            
        # Dodaj pustą linię oddzielającą zdania (wymagane w formacie CoNLL)
        all_conll_lines.append("")

    return all_conll_lines

# --- Główna funkcja ---

if __name__ == "__main__":
    values_by_cat, templates = load_data()
    
    if values_by_cat and templates:
        # Obliczenie docelowej liczby
        target_records = len(templates) * RECORDS_PER_TEMPLATE
        
        print(f"Załadowano {len(templates)} szablonów i {len(values_by_cat)} kategorii wartości.")
        print(f"Ustawiono, że każdy szablon zostanie użyty {RECORDS_PER_TEMPLATE} razy. Docelowy zbiór: {target_records} rekordów.")
        
        all_conll_output_lines = []
        
        # KLUCZOWA ZMIANA: Pętla wielokrotnego generowania
        for i in range(RECORDS_PER_TEMPLATE):
            print(f"Generacja: {i + 1}/{RECORDS_PER_TEMPLATE}...")
            # 1. Generowanie danych CoNLL (za każdym razem losowane są nowe wartości)
            conll_output_lines = generate_conll(templates, values_by_cat)
            all_conll_output_lines.extend(conll_output_lines)

        # 2. Zapis do pliku
        try:
            # Zapisujemy wszystkie wygenerowane linie
            with open(OUTPUT_CONLL_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(all_conll_output_lines))
                
            generated_sentences = len(templates) * RECORDS_PER_TEMPLATE
            print(f"\n✅ Pomyślnie zapisano {generated_sentences} zdań (szablonów) do {OUTPUT_CONLL_FILE}")
            
        except Exception as e:
            print(f"Błąd podczas zapisu pliku: {e}")