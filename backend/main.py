from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import re
import random
from typing import List, Dict, Any, Optional

import spacy
import morfeusz2
import torch
from transformers import pipeline


# ============================================================
# 1. Global NLP objects: spaCy + Morfeusz + FastPDN (HerBERT NER)
# ============================================================

print("Loading spaCy...")
NLP = spacy.load("pl_core_news_sm")

print("Loading Morfeusz2...")
MORF = morfeusz2.Morfeusz()


class MorphoRealizer:
    """
    Prosta warstwa nad Morfeuszem do odmieniania nazw własnych (np. miast).
    """

    def __init__(self, morf: morfeusz2.Morfeusz):
        self.morf = morf

    def _generate_noun_form(self, lemma: str, case: str, number: str = "sg") -> str:
        """
        Wybierz formę rzeczownika:
        - case: 'loc', 'gen', 'nom', ...
        - number: 'sg' / 'pl'
        """
        try:
            forms = self.morf.generate(lemma)
        except RuntimeError:
            return lemma

        # Morfeusz2: (orth, base, tags, cats, misc)
        for orth, base, tags, cats, misc in forms:
            if "subst" in tags and f":{case}:" in tags and f":{number}:" in tags:
                return orth

        for orth, base, tags, cats, misc in forms:
            if "subst" in tags and f":{case}:" in tags:
                return orth

        return lemma

    def inflect_city_by_prepositions(self, text: str, city_lemma: str) -> str:
        """
        'w <miasto>'  -> 'w <miasto_loc>'
        'do <miasto>' -> 'do <miasto_gen>'
        """

        def repl_loc(match: re.Match) -> str:
            prep = match.group(1)
            form = self._generate_noun_form(city_lemma, "loc", "sg")
            return f"{prep} {form}"

        def repl_gen(match: re.Match) -> str:
            prep = match.group(1)
            form = self._generate_noun_form(city_lemma, "gen", "sg")
            return f"{prep} {form}"

        pattern_loc = r"\b([wW])\s+" + re.escape(city_lemma) + r"\b"
        pattern_gen = r"\b([dD]o)\s+" + re.escape(city_lemma) + r"\b"

        text = re.sub(pattern_loc, repl_loc, text)
        text = re.sub(pattern_gen, repl_gen, text)
        return text


MORPHO_REALIZER = MorphoRealizer(MORF)

print("Loading HerBERT token classifier (FastPDN)...")
DEVICE = 0 if torch.cuda.is_available() else -1
NER_PIPELINE = pipeline(
    "ner",
    model="clarin-pl/FastPDN",        # publiczny PL NER
    aggregation_strategy="simple",
    device=DEVICE,
)


# Typ pomocniczy (nie zmieniam formatu – dalej dict)
PIIEntity = Dict[str, Any]


# ============================================================
# 2. Regexy PII (z tolerancją na "brudne" dane + placeholdery)
# ============================================================

# --- Pomocnicze mapowanie liter → cyfr dla telefonów ---
PHONE_CHAR_MAP = str.maketrans({
    "O": "0", "o": "0",
    "I": "1", "l": "1", "L": "1",
    "Z": "2", "z": "2",
    "S": "5", "s": "5",
    "B": "8", "b": "8",
})


def normalize_phone_digits(raw: str) -> str:
    """
    Zamiana typowych literówek na cyfry i wyrzucenie wszystkiego poza cyframi.
    Np. '508 561 71o' -> '508561710'
    """
    return re.sub(r"\D", "", raw.translate(PHONE_CHAR_MAP))


# PESEL: 11 czystych cyfr LUB "prawie PESEL" w kontekście słowa „PESEL”
PESEL_RAW_RE = re.compile(r"\b\d{11}\b")
PESEL_TAGGED_RE = re.compile(r"(?i)\bpesel\b[^0-9]{0,5}([0-9A-Za-z!]{8,14})")

# kandydaci na telefony – szeroki, "brudny" wzorzec, potem docinamy heurystyką
PHONE_RE = re.compile(
    r"\b(?:\+48[-\s]?)?(?:[0-9A-Za-z]{2,3}[-\s]?){2,4}\b"
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IBAN_PL_RE = re.compile(r"\bPL\d{26}\b")
CREDIT_CARD_RE = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
DOC_NUM_RE = re.compile(r"\b(?:[A-Z]{2,4}\d{3,8}|\d{4}-\d{4}-\d{4})\b")

# wiek – dopuszczamy lekkie "śmieci" typu 8G lat
AGE_RE = re.compile(
    r"\b([0-9A-Za-z!]{1,3})\s*(?:lat|r\.ż\.)\b",
    re.IGNORECASE,
)

DATE_NUM_RE = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b")
DATE_WORD_RE = re.compile(r"\b\d{1,2}\s+[a-ząćęłńóśźż]+\s+\d{4}\b", re.IGNORECASE)
ZIP_RE = re.compile(r"\b\d{2}-\d{3}\b")

SEX_RE = re.compile(r"\b(kobieta|mężczyzna|meżczyzna|mężcżyzną|mężczyna)\b", re.IGNORECASE)
RELATIVE_RE = re.compile(
    r"\b(ojciec|tata|matka|mama|brat|siostra|syn|córka|rodzice|dziadek|babcia)\b",
    re.IGNORECASE,
)

# zawód/stanowisko
JOB_TITLE_RE = re.compile(
    r"(?i)\b(?:pracuję\s+jako|pracuje\s+jako|jestem|zawód\s*[:\-]|stanowisko\s*[:\-])\s+([a-ząćęłńóśźż0-9\s\.\-]{3,60})"
)

HEALTH_RE = re.compile(
    r"\b(depresj\w*|alkoholiz\w*|alkoholik\w*|choruj\w*|chorob\w*)\b",
    re.IGNORECASE,
)
RELIGION_RE = re.compile(
    r"\b(katolik\w*|prawosław\w*|protestan\w*|muzułman\w*|ateist\w*)\b",
    re.IGNORECASE,
)
POLITICAL_RE = re.compile(
    r"\b(lewicow\w*|prawicow\w*|libera\w*|konserwaty\w*|socjalist\w*)\b",
    re.IGNORECASE,
)
ETHNICITY_RE = re.compile(
    r"\b(Polak\w*|Niemc\w*|Ukrain\w*|Żyd\w*|Rom\w*)\b",
    re.IGNORECASE,
)
SEXUAL_OR_RE = re.compile(
    r"\b(gej\w*|lesbij\w*|biseksual\w*|heteroseksual\w*)\b",
    re.IGNORECASE,
)
USERNAME_RE = re.compile(r"\B@[A-Za-z0-9_]+\b")
SECRET_RE = re.compile(
    r"\b(hasło|password|passwd|token|api[_-]?key)\b",
    re.IGNORECASE,
)

# Placeholdery z końcówki (name1, email1, phone1, pesel1, document-number1, ...)
PLACEHOLDER_RE = re.compile(
    r"\b(name1|surname1|age1|sex1|city1|address1|email1|phone1|pesel1|document-number1)\b",
    re.IGNORECASE,
)
PLACEHOLDER_MAP: Dict[str, str] = {
    "name1": "NAME",
    "surname1": "SURNAME",
    "age1": "AGE",
    "sex1": "SEX",
    "city1": "CITY",
    "address1": "ADDRESS",
    "email1": "EMAIL",
    "phone1": "PHONE",
    "pesel1": "PESEL",
    "document-number1": "DOCUMENT_NUMBER",
}

# Placeholdery w anonimie ({name}, {pesel}, {phone}, ...)
TEMPLATE_TOKEN_RE = re.compile(
    r"\[(?:name|surname|age|date-of-birth|date|sex|religion|political-view|ethnicity|sexual-orientation|health|"
    r"relative|city|address|email|phone|pesel|document-number|bank-account|credit-card-number|company|school-name|"
    r"job-title|username|secret)\]"
)


def _get_context(text: str, start: int, end: int, radius: int) -> str:
    """Pomocniczo: wytnij fragment kontekstu do heurystyk."""
    ctx_start = max(0, start - radius)
    ctx_end = min(len(text), end + radius)
    return text[ctx_start:ctx_end]


# --- heurystyka: wycinamy DN110 itp. z kontekstu rur, żeby nie traktować tego jak dokument ---
def is_pipe_diameter(text: str, m: re.Match) -> bool:
    """
    Zwraca True dla 'DN110', 'DN80' itp. w kontekście rurociągów
    (rura, PVC, PE, kanalizacja...), aby nie traktować tego jako DOCUMENT_NUMBER.
    """
    span = m.group(0)
    if not re.fullmatch(r"DN\d{2,3}", span):
        return False

    ctx = _get_context(text, m.start(), m.end(), radius=30).lower()
    keywords = [
        "rura", "rurę", "rurą", "rurociąg",
        "kanaliz", "pvc", "pcv", " pe", "ø", "sdr",
        "instalacj", "przyłącz"
    ]
    return any(k in ctx for k in keywords)


def is_health_true_positive(text: str, m: re.Match) -> bool:
    """
    Heurystyka: akceptujemy HEALTH tylko w kontekście zdrowotnym
    (unikamy np. 'lej depresyjny' w hydrogeologii).
    """
    ctx = _get_context(text, m.start(), m.end(), radius=40).lower()
    triggers = [
        "zdiagnoz",        # mam zdiagnozowaną depresję
        "psycholog",       # u psychologa
        "psychiatr",       # u psychiatry
        "terapi",          # terapia
        "leczen",          # leczenie
        "choruję na",      # choruję na ...
        "choruje na",
        "nadcisn",         # nadciśnienie
        "uzależn", "uzalezn",
        "samobój", "samoboj",
        "objaw",
    ]
    return any(t in ctx for t in triggers)


def regex_pii(text: str) -> List[PIIEntity]:
    """
    Wykrywanie PII wyłącznie regexami (PESEL, telefon, email, itd.).
    """
    cands: List[PIIEntity] = []

    def add(_type: str, m: re.Match, score: float = 0.99, group_idx: int = 0) -> None:
        span = m.group(group_idx)
        start = m.start(group_idx)
        end = start + len(span)
        cands.append(
            {
                "type": _type,
                "start": start,
                "end": end,
                "span": span,
                "score": score,
            }
        )

    # PESEL – surowe 11 cyfr
    for m in PESEL_RAW_RE.finditer(text):
        add("PESEL", m, 0.999)

    # PESEL – w kontekście słowa „PESEL”, z możliwymi literówkami / znakami
    for m in PESEL_TAGGED_RE.finditer(text):
        add("PESEL", m, 0.999, group_idx=1)

    # TELEFONY – szeroki kandydat, potem filtrujemy długość i kontekst
    for m in PHONE_RE.finditer(text):
        raw = m.group(0)
        digits = normalize_phone_digits(raw)
        if len(digits) < 7 or len(digits) > 11:
            continue

        # krótkie (7–8 cyfr) tylko w mocnym kontekście telefonicznym
        if len(digits) in (7, 8):
            ctx = _get_context(text, m.start(), m.end(), radius=10).lower()
            if not any(t in ctx for t in ["tel", "telefon", "kom.", "nr tel", "nr. tel", "nr telefonu"]):
                continue

        add("PHONE", m, 0.99)

    for m in EMAIL_RE.finditer(text):
        add("EMAIL", m, 0.99)

    for m in IBAN_PL_RE.finditer(text):
        add("BANK_ACCOUNT", m, 0.999)

    for m in CREDIT_CARD_RE.finditer(text):
        ctx = _get_context(text, m.start(), m.end(), radius=40).lower()
        if "konto" in ctx or "rachunek" in ctx:
            add("BANK_ACCOUNT", m, 0.97)
        else:
            add("CREDIT_CARD_NUMBER", m, 0.97)

    for m in DOC_NUM_RE.finditer(text):
        if is_pipe_diameter(text, m):
            continue
        add("DOCUMENT_NUMBER", m, 0.95)

    for m in AGE_RE.finditer(text):
        add("AGE", m, 0.9)

    for m in DATE_NUM_RE.finditer(text):
        ctx = _get_context(text, m.start(), m.end(), radius=25).lower()
        if "urodz" in ctx or "ur." in ctx:
            add("DATE_OF_BIRTH", m, 0.9)
        else:
            add("DATE", m, 0.85)

    for m in DATE_WORD_RE.finditer(text):
        ctx = _get_context(text, m.start(), m.end(), radius=25).lower()
        if "urodz" in ctx or "ur." in ctx:
            add("DATE_OF_BIRTH", m, 0.9)
        else:
            add("DATE", m, 0.85)

    for m in SEX_RE.finditer(text):
        add("SEX", m, 0.8)

    for m in RELATIVE_RE.finditer(text):
        add("RELATIVE", m, 0.8)

    # Zawód/stanowisko jako JOB_TITLE
    for m in JOB_TITLE_RE.finditer(text):
        add("JOB_TITLE", m, 0.8, group_idx=1)

    for m in HEALTH_RE.finditer(text):
        if not is_health_true_positive(text, m):
            continue
        add("HEALTH", m, 0.8)

    for m in RELIGION_RE.finditer(text):
        add("RELIGION", m, 0.8)

    for m in POLITICAL_RE.finditer(text):
        add("POLITICAL_VIEW", m, 0.8)

    for m in ETHNICITY_RE.finditer(text):
        add("ETHNICITY", m, 0.8)

    for m in SEXUAL_OR_RE.finditer(text):
        add("SEXUAL_ORIENTATION", m, 0.8)

    for m in USERNAME_RE.finditer(text):
        add("USERNAME", m, 0.75)

    for m in SECRET_RE.finditer(text):
        add("SECRET", m, 0.75)

    # Placeholdery (name1, email1, phone1, pesel1, ...)
    for m in PLACEHOLDER_RE.finditer(text):
        key = m.group(1).lower()
        _type = PLACEHOLDER_MAP.get(key)
        if _type:
            add(_type, m, 0.95)

    return cands


# ============================================================
# 3. FastPDN (HerBERT) NER → kandydaci PII + HEURYSTYKI
# ============================================================

def fastpdn_ner_sentence(sent_text: str, sent_start: int) -> List[Dict[str, Any]]:
    """
    NER FastPDN na pojedynczym zdaniu (offsetowanym sent_start).
    """
    outputs = NER_PIPELINE(sent_text)
    ents: List[Dict[str, Any]] = []
    for ent in outputs:
        ents.append(
            {
                "entity_group": ent["entity_group"],  # np. 'nam_liv_person'
                "score": float(ent["score"]),
                "start": sent_start + int(ent["start"]),
                "end": sent_start + int(ent["end"]),
                "span": ent["word"],
            }
        )
    return ents


def map_fastpdn_group_to_internal(group: str) -> str:
    g = group.lower()
    if "person" in g:
        return "PERSON_CAND"
    if "gpe_city" in g:
        return "CITY_CAND"
    if "gpe" in g or "loc" in g:
        return "LOC_CAND"
    if "org" in g:
        return "ORG_CAND"
    return "OTHER"


def is_word_boundary_span(text: str, start: int, end: int) -> bool:
    """
    Czy ent zaczyna/kończy się na granicy słowa
    (żeby nie podmieniać np. 'MI' w 'GMINA').
    """
    left = text[start - 1] if start > 0 else " "
    right = text[end] if end < len(text) else " "
    return (not left.isalpha()) and (not right.isalpha())


def is_reasonable_span(span: str, ent_type: str) -> bool:
    """
    Odrzuć ewidentne śmieci (zbyt krótkie albo nie pasujące do typu).
    """
    s = span.strip()
    # odrzuć ewidentne śmieci typu "A", "Mi", "Na"
    if len(s) < 3 and not any(ch.isdigit() for ch in s):
        return False

    # PERSON / COMPANY / CITY muszą wyglądać jak nazwa własna
    if ent_type in {"PERSON_CAND", "ORG_CAND", "CITY_CAND", "LOC_CAND"}:
        # nie dopuszczaj samych wielkich skrótów 1-2 literowych
        if len(s) <= 2 and s.isupper():
            return False
        # nie dopuszczaj czegoś, co nie ma litery (same cyfry/symbole)
        if not any(ch.isalpha() for ch in s):
            return False

    return True


def filter_person_candidates(doc: spacy.tokens.Doc, candidates: List[PIIEntity]) -> List[PIIEntity]:
    """
    Filtrujemy pseudo-osoby (np. 'Inwestor') będące zwykłymi rzeczownikami.
    """
    filtered: List[PIIEntity] = []
    for c in candidates:
        if c["type"] != "PERSON_CAND":
            filtered.append(c)
            continue

        span = doc.char_span(c["start"], c["end"], alignment_mode="expand")
        if span is None:
            continue

        # pseudo-osoby typu "Inwestor", "Organ", "Spółka" itp.
        if len(span) == 1:
            tok = span[0]
            if tok.pos_ == "NOUN":
                continue

        filtered.append(c)

    return filtered


def classify_location(span: str, context: str) -> str:
    """
    Rozróżnienie CITY vs ADDRESS z użyciem samego spana i kontekstu.
    """
    lower_span = span.lower()
    lower_ctx = context.lower()

    has_number = any(ch.isdigit() for ch in span)
    street_words = [
        "ul.", "ul ", "ulica", "aleja", "al.", "plac", "pl.",
        "alei", "aleję", "placu", "pi.", "pl."
    ]
    has_street = any(w in lower_span for w in street_words)
    has_zip = bool(ZIP_RE.search(span))

    address_triggers = [
        "mieszkam", "adres", "zamieszka", "przy ulicy",
        "pod adresem", "adres to", "plac", "placu"
    ]
    has_address_ctx = any(w in lower_ctx for w in address_triggers)

    if has_number or has_street or has_zip or has_address_ctx:
        return "ADDRESS"
    return "CITY"


def classify_org(span: str, context: str) -> str:
    """
    Prosty podział ORG na SCHOOL_NAME vs COMPANY.
    """
    lower = span.lower()
    school_words = [
        "szkoła", "szkoły", "liceum", "technikum", "uniwersytet",
        "politechnika", "uczelnia", "gimnazjum", "przedszkole",
    ]
    if any(w in lower for w in school_words):
        return "SCHOOL_NAME"
    return "COMPANY"


def split_person_into_name_surname(text: str, ent: PIIEntity) -> List[PIIEntity]:
    """
    Z encji PERSON tworzy osobne encje NAME i SURNAME, jeśli to możliwe.
    Zakładamy prosty przypadek 'Imię Nazwisko' (ew. kilka członów).
    """
    span_text = text[ent["start"]:ent["end"]]
    parts = span_text.strip().split()
    if len(parts) < 2:
        return [ent]

    sub_ents: List[PIIEntity] = []

    # NAME – pierwsze słowo
    name_word = parts[0]
    name_start = text.find(name_word, ent["start"], ent["end"])
    if name_start == -1:
        return [ent]
    name_end = name_start + len(name_word)
    sub_ents.append({
        "type": "NAME",
        "start": name_start,
        "end": name_end,
        "span": name_word,
        "score": ent.get("score", 0.9),
    })

    # SURNAME – ostatnie słowo
    surname_word = parts[-1]
    surname_start = text.rfind(surname_word, name_end, ent["end"])
    if surname_start == -1 or surname_start < name_end:
        return [ent]
    surname_end = surname_start + len(surname_word)

    sub_ents.append({
        "type": "SURNAME",
        "start": surname_start,
        "end": surname_end,
        "span": surname_word,
        "score": ent.get("score", 0.9),
    })

    return sub_ents


def detect_pii(text: str, doc: spacy.tokens.Doc) -> List[PIIEntity]:
    """
    Główne wykrywanie PII:
    - NER FastPDN po zdaniach,
    - mapowanie do typów wewnętrznych,
    - heurystyki (CITY vs ADDRESS, ORG → SCHOOL/COMPANY),
    - regexy,
    - resolucja overlappów.
    """
    # NER na poziomie zdań (stabilne granice, brak twardego cięcia 512 tok.)
    ner_raw: List[Dict[str, Any]] = []
    for sent in doc.sents:
        ner_raw.extend(fastpdn_ner_sentence(sent.text, sent.start_char))

    ner_cands: List[PIIEntity] = []
    for ent in ner_raw:
        base = map_fastpdn_group_to_internal(ent["entity_group"])
        if base == "OTHER" or ent["score"] < 0.5:
            continue

        start, end, span = ent["start"], ent["end"], ent["span"]

        # filtr pod względem długości / sensowności
        if not is_reasonable_span(span, base):
            continue

        # wymuś granice słów dla nazw własnych
        if base in {"PERSON_CAND", "ORG_CAND", "CITY_CAND", "LOC_CAND"}:
            if not is_word_boundary_span(text, start, end):
                continue

        ner_cands.append(
            {
                "type": base,
                "start": start,
                "end": end,
                "span": span,
                "score": ent["score"],
            }
        )

    ner_cands = filter_person_candidates(doc, ner_cands)

    classified_ner: List[PIIEntity] = []
    for c in ner_cands:
        span = c["span"]
        ctx = _get_context(text, c["start"], c["end"], radius=40)
        if c["type"] == "PERSON_CAND":
            c["type"] = "PERSON"
        elif c["type"] in ("CITY_CAND", "LOC_CAND"):
            c["type"] = classify_location(span, ctx)
        elif c["type"] == "ORG_CAND":
            c["type"] = classify_org(span, ctx)
        classified_ner.append(c)

    # Rozbij PERSON na NAME / SURNAME tam, gdzie się da
    expanded_ner: List[PIIEntity] = []
    for c in classified_ner:
        if c["type"] == "PERSON":
            expanded_ner.extend(split_person_into_name_surname(text, c))
        else:
            expanded_ner.append(c)

    regex_cands = regex_pii(text)
    all_cands = expanded_ner + regex_cands
    resolved = resolve_overlaps(all_cands)
    return resolved


# ============================================================
# 4. Resolucja overlappów
# ============================================================

PRIORITY: Dict[str, int] = {
    "PESEL": 100,
    "DOCUMENT_NUMBER": 95,
    "CREDIT_CARD_NUMBER": 90,
    "BANK_ACCOUNT": 85,
    "PHONE": 80,
    "EMAIL": 79,
    "USERNAME": 78,
    "SECRET": 77,
    "DATE_OF_BIRTH": 72,
    "DATE": 70,
    "AGE": 69,
    "ADDRESS": 68,
    "CITY": 67,
    "PERSON": 60,
    "NAME": 59,
    "SURNAME": 58,
    "RELATIVE": 57,
    "COMPANY": 56,
    "SCHOOL_NAME": 55,
    "JOB_TITLE": 54,
    "RELIGION": 50,
    "POLITICAL_VIEW": 49,
    "ETHNICITY": 48,
    "SEXUAL_ORIENTATION": 47,
    "HEALTH": 46,
    "SEX": 45,
}


def _prio(t: str) -> int:
    return PRIORITY.get(t, 0)


def resolve_overlaps(cands: List[PIIEntity]) -> List[PIIEntity]:
    """
    Usuwa nachodzące na siebie encje, zostawiając te o wyższym priorytecie.
    """
    if not cands:
        return []

    sorted_c = sorted(
        cands,
        key=lambda c: (
            c["start"],
            -_prio(c["type"]),
            -(c["end"] - c["start"]),
            -c.get("score", 0.0),
        ),
    )

    result: List[PIIEntity] = []
    for c in sorted_c:
        overlap = False
        for r in result:
            if not (c["end"] <= r["start"] or c["start"] >= r["end"]):
                overlap = True
                break
        if not overlap:
            result.append(c)
    return result


# ============================================================
# 5. Mapowanie typ → token
# ============================================================

ENTITY_TO_TOKEN: Dict[str, str] = {
    # 1. Dane identyfikacyjne osobowe
    "NAME": "[name]",
    "SURNAME": "[surname]",
    "PERSON": "[name} [surname]",
    "AGE": "[age]",
    "DATE_OF_BIRTH": "[date-of-birth]",
    "DATE": "[date]",
    "SEX": "[sex]",
    "RELIGION": "[religion]",
    "POLITICAL_VIEW": "[political-view]",
    "ETHNICITY": "[ethnicity]",
    "SEXUAL_ORIENTATION": "[sexual-orientation]",
    "HEALTH": "[health]",
    "RELATIVE": "[relative]",
    # 2. Dane kontaktowe i lokalizacyjne
    "CITY": "[city]",
    "ADDRESS": "[address]",
    "EMAIL": "[email]",
    "PHONE": "[phone]",
    # 3. Identyfikatory dokumentów i tożsamości
    "PESEL": "[pesel]",
    "DOCUMENT_NUMBER": "[document-number]",
    # 4. Dane zawodowe i edukacyjne
    "COMPANY": "[company]",
    "SCHOOL_NAME": "[school-name]",
    "JOB_TITLE": "[job-title]",
    # 5. Informacje finansowe
    "BANK_ACCOUNT": "[bank-account]",
    "CREDIT_CARD_NUMBER": "[credit-card-number]",
    # 6. Identyfikatory cyfrowe i loginy
    "USERNAME": "[username]",
    "SECRET": "[secret]",
}


def cleanup_templates(text: str) -> str:
    """
    Sprzątanie artefaktów typu '{name} {surname}{name} {surname}'
    zanim polecą do syntetyka.
    """
    # powtarzające się pary {name} {surname}
    text = re.sub(
        r"(\{name\}\s+\{surname\})(\s*\{name\}\s+\{surname\})+",
        r"\1",
        text,
    )
    return text


def anonymize_text(text: str, entities: List[PIIEntity]) -> str:
    """
    Zamienia wykryte encje na placeholdery ({name}, {pesel}, ...).
    """
    entities_sorted = sorted(entities, key=lambda e: e["start"])
    out_parts: List[str] = []
    cursor = 0

    for e in entities_sorted:
        out_parts.append(text[cursor:e["start"]])
        token = ENTITY_TO_TOKEN.get(e["type"])
        if token is None:
            token = text[e["start"]:e["end"]]
        out_parts.append(token)
        cursor = e["end"]

    out_parts.append(text[cursor:])
    text_out = "".join(out_parts)
    text_out = cleanup_templates(text_out)
    return text_out


# ============================================================
# 6. Generator syntetycznych danych
# ============================================================

FIRST_NAMES = ["Jan", "Maria", "Piotr", "Katarzyna", "Michał", "Agnieszka", "Natasza", "Karol"]
LAST_NAMES = ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kamińska", "Lewandowski", "Zieliński"]
CITIES = ["Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław", "Bielsko-Biała"]
STREETS = ["Długa", "Szeroka", "Krótka", "Lipowa", "Polna", "Słoneczna"]
COMPANIES = ["Firma X", "ACME Sp. z o.o.", "TechPol", "InnoSoft"]
SCHOOLS = ["Uniwersytet Warszawski", "Politechnika Wrocławska", "Liceum nr 1"]
JOB_TITLES = ["lekarz", "nauczyciel", "inżynier", "programista"]

RELIGIONS = ["katolik", "ateista", "agnostyk"]
POLITICAL_VIEWS = ["liberał", "konserwatysta", "socjaldemokrata"]
ETHNICITIES = ["Polak", "Ukrainiec", "Niemiec"]
SEXUAL_ORIENTATIONS = ["heteroseksualna", "homoseksualna", "biseksualna"]
HEALTH_STATES = ["choruję na nadciśnienie", "mam zdiagnozowaną depresję"]
RELATIVES = ["mój brat", "moja siostra", "mój ojciec", "moja matka"]


def random_pesel() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(11))


