## 1. Generowanie danych syntetycznych

### Mechanizm generacji

Dane syntetyczne generujemy poprzez zastępowanie tagów takich jak `{name}`, `{city}` czy `{address}` wartościami pobieranymi z przygotowanych słowników (imiona, nazwiska, miasta, ulice) oraz dodatkowo z modeli językowych, które podpowiadają najbardziej naturalne warianty. Połączenie obu źródeł pozwala uzyskać realizm danych przy zachowaniu pełnej kontrolowalności.

### Walka z fleksją

Kluczowym elementem generacji jest poprawne odmienianie podstawionych słów w zależności od kontekstu zdania. Stosujemy analizator morfologiczny, który:

1. rozpoznaje przypadek i liczbę wymagane przez konstrukcję zdania,
2. odgina nowe słowo do odpowiedniej formy (np. *Radom → Radomiu*, *Kasia → Kasi*).
   Dzięki temu konstrukcje typu:

* **Wejście:** „Mieszkam w {city}.”
* **Sukces:** „Mieszkam w Radomiu.”
  unikaną błędów takich jak „Mieszkam w Radom”.

### Dbałość o sens

Generator uwzględnia strukturę zdań wejściowych – typ encji oraz ich funkcję składniową. Randomizacja nie jest całkowicie losowa: dobór wartości syntetycznych jest ograniczony do semantycznie zgodnych kategorii (np. `{city}` zawsze podmieniany jest na miasto, a `{name}` na imię w odpowiadającej płci, jeśli kontekst ją ujawnia). Pozwala to tworzyć dane, które pozostają realistyczne i zbliżone do oryginalnych pod względem dystrybucji językowej.

### Showcase – przykłady generacji

**1.**
Szablon: *"Spotkałem się z {name} w {city}."*
Wynik: *"Spotkałem się z Kasią w Gdańsku."*

**2.**
Szablon: *"Mój adres to {address}, mieszkam w {city}."*
Wynik: *"Mój adres to ulica Słoneczna 14, mieszkam w Białymstoku."*

**3.**
Szablon: *"Rozmawiałem dziś z {surname} na temat projektu."*
Wynik: *"Rozmawiałem dziś z Kowalczykiem na temat projektu."*

**4.**
Szablon: *"Pracuję razem z {name} {surname} w oddziale w {city}."*
Wynik: *"Pracuję razem z Martą Wójcik w oddziale w Toruniu."*

**5.**
Szablon: *"Jutro jadę do {city} spotkać się z {name}."*
Wynik: *"Jutro jadę do Poznania spotkać się z Pawłem."*