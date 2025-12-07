## preprocessing.md – Obrabianie danych

### 1. Źródła danych

W projekcie korzystamy **wyłącznie z danych syntetycznych**, generowanych automatycznie na podstawie:

* przygotowanych szablonów językowych,
* słowników encji (imiona, nazwiska, miasta, adresy, instytucje),
* oraz dodatkowych heurystyk zapewniających różnorodność składniową i semantyczną.

Nie wykorzystujemy żadnych danych rzeczywistych, dlatego cały zbiór jest od początku w pełni bezpieczny pod kątem RODO.

### 2. Czyszczenie i standaryzacja danych

Po wygenerowaniu dane przechodzą proces normalizacji obejmujący:

* usuwanie artefaktów formatowania i nadmiarowych spacji,
* normalizację znaków diakrytycznych,
* tokenizację zgodną z pipeline’em HerBERT,
* segmentację na zdania i ujednolicony format sekwencyjny.

Celem jest uzyskanie czystego, jednorodnego zbioru, który może być bezpośrednio użyty w fine-tuningu modelu NER.

### 3. Formatowanie danych do fine-tuningu

Dane syntetyczne są konwertowane do standardowego formatu NER w postaci token–etykieta:

```
Token       Label
Spotkałem   O
się         O
z           O
Kasią       B-PER
w           O
Gdańsku     B-LOC
.           O
```

Każde zdanie zapisujemy w osobnym bloku, oddzielonym pustą linią, dzięki czemu zbiór jest kompatybilny z większością frameworków NER opartych o Transformery.

### 4. Kontrola jakości i walidacja

Wygenerowane dane przechodzą automatyczną walidację obejmującą:

* sprawdzenie poprawności fleksyjnej (odmiana nazw własnych zgodnie z kontekstem),
* sprawdzenie zgodności tagów NER (brak luk, brak nieoznaczonych encji),
* ocenę różnorodności syntaktycznej (różne konstrukcje zdań i warianty semantyczne),
* marker wykrywania potencjalnych konfliktów (np. niepoprawne formy lokatywne).

### 5. Finalny pipeline

1. Generacja szablonów i dobór kategorii encji.
2. Losowanie wartości syntetycznych i ich odmiana morfologiczna.
3. Walidacja poprawności składniowej i etykiet NER.
4. Tokenizacja i konwersja do formatu token–tag.
5. Eksport kompletu danych do procesu fine-tuningu.