def random_phone() -> str:
    parts = ["".join(str(random.randint(0, 9)) for _ in range(3)) for _ in range(3)]
    return " ".join(parts)


def random_email(first_name: str, last_name: str) -> str:
    local = f"{first_name.lower()}.{last_name.lower()}"
    domain = random.choice(["example.com", "mail.pl", "test.org"])
    return f"{local}@{domain}"


def random_iban_pl() -> str:
    return "PL" + "".join(str(random.randint(0, 9)) for _ in range(26))


def random_credit_card() -> str:
    digits = [str(random.randint(0, 9)) for _ in range(16)]
    return "{}{}{}{} {}{}{}{} {}{}{}{} {}{}{}{}".format(*digits)


def random_document_number() -> str:
    letters = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3))
    digits = "".join(random.choice("0123456789") for _ in range(6))
    return letters + digits


def random_username() -> str:
    base = random.choice(FIRST_NAMES).lower()
    return base + str(random.randint(10, 999))


def random_secret() -> str:
    return "sekret_" + "".join(random.choice("abcdef0123456789") for _ in range(12))


def random_date() -> str:
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    year = random.randint(1970, 2024)
    return f"{day:02d}.{month:02d}.{year}"


def random_age() -> str:
    return f"{random.randint(18, 95)} lat"


def cleanup_synthetic_text(text: str) -> str:
    """
    Dodatkowe sprzątanie po podstawieniu syntetyków – głównie numery telefonów
    sklejone z innymi cyframi/literami.
    """
    # cyfra + telefon -> wstaw spację
    text = re.sub(r"(\d)(\d{3}\s\d{3}\s\d{3})", r"\1 \2", text)
    # litera + telefon -> wstaw spację
    text = re.sub(r"([A-Za-z])(\d{3}\s\d{3}\s\d{3})", r"\1 \2", text)
    return text


def synthesize_text(anonymized: str) -> str:
    """
    Podstawia losowe dane syntetyczne w miejsce placeholderów.
    - per-placeholder generator (żeby nie mieć wszędzie tego samego PESEL/telefonu),
    - ale jeden wspólny sex/age na dokument (mniej sprzeczności).
    """

    # profil "globalny" dla dokumentu
    city_lemma = random.choice(CITIES)
    street_name = random.choice(STREETS)
    company_val = random.choice(COMPANIES)
    school_val = random.choice(SCHOOLS)
    job_val = random.choice(JOB_TITLES)

    sex_val = random.choice(["kobieta", "mężczyzna"])
    age_val = random_age()
    dob_val = random_date()
    date_val = random_date()
    religion_val = random.choice(RELIGIONS)
    pol_view_val = random.choice(POLITICAL_VIEWS)
    ethnicity_val = random.choice(ETHNICITIES)
    orientation_val = random.choice(SEXUAL_ORIENTATIONS)
    health_val = random.choice(HEALTH_STATES)
    relative_val = random.choice(RELATIVES)

    def gen_email() -> str:
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        return random_email(fn, ln)

    def gen_for(token: str) -> str:
        # 1. Dane identyfikacyjne
        if token == "[name]":
            return random.choice(FIRST_NAMES)
        if token == "[surname]":
            return random.choice(LAST_NAMES)
        if token == "[age]":
            return age_val
        if token == "[date-of-birth]":
            return dob_val
        if token == "[date]":
            return date_val
        if token == "[sex]":
            return sex_val
        if token == "[religion]":
            return religion_val
        if token == "[political-view]":
            return pol_view_val
        if token == "[ethnicity]":
            return ethnicity_val
        if token == "[sexual-orientation]":
            return orientation_val
        if token == "[health]":
            return health_val
        if token == "[relative]":
            return relative_val

        # 2. Lokalizacja i kontakt
        if token == "[city]":
            return city_lemma
        if token == "[address]":
            # adres bez powtarzania miasta – miasto będzie osobno
            return f"ulica {street_name} {random.randint(1, 50)}"
        if token == "[email]":
            return gen_email()
        if token == "[phone]":
            return random_phone()

        # 3. Dokumenty i finanse
        if token == "[pesel]":
            return random_pesel()
        if token == "[document-number]":
            return random_document_number()
        if token == "[bank-account]":
            return random_iban_pl()
        if token == "[credit-card-number]":
            return random_credit_card()

        # 4. Loginy / sekrety / praca
        if token == "[company]":
            return company_val
        if token == "[school-name]":
            return school_val
        if token == "[job-title]":
            return job_val
        if token == "[username]":
            return random_username()
        if token == "[secret]":
            return random_secret()

    def repl(m: re.Match) -> str:
        placeholder = m.group(0)
        return gen_for(placeholder)

    text = TEMPLATE_TOKEN_RE.sub(repl, anonymized)

    # Fleksja miasta po 'w' / 'do' – dla jednego, globalnego city_lemma
    text = MORPHO_REALIZER.inflect_city_by_prepositions(text, city_lemma)

    # Dodatkowe sprzątanie po podstawieniu
    text = cleanup_synthetic_text(text)

    return text


