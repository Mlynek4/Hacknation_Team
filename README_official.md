## 1. O projekcie

Nasz system anonimizacji opiera się na **fine-tuningu HerBERT-Large do NER oraz generatorze danych syntetycznych z obsługą fleksji**.
Celem rozwiązania jest precyzyjne usuwanie danych wrażliwych z tekstów przy zachowaniu naturalności składniowej.

---

## 2. Struktura repozytorium

```
├── src/
│   ├── anonymizer.py          # Główny moduł anonimizacji
│   ├── generator.py           # Generator danych syntetycznych
│   ├── inference.py           # Uruchamianie modelu NER
│   └── utils/                 # Pomocnicze skrypty: tokenizacja, fleksja, słowniki
│
├── models/
│   └── herbert_ner/           # Wagi fine-tunowanego modelu (opcjonalnie)
│
├── data/
│   └── dictionaries/          # Słowniki imion, miast, adresów itd.
│
├── output_[nazwa_zespolu].txt                # Wynik anonimizacji (wymagane)
├── performance_[nazwa_zespolu].txt           # Metryki i środowisko (wymagane)
├── preprocessing_[nazwa_zespolu].md          # Opis przetwarzania danych (opcjonalnie)
├── synthetic_generation_[nazwa_zespolu].md   # Generator danych syntetycznych (opcjonalnie)
├── presentation_[nazwa_zespolu].pdf          # Prezentacja (wymagane)
└── Readme.md
```

---

## 3. Jak to działa – opis procesu anonimizacji

1. **Tokenizacja** tekstu zgodnie z pipeline’em HerBERT.
2. **Model NER** (fine-tuning HerBERT-Large) rozpoznaje encje takie jak imię, nazwisko, miasto, adres, PESEL itp.
3. **Anonimizacja** – każde wykryte wyrażenie zostaje zastąpione odpowiednim tokenem `{name}`, `{city}`, `{pesel}`, `{address}` itd.
4. (Opcjonalnie) **Generacja syntetyczna** – narzędzie może odtworzyć pełne zdanie poprzez zamianę tagów na realistyczne, poprawnie odmienione wartości.

---

## 4. Instalacja

### Wymagania

* Python 3.10+
* PyTorch
* Transformers
* Morfeusz 2 (lub inny moduł morfologiczny użyty w projekcie)

### Instalacja

```bash
pip install -r requirements.txt
```

---

## 5. Uruchomienie anonimizacji

### Anonimizacja pliku wejściowego

```bash
python src/anonymizer.py --input input.txt --output output_[nazwa_zespolu].txt
```

### Generacja danych syntetycznych (opcjonalnie)

```bash
python src/generator.py --template templates/example.txt --output synthetic.txt
```

---

## 6. Kontakt / Zespół

**Nazwa zespołu:** *twoja_nazwa_zespolu_bez_polskich_znakow*
Możesz dodać krótką sekcję z członkami zespołu.