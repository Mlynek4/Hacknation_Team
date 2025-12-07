## 1. O projekcie

Nasz system anonimizacji opiera się na dwóch niezależnie rozwijanych podejściach: fine-tuningu HerBERT-Large do NER oraz systemie regułowym wspomagane AI + deanonimizacja syntetyczna.
Niestety nie starczylo nam czasu na podpiecie modelu HerBERT-Large do frontendu.
![img.png](img.png)
[demo.mp4](demo.mp4)
---

## 2. Struktura repozytorium

```
├── frontend/src/
│   │── api/
│   ├── assets/          # Główny moduł anonimizacji
│   ├── constans/           # Generator danych syntetycznych
│   ├── components           # Uruchamianie modelu NER
│   └── styles/                 # Pomocnicze skrypty: tokenizacja, fleksja, słowniki
│
│── backend/
│   │── main.py                # Generowanie odpowiedzi modelu
│
│
├── dataset/
│   └── anonymizer_values_55k/          # Słowniki imion, miast, adresów itd.
│   └── szablony_zdan/          # Predefiniowane zdania z placeholderami
│   └── output_data/          # Wygenerowany Korpus Syntetyczny (NER)
│
├── output_hallucination_nation.txt                # Wynik anonimizacji (wymagane)
├── performance_hallucination_nation.txt           # Metryki i środowisko (wymagane)
├── preprocessing_hallucination_nation.md          # Opis przetwarzania danych (opcjonalnie)
├── synthetic_generation_hallucination_nation.md   # Generator danych syntetycznych (opcjonalnie)
├── presentation_hallucination_nation.pdf          # Prezentacja (wymagane)
└── Readme.md
```

---

## 3. Jak to działa – opis procesu anonimizacji
Nasz system anonimizacji został zbudowany w oparciu o **dwa równolegle rozwijane podejścia**:

1. **fine-tuning HerBERT-Large do NER**,
2. **metodę regułową wspomaganą AI (Microsoft Presidio + własne rozszerzenia)**.

Z uwagi na ograniczenia czasowe, do wersji demonstracyjnej podłączona została wyłącznie **metoda regułowa**, jednak oba podejścia zostały zaprojektowane, przetestowane i porównane pod kątem jakości anonimizacji.


Proces anonimizacji w finalnym rozwiązaniu działa następująco:

1. **Tekst wejściowy** jest analizowany przez Presidio oraz nasze dodatkowe reguły (RegEx + modele klasyfikacyjne).
2. **Dane wrażliwe** (imię, nazwisko, adres, PESEL itd.) są wykrywane i podmieniane na tokeny zastępcze, np. `{name}`, `{surname}`, `{address}`, `{pesel}`.
3. System może opcjonalnie wykonać **deanonimizację syntetyczną**, czyli ponowne wypełnienie tekstu realistycznymi, losowymi encjami zgodnymi z fleksją języka polskiego.
---

## 4. Instalacja

### Wymagania

Docker Desktop 

### Instalacja

docker-compose up

---

## 5. Linki
Bert fine tuning:
https://colab.research.google.com/drive/1wfSXAJxOqR2JfEMlEA5WX7oK-ywqP6xo#scrollTo=DjbbdCMAztni


## 6. Kontakt / Zespół
**Hallucination Nation**

Jacek Młynarczyk
ICM UW, ML Engineering

Jakub Meixner
MagTop, IF PAN, ML Engineering 

Jakub Bot
PG, Frontend, Backend

Kamil Raubo
PG, ML Engineering


## 7. References
- https://aclanthology.org/2021.bsnlp-1.1/
- https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1585260/full
- https://www.sciencedirect.com/science/article/pii/S0957417425030908

