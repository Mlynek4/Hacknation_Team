# Generowanie danych syntetycznych

W tym rozdziale opisujemy proces zamiany tokenów anonimizacyjnych (np. [name], [city], [pesel]) na losowe, ale sensowne dane syntetyczne. Celem jest uzyskanie tekstów realistycznych, zachowujących strukturę językową oryginału, jednocześnie nie ujawniających żadnych prawdziwych informacji.

---

## 1. Mechanizm generowania

Nowe dane syntetyczne pochodzą głównie z:

- **Słowników i list kontrolowanych** – np. listy imion, nazwisk, miast, ulic, firm, szkół, zawodów, religii, poglądów politycznych, orientacji seksualnej, etniczności i stanów zdrowia.  
- **Losowego generatora liczb** – do tworzenia PESEL, numerów dokumentów, numerów kart kredytowych, kont bankowych, numerów telefonów, dat.  
- **Prostej funkcji formatowania** – np. łączenie imienia i nazwiska w pełną postać, tworzenie adresów w postaci "Miasto przy ulicy X Y".

Całość opiera się na deterministycznej, kontrolowanej randomizacji, dzięki czemu wyniki pozostają realistyczne, ale całkowicie syntetyczne.

---

## 2. Walka z fleksją

Jednym z najważniejszych wyzwań jest poprawna **odmiana słów**, szczególnie nazw miejscowości i imion w kontekście gramatycznym.

- **Problem**: Model widzi zdanie w postaci  
  > "Mieszkam w [city]."  
- **Porażka**: Zastąpienie tokenu bez uwzględnienia odmiany  
  > "Mieszkam w Radom." (niepoprawne gramatycznie)  
- **Sukces**: Zastosowanie modułu Morfeusz2 oraz klasy `MorphoRealizer` umożliwia wygenerowanie poprawnej formy w zależności od kontekstu  
  > "Mieszkam w Radomiu."  

Mechanizm:

1. Token [city] jest zastępowany losowo wybraną nazwą miasta z listy.  
2. MorfoRealizer analizuje kontekst, np. po przyimkach „w”, „do” i generuje poprawną formę fleksyjną (miejscownik, dopełniacz, itp.).  
3. Podobnie można stosować dla imion i nazwisk w zdaniach, gdy wymagane są odmiany (np. „Spotkałem się z [name]” → „Spotkałem się z Kasią”).

Dzięki temu wszystkie dane syntetyczne zachowują **poprawność gramatyczną** i spójność kontekstową.

---

## 3. Dbałość o sens danych

Generacja danych syntetycznych uwzględnia:

- **Zachowanie struktury zdania** – tokeny zamieniane są na dane o tym samym typie i podobnym charakterze (imię → imię, miasto → miasto).  
- **Randomizacja kontrolowana** – nowa wartość nie musi mieć żadnego związku z oryginalnym tekstem, ale pozostaje semantycznie spójna.  
- **Losowanie z list podobnych elementów** – np. dla [job-title] losowane są typowe zawody z listy; dla [health] losowane są realistyczne stany zdrowia.

Takie podejście gwarantuje, że syntetyczne zdania są naturalne, a przy tym całkowicie anonimowe.

---

## 4. Przykłady (Showcase)

Poniżej kilka przykładów konwersji tekstu zanonimizowanego na syntetyczny:

**Przykład 1**  
Szablon (zanonimizowany):  
"Spotkałem się z {name} w {city}."  
Wynik (syntetyczny):  
"Spotkałem się z Kasią w Gdańsku."

**Przykład 2**  
Szablon (zanonimizowany):  
"{name} pracuje w {company} i mieszka przy {address}."  
Wynik (syntetyczny):  
"Piotr Kowalski pracuje w ACME Sp. z o.o. i mieszka przy Wrocławiu przy ulicy Szerokiej 12."

**Przykład 3**  
Szablon (zanonimizowany):  
"Mój PESEL to {pesel} i mój numer telefonu to {phone}."  
Wynik (syntetyczny):  
"Mój PESEL to 82071512345 i mój numer telefonu to 501 234 567."

**Przykład 4**  
Szablon (zanonimizowany):  
"Jestem {sex} i mam {age} lat."  
Wynik (syntetyczny):  
"Jestem kobieta i mam 34 lat."

**Przykład 5**  
Szablon (zanonimizowany):  
"{name} ukończył {school-name} i pracuje jako {job-title}."  
Wynik (syntetyczny):  
"Maria Nowak ukończyła Politechnikę Wrocławską i pracuje jako programista."

---

## 5. Podsumowanie

- Syntetyzacja opiera się na **kontrolowanej losowości** i użyciu **list słownikowych**.  
- Poprawność fleksyjna zapewniona jest przez integrację z **Morfeusz2** i modułem `MorphoRealizer`.  
- Dane są **semantycznie spójne**, zachowują strukturę zdań i typ danych, ale nie zawierają żadnych prawdziwych informacji.  
- Przykłady pokazują, że pipeline działa zarówno dla imion, nazwisk, miast, adresów, jak i danych liczbowych i finansowych.

