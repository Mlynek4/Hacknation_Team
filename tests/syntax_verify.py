import re

# ============================================================
# 1. PROSTA MOCK PREDICT (PODMIENISZ NA SWÓJ MODEL)
# ============================================================


def fake_predict_text(text):
    # przykład: Jan Kowalski mieszka w Nowym Sączu
    return [
        ("Inspektor", "O"),
        ("sprawdził", "O"),
        ("tożsamość", "O"),
        ("Mateusz", "B-NAME"),
        ("Michalski", "B-SURNAME"),
        ("(", "O"),
        ("PESEL", "O"),
        ("303176009", "B-PESEL"),
        (")", "O"),
        ("i", "O"),
        ("zarejestrował", "O"),
        ("adres", "O"),
        ("zamieszkania", "O"),
        ("ul.", "B-ADDRESS"),
        ("Mickiewicza", "I-ADDRESS"),
        ("45", "I-ADDRESS"),
        (",", "I-ADDRESS"),
        ("Koszalin", "I-ADDRESS"),
        (".", "O"),
        ("Zlecono", "O"),
        ("kontrolę", "O"),
        ("adresu", "O"),
        ("ul.", "B-ADDRESS"),
        ("Nowa", "I-ADDRESS"),
        ("84", "I-ADDRESS"),
        (",", "I-ADDRESS"),
        ("Ciechanów", "I-ADDRESS"),
        ("Reykjavik", "B-CITY"),
        ("po", "O"),
        ("otrzymaniu", "O"),
        ("zgłoszenia", "O"),
        ("od", "O"),
        ("moja", "B-RELATIVE"),
        ("siostra", "I-RELATIVE"),
        ("Grzegorz", "I-RELATIVE"),
        ("Kaczmarek", "I-RELATIVE"),
        (".", "O"),
    ]
    # return [
    #     ("J", "B-NAME"),
    #     ("a", "I-NAME"),
    #     ("n", "I-NAME"),
    #     ("mieszka", "O"),
    #     ("w", "O"),
    #     ("Nowym", "B-CITY"),
    #     ("Sączu", "I-CITY")
    # ]


# ============================================================
# 2. GRUPOWANIE ENCI: B-XXX + I-XXX + I-XXX → jedna encja
# ============================================================


def group_entities(predicted):
    entities = []
    current = None

    for token, tag in predicted:
        if tag == "O":
            if current:
                entities.append(current)
                current = None
            continue

        prefix, ent_class = tag.split("-", 1)

        # ----------------------
        # B-XXX → start new entity
        # ----------------------
        if prefix == "B":
            if current:
                entities.append(current)

            current = {"text": token, "tag": ent_class}
            continue

        # ----------------------
        # I-XXX
        # ----------------------
        if prefix == "I":
            if not current or current["tag"] != ent_class:
                # treat as B
                current = {"text": token, "tag": ent_class}
                continue

            # I continuing same entity — now decide how to join
            if (
                len(token) == 1
                or token.islower()
                or token.isalpha()
                and len(token) <= 2
            ):
                # subtoken → attach **without space**
                current["text"] += token
            else:
                # normal word → add space
                current["text"] += " " + token

    if current:
        entities.append(current)

    return entities


# ============================================================
# 3. PLACEHOLDERY
# ============================================================

PLACEHOLDERS = {
    "ADDRESS": "[address]",
    "AGE": "[age]",
    "BANK-ACCOUNT": "[bank-account]",
    "CITY": "[city]",
    "COMPANY": "[company]",
    "CREDIT-CARD-NUMBER": "[credit-card-number]",
    "DATE": "[date]",
    "DATE-OF-BIRTH": "[date-of-birth]",
    "DOCUMENT-NUMBER": "[document-number]",
    "EMAIL": "[email]",
    "ETHNICITY": "[ethnicity]",
    "HEALTH": "[health]",
    "JOB-TITLE": "[job-title]",
    "NAME": "[name]",
    "PESEL": "[pesel]",
    "PHONE": "[phone]",
    "POLITICAL-VIEW": "[political-view]",
    "RELATIVE": "[relative]",
    "RELIGION": "[religion]",
    "SCHOOL-NAME": "[school-name]",
    "SECRET": "[secret]",
    "SEX": "[sex]",
    "SEXUAL-ORIENTATION": "[sexual-orientation]",
    "SURNAME": "[surname]",
    "USERNAME": "[username]",
}


# ============================================================
# 4. BEZPIECZNA ZAMIANA (CAŁE SŁOWA)
# ============================================================


def safe_replace(text, original, placeholder):
    return re.sub(r"\b" + re.escape(original) + r"\b", placeholder, text)


# ============================================================
# 5. GŁÓWNA FUNKCJA
# ============================================================


def replace_entities(text):
    predicted = fake_predict_text(text)

    # Łączenie B-/I-
    entities = group_entities(predicted)

    replaced_text = text
    log = []

    for ent in entities:
        original = ent["text"]
        tag = ent["tag"]
        placeholder = PLACEHOLDERS.get(tag, f"[{tag.lower()}]")

        replaced_text = safe_replace(replaced_text, original, placeholder)

        log.append({"original": original, "replacement": placeholder, "tag": tag})

    return replaced_text, log, predicted


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    example = "Inspektor sprawdził tożsamość Mateusz Michalski (PESEL 303176009) i zarejestrował adres zamieszkania ul. Mickiewicza 45, Koszalin. Zlecono kontrolę adresu ul. Nowa 84, Ciechanów Reykjavik po otrzymaniu zgłoszenia od moja siostra Grzegorz Kaczmarek."
    masked, log, pred = replace_entities(example)

    print("Oryginał:", example)
    print("Masked:", masked)
    print("Pred:", pred)
    print("Log:", log)