# ============================================================
# 7. Główna funkcja pipeline'u
# ============================================================

def run_pipeline(text: str) -> Dict[str, Any]:
    """
    Wejście: surowy tekst z PII.
    Wyjście:
        - doc: obiekt spaCy
        - entities: lista wykrytych encji PII
        - anonymized: tekst z placeholderami {name}, {phone}, ...
        - synthetic: tekst z wylosowanymi, syntetycznymi danymi
    """
    doc = NLP(text)
    entities = detect_pii(text, doc)
    anonymized = anonymize_text(text, entities)
    synthetic = synthesize_text(anonymized)
    return {
        "doc": doc,
        "entities": entities,
        "anonymized": anonymized,
        "synthetic": synthetic,
    }

app = FastAPI()

origins = [
    "http://localhost:5173",  # Twój frontend dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # które domeny mają dostęp
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS itp.
    allow_headers=["*"],  # nagłówki HTTP
)


# definiujesz model danych
class TextRequest(BaseModel):
    text: str  # FastAPI wie, że "text" musi być stringiem


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/anonymize")
def anonymize_text(req: TextRequest):
    text = req.text
    result = run_pipeline(text)
    print("Entities:", result["entities"])
    print("Anonymized:", result["anonymized"])
    print("Synthetic:", result["synthetic"])
    return {
        "textAnonymized": result["anonymized"],
        "textSynthetic": result["synthetic"]
    }
