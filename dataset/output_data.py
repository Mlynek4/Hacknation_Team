# import pandas as pd
# import random
# import re

# VALUES_FILE = "anonymizer_values_55k.csv"
# TEMPLATES_FILE = "templates_5000.csv"
# OUTPUT_FILE = "filled_templates.csv"

# # 1) Load values
# df_vals = pd.read_csv(VALUES_FILE)
# values_by_cat = df_vals.groupby("category")["value"].apply(list).to_dict()

# # 2) Load templates
# df_templates = pd.read_csv(TEMPLATES_FILE)
# templates = df_templates["template"].tolist()

# def extract_placeholders(template):
#     return re.findall(r"\[([^\]]+)\]", template)

# def fill(template):
#     placeholders = extract_placeholders(template)
#     text = template

#     for ph in placeholders:
#         if ph in values_by_cat:
#             value = random.choice(values_by_cat[ph])
#         else:
#             value = f"<MISSING-{ph}>"

#         text = text.replace(f"[{ph}]", value)

#     return text

# # 3) Fill all templates
# filled = [fill(t) for t in templates]

# # 4) Save
# pd.DataFrame({"text": filled}).to_csv(OUTPUT_FILE, index=False)

# print("Done.")


# # import pandas as pd
# # import random
# # import re
# # import spacy

# # VALUES_FILE = "anonymizer_values_55k.csv"
# # TEMPLATES_FILE = "templates_5000.csv"
# # OUTPUT_FILE = "filled_templates.csv"

# # # ---- Load data ----
# # df_vals = pd.read_csv(VALUES_FILE)
# # values_by_cat = df_vals.groupby("category")["value"].apply(list).to_dict()
# # df_templates = pd.read_csv(TEMPLATES_FILE)
# # templates = df_templates["template"].tolist()

# # nlp = spacy.load("pl_core_news_sm")

# # # ---- Placeholder regex ----
# # PLACEHOLDER_RE = re.compile(r"\[([^\]]+)\]")

# # # ---- Simple rules for Polish inflection (example: dopełniacz) ----
# # def odmiana(value, category, case="gen"):
# #     if category == "surname" and case=="gen":
# #         # bardzo uproszczona odmiana do dopełniacza
# #         if value.endswith("ski"):
# #             return value[:-2] + "skiego"
# #         elif value.endswith("ska"):
# #             return value[:-1] + "iej"
# #         elif value.endswith("ak"):
# #             return value + "a"
# #         else:
# #             return value + "a"
# #     if category == "city" and case=="loc":
# #         # miejscownik
# #         if value.endswith("a"):
# #             return value[:-1] + "ie"
# #         else:
# #             return value + "ie"
# #     # dla innych przypadków, brak zmian
# #     return value

# # # ---- Extract placeholders ----
# # def extract_placeholders(template):
# #     return PLACEHOLDER_RE.findall(template)

# # # ---- Fill template with context-aware inflection ----
# # def fill(template):
# #     text = template
# #     placeholders = extract_placeholders(template)

# #     for ph in placeholders:
# #         if ph in values_by_cat:
# #             value = random.choice(values_by_cat[ph])
# #         else:
# #             value = f"<MISSING-{ph}>"

# #         # prosty kontekst: sprawdz słowo poprzedzające placeholder
# #         # np. "z [surname]" -> dopełniacz
# #         pattern = r"(\b\w+\b)\s+\[" + re.escape(ph) + r"\]"
# #         match = re.search(pattern, text)
# #         if match:
# #             prev_word = match.group(1).lower()
# #             if prev_word in ["z", "do", "od"]:  # typowe prepozycje do dopełniacza
# #                 value = odmiana(value, ph, "gen")
# #             elif prev_word in ["w", "na", "przy"]:  # miejscownik
# #                 value = odmiana(value, ph, "loc")
# #             # można dodać inne reguły

# #         text = text.replace(f"[{ph}]", value)

# #     return text

# # # ---- Fill all templates ----
# # filled = [fill(t) for t in templates]

# # # ---- Save ----
# # pd.DataFrame({"text": filled}).to_csv(OUTPUT_FILE, index=False)
# # print("Done.")

import pandas as pd
import random
import re
from typing import List, Tuple, Dict

# --- Konfiguracja plików ---
VALUES_FILE = "anonymizer_values_55k.csv"
TEMPLATES_FILE = "szablony_zdan.csv"
OUTPUT_CONLL_FILE = "output_data.txt"

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
    To jest kluczowa funkcja, która rozwiązuje problem tokenizacji.
    """
    all_conll_lines = []
    
    for template in templates:
        # Znajdujemy wszystkie placeholdery w szablonie
        placeholders = PLACEHOLDER_RE.findall(template)
        
        # Wypełniamy wartościami i jednocześnie śledzimy granice
        # Używamy re.split, aby podzielić szablon na części: tekst_O * placeholder * tekst_O * ...
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
                
                # Wylosuj wartość i zaktualizuj szablon (choć tutaj nie aktualizujemy samego stringa, tylko generujemy tokeny)
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
        print(f"Załadowano {len(templates)} szablonów i {len(values_by_cat)} kategorii wartości.")
        
        # 1. Generowanie danych CoNLL
        conll_output_lines = generate_conll(templates, values_by_cat)
        
        # 2. Zapis do pliku
        try:
            with open(OUTPUT_CONLL_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(conll_output_lines))
            print(f"Pomyślnie zapisano {len(conll_output_lines) - len(templates)} tokenów do {OUTPUT_CONLL_FILE}")
            
            # Opcjonalnie: Zapisz surowe teksty (jak w pierwotnym skrypcie)
            # filled_texts = [fill(t) for t in templates] # Można zaimplementować inną funkcję fill
            # pd.DataFrame({"text": filled_texts}).to_csv("filled_templates_raw.csv", index=False)
            
        except Exception as e:
            print(f"Błąd podczas zapisu pliku: {e}")