# Preprocessing danych  
W tym rozdziale opisujemy cały proces przetwarzania danych wejściowych – od ich wczytania, poprzez czyszczenie oraz wykrywanie wrażliwych informacji (PII), aż po pełną anonimizację. Jest to pierwszy etap pipeline’u prowadzący do późniejszego generowania danych syntetycznych (opisanych osobno w pliku `synthetic_generation.md`).

---

## 1. Cel preprocessingu

Celem modułu preprocessingu jest:

1. **Wykrycie danych wrażliwych (PII)** – takich jak imiona i nazwiska, adresy, PESEL, numery dokumentów, adresy e-mail, dane finansowe, dane dot. zdrowia, poglądów politycznych itp.  
2. **Znormalizowanie tych danych** do ujednoliconych tokenów (np. `"{name}"`, `"{city}"`, `"{pesel}"`…), tak aby możliwe było ich późniejsze zastąpienie treściami syntetycznymi.  
3. **Zachowanie struktury wypowiedzi**, aby syntetyczne dane miały zbliżony rozkład semantyczny i składniowy do danych wejściowych.  

---

## 2. Wykorzystywane narzędzia NLP

Preprocessing wykorzystuje jednocześnie **rule-based** oraz **model-based** metody wykrywania PII.

### 2.1. spaCy – przetwarzanie języka polskiego  
- Załadowany model: `pl_core_news_sm`.  
- Używany do segmentacji tekstu na zdania i tokeny.  
- Pozwala na stabilną ekstrakcję fragmentów tekstu, niezbędną m.in. do użytkowania modeli NER opartych na transformerach.

### 2.2. Morfeusz2 – analizator i generator fleksyjny  
- Wykorzystywany do generowania poprawnych form rzeczowników (głównie nazw miast).  
- Niezwykle istotny dla późniejszego generowania syntetycznych danych, ale już na etapie preprocessingu jest używany pośrednio (np. w rozróżnianiu form lokalnych i dopełniaczowych).

### 2.3. FastPDN (HerBERT NER) – model Transformer do detekcji encji  
- Publiczny model: `clarin-pl/FastPDN`.  
- Używany z `aggregation_strategy="simple"`  
- Wykrywa encje typu **osoba, lokalizacja, organizacja** itp.  
- Wyniki są następnie mapowane na wewnętrzne kategorie PII.

---

## 3. Detekcja PII – łączenie regexów i NER

Wykrywanie danych wrażliwych odbywa się dwutorowo:

---

### 3.1. Reguły oparte o wyrażenia regularne (regex)

System zawiera bogaty zestaw reguł pokrywających m.in.:

- **PESEL**  
- **numery telefonów**  
- **adresy e-mail**  
- **IBAN / konta bankowe**  
- **numery kart kredytowych**  
- **numery dokumentów**  
- **adresy pocztowe (kody pocztowe)**  
- **daty i wiek**  
- **płeć**  
- **informacje o rodzinie, zdrowiu, religii, poglądach politycznych, orientacji, etniczności**  
- **nazwy użytkowników (`@username`)**  
- **tajne dane (hasła, tokeny)**

Każdy dopasowany fragment jest konwertowany na kandydat PII wraz z typem, zakresem i wstępnym score.

---

### 3.2. Detekcja NER oparta o model FastPDN

Proces wygląda następująco:

1. Tekst dzielony jest na zdania spaCy.  
2. Każde zdanie przepuszczane jest przez model NER.  
3. Surowe encje są mapowane na wewnętrzne typy:  
   - `PERSON_CAND`,  
   - `CITY_CAND`, `LOC_CAND`,  
   - `ORG_CAND`.  
4. Wstępna filtracja odrzuca fałszywe osoby (np. rzeczowniki niebędące nazwami własnymi).  
5. Dodatkowe klasyfikatory rule-based dokonują rozróżnień:  
   - `CITY` vs `ADDRESS`,  
   - `COMPANY` vs `SCHOOL_NAME`.

---

## 4. Łączenie obu źródeł PII i rozwiązywanie konfliktów

Po zebraniu kandydatów z regexów i NER:

1. Wszystkie encje trafiają do wspólnej listy.  
2. Występuje **system priorytetów** — np. PESEL ma wyższy priorytet niż PERSON.  
3. Funkcja `resolve_overlaps()` usuwa nachodzące na siebie encje, pozostawiając tę o:
   - wyższym priorytecie,  
   - większym score modelu,  
   - większym zakresie tekstu (w przypadku remisu).  

Dzięki temu nie powstają duplikaty typu:  

```
"Kowalski" -> PERSON
"Kowalski" -> SURNAME
```

Zostaje tylko najbardziej trafna.

---

## 5. Mapowanie typów PII na tokeny anonimizacyjne

Każda encja PII zostaje zamieniona na ujednolicony token, np.:

| Typ PII | Token |
|--------|--------|
| PERSON | `{name} {surname}` |
| CITY | `{city}` |
| EMAIL | `{email}` |
| PESEL | `{pesel}` |
| HEALTH | `{health}` |
| COMPANY | `{company}` |
| ADDRESS | `{address}` |

Tokenizacja zachowuje strukturę tekstu.  
Zanonimizowana wersja nie zawiera już żadnych danych osobowych.

---

## 6. Tworzenie wersji zanonimizowanej

Funkcja `anonymize_text()`:

1. Sortuje encje rosnąco po początku zakresu.  
2. Buduje wynikowy tekst, wstawiając tokeny w miejsce oryginalnych danych.  
3. Zachowuje wszystkie pozostałe słowa nienaruszone.

Przykład:

> "Nazywam się Jan Kowalski i mieszkam w Warszawie."  
→  
> "Nazywam się {name} {surname} i mieszkam w {address}."

To właśnie tę postać tekstu wykorzystujemy później do generacji syntetycznej.

---

## 7. Główna funkcja pipeline’u

Funkcja `run_pipeline(text)` przeprowadza cały proces:

1. Przetwarzanie tekstu spaCy.  
2. Detekcja encji PII.  
3. Anonimizacja (zamiana na tokeny).  
4. Przekazanie teksu dalej – do generatora syntetycznego.

Zwracane są:  
- dokument spaCy,  
- lista wykrytych encji,  
- tekst zanonimizowany,  
- tekst po generacji syntetycznej (opisany osobno).

---

## 8. Podsumowanie

Preprocessing:

- **wykrywa**,  
- **kategoryzuje**,  
- **czyści**,  
- **marca**,  
- **tokenizuje**  

wszystkie dane wrażliwe, przygotowując je do dalszego etapu generacji syntetycznej.  
Stanowi fundament całego pipeline’u, zapewniając bezpieczeństwo danych oraz spójność formatu wejściowego dla kolejnych modułów.
