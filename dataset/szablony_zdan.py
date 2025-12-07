import random
import csv
from tqdm import tqdm
from typing import List, Dict
import re

# SEED = 20251206
# random.seed(SEED)

TARGET = 3000 
OUTPUT_FILE = "szablony_zdan.csv"
# Ustawienia
TARGET_COUNT_PER_PH = 20

# ----- PLACEHOLDERS -----
PH = {
    "NAME": "[name]",
    "SURNAME": "[surname]",
    "FULLNAME": "[name] [surname]",
    "AGE": "[age]",
    "DOB": "[date-of-birth]",
    "DATE": "[date]",
    "CITY": "[city]",
    "ADDRESS": "[address]",
    "PHONE": "[phone]",
    "EMAIL": "[email]",
    "PESEL": "[pesel]",
    "DOCNR": "[document-number]",
    "COMPANY": "[company]",
    "SCHOOL": "[school-name]",
    "JOB": "[job-title]",
    "BANK": "[bank-account]",
    "CARD": "[credit-card-number]",
    "USERNAME": "[username]",
    "REL": "[relative]",
    "HEALTH": "[health]",
    "SECRET": "[secret]",
    "SEX": "[sex]", 
    "RELIGION": "[religion]",
    "POLITICAL-VIEW": "[political-view]",
    "ETHNICITY": "[ethnicity]",
    "SEXUAL-ORIENTATION": "[sexual-orientation]"
}

# -------------------------------------------------------------------
# MAPA ZBALANSOWANYCH SZABLONÓW (15 unikalnych na każdy PH)
# -------------------------------------------------------------------
FULL_TEMPLATE_MAP = {
    "NAME": [
        f"Imię {PH['NAME']} jest kluczowym elementem identyfikacji w systemie.",
        f"Wprowadzono imię {PH['NAME']} do bazy klientów w dniu {PH['DATE']}.",
        f"Zapisano, że {PH['NAME']} ma drugie imię {PH['NAME']}.",
        f"Dokument {PH['DOCNR']} wystawiono na imię {PH['NAME']} {PH['SURNAME']}.",
        f"Pani {PH['NAME']} pracuje jako {PH['JOB']} w firmie {PH['COMPANY']}.",
        f"Kontakt telefoniczny z {PH['NAME']} pod numerem {PH['PHONE']} jest niemożliwy.",
        f"Zweryfikowano imię {PH['NAME']} na podstawie numeru {PH['PESEL']}.",
        f"Sprawa {PH['DOCNR']} dotyczy {PH['NAME']} i jego krewnego {PH['REL']}.",
        f"Wiek {PH['AGE']} osoby o imieniu {PH['NAME']} to {PH['AGE']} lat.",
        f"Adres e-mail {PH['EMAIL']} jest powiązany z {PH['NAME']} w {PH['CITY']}.",
        f"Przelew na konto {PH['BANK']} dla {PH['NAME']} {PH['SURNAME']} został zatwierdzony.",
        f"Pacjent {PH['NAME']} {PH['SURNAME']} ma problem {PH['HEALTH']} i płeć {PH['SEX']}.",
        f"W systemie figuruje login {PH['USERNAME']} dla {PH['NAME']} z hasłem {PH['SECRET']}.",
        f"Wyznanie {PH['RELIGION']} i {PH['POLITICAL-VIEW']} są przypisane do osoby {PH['NAME']}.",
        f"Osoba o imieniu {PH['NAME']} urodziła się w dniu {PH['DOB']}."
    ],
    "SURNAME": [
        f"Nazwisko {PH['SURNAME']} jest głównym kryterium wyszukiwania w rejestrze.",
        f"Urzędnik potwierdza, że rodzina o nazwisku {PH['SURNAME']} figuruje w rejestrze {PH['CITY']}.",
        f"W akcie urodzenia widnieje {PH['NAME']} {PH['SURNAME']} ur. {PH['DOB']}.",
        f"Zlecono sprawdzenie adresu {PH['ADDRESS']} dla rodziny {PH['SURNAME']} w dniu {PH['DATE']}.",
        f"Pani {PH['NAME']} {PH['SURNAME']} pracuje jako {PH['JOB']} w {PH['COMPANY']} na podstawie {PH['DOCNR']}.",
        f"Zarejestrowano nazwisko {PH['SURNAME']} w systemie {PH['USERNAME']} pod adresem {PH['EMAIL']}.",
        f"Zweryfikowano nazwisko {PH['SURNAME']} na podstawie PESEL {PH['PESEL']}.",
        f"Sprawa {PH['DOCNR']} dotyczy {PH['NAME']} i {PH['SURNAME']} mieszkających w {PH['ADDRESS']}.",
        f"Wiek {PH['AGE']} osoby o nazwisku {PH['SURNAME']} ma znaczenie historyczne.",
        f"Księgowy kontaktuje się z {PH['NAME']} {PH['SURNAME']} w sprawie zaległości na koncie {PH['BANK']}.",
        f"Pacjent {PH['NAME']} {PH['SURNAME']} ma problem {PH['HEALTH']} i pochodzenie {PH['ETHNICITY']}.",
        f"Pani {PH['SURNAME']} opuściła {PH['SCHOOL']} w wieku {PH['AGE']}.",
        f"Poglądy {PH['POLITICAL-VIEW']} są przypisane do {PH['SURNAME']} i {PH['RELIGION']}.",
        f"Zażądano podania nazwiska {PH['SURNAME']} w związku z użyciem karty {PH['CARD']}.",
        f"Nazwisko {PH['SURNAME']} jest powiązane z krewnym {PH['REL']}."
    ],
    "FULLNAME": [
        f"Potwierdzenie tożsamości osoby: {PH['FULLNAME']} na podstawie {PH['DOCNR']}.",
        f"Osoba {PH['FULLNAME']} ma {PH['AGE']} lat i mieszka w {PH['CITY']} pod adresem {PH['ADDRESS']}.",
        f"Dokumentacja **wskazuje**, że {PH['FULLNAME']} **jest objęty** ochroną ze względu na {PH['SEXUAL-ORIENTATION']}.",
        f"W trakcie wywiadu {PH['FULLNAME']} **oświadczył**, że jest płci {PH['SEX']} i wyznania {PH['RELIGION']}.",
        f"Klient {PH['FULLNAME']} **zażądał** zwrotu środków na konto {PH['BANK']} w dniu {PH['DATE']}.",
        f"Inspektor **sprawdził** tożsamość {PH['FULLNAME']} (PESEL {PH['PESEL']}).",
        f"Pełnomocnik {PH['FULLNAME']} **przedstawił** nowy adres {PH['ADDRESS']} i numer {PH['PHONE']}.",
        f"Firma {PH['COMPANY']} **zatrudnia** {PH['FULLNAME']} na stanowisku {PH['JOB']} od {PH['DOB']}.",
        f"Księgowy **skontaktował się** z {PH['FULLNAME']} na adres {PH['EMAIL']} w sprawie {PH['CARD']}.",
        f"**Wydano** zaświadczenie numer {PH['DOCNR']} dla {PH['FULLNAME']} w dniu {PH['DATE']}.",
        f"{PH['FULLNAME']} **awansował** ze stanowiska {PH['JOB']} i **otrzymał** nowe uprawnienia.",
        f"Dane {PH['FULLNAME']} i numer {PH['PHONE']} są w aktach sprawy z kluczem {PH['SECRET']}.",
        f"**Zgłoszono** podejrzenie, że {PH['REL']} jest krewnym {PH['FULLNAME']} w {PH['SCHOOL']}.",
        f"Konto {PH['USERNAME']} i klucz {PH['SECRET']} należą do {PH['FULLNAME']} (wiek {PH['AGE']}).",
        f"W związku z {PH['HEALTH']}, {PH['FULLNAME']} **wskazał** wiek {PH['AGE']} i pochodzenie {PH['ETHNICITY']}."
    ],
    "AGE": [
        f"Wiek {PH['AGE']} jest kluczowy w kontekście świadczeń medycznych ({PH['HEALTH']}).",
        f"Umowa została podpisana w dniu {PH['DATE']} przez osobę w wieku {PH['AGE']} lat.",
        f"Weryfikacja wieku {PH['AGE']} jest wymagana do dostępu do konta {PH['USERNAME']}.",
        f"Rekrutacja do {PH['SCHOOL']} jest możliwa dla osób w wieku {PH['AGE']}.",
        f"Osoba mająca {PH['AGE']} lat podała zły numer karty {PH['CARD']}.",
        f"Wiek {PH['AGE']} ma znaczenie w kontekście poglądów {PH['POLITICAL-VIEW']} i wyznania {PH['RELIGION']}.",
        f"PESEL {PH['PESEL']} potwierdza wiek {PH['AGE']} i płeć {PH['SEX']}.",
        f"Doświadczenie zawodowe jako {PH['JOB']} wymagane jest od wieku {PH['AGE']}.",
        f"Pacjent {PH['FULLNAME']} w wieku {PH['AGE']} zgłosił {PH['HEALTH']} w {PH['CITY']}.",
        f"Wiek {PH['AGE']} jest powiązany z datą urodzenia {PH['DOB']} i adresem {PH['ADDRESS']}.",
        f"Osoba w wieku {PH['AGE']} **wniosła** o wydanie duplikatu dokumentu {PH['DOCNR']}.",
        f"Minimalny wiek {PH['AGE']} jest wymagany do otwarcia konta {PH['BANK']} w firmie {PH['COMPANY']}.",
        f"Zgodnie z protokołem, wiek {PH['AGE']} krewnego {PH['REL']} został odnotowany.",
        f"Wiek {PH['AGE']} i pochodzenie {PH['ETHNICITY']} są danymi statystycznymi.",
        f"Klient w wieku {PH['AGE']} skontaktował się z {PH['PHONE']}."
    ],
    "DOB": [
        f"Data urodzenia {PH['DOB']} jest niezbędna do weryfikacji PESEL {PH['PESEL']}.",
        f"Potwierdza się, że data urodzenia {PH['DOB']} jest zgodna z {PH['DOCNR']}.",
        f"W akcie urodzenia widnieje {PH['NAME']} {PH['SURNAME']} ur. {PH['DOB']}.",
        f"Wójt gminy **rozpatruje** prośbę **dotyczącą** zmiany daty urodzenia {PH['DOB']}.",
        f"W związku z {PH['HEALTH']}, {PH['FULLNAME']} **wskazał** datę urodzenia {PH['DOB']} jako dane krytyczne.",
        f"Data {PH['DOB']} jest powiązana z wiekiem {PH['AGE']} i adresem {PH['ADDRESS']} w {PH['CITY']}.",
        f"Zeznanie {PH['REL']} **kwestionuje** datę urodzenia {PH['DOB']} swojego brata {PH['NAME']}.",
        f"**Przetwarzano** dane dotyczące daty urodzenia {PH['DOB']} osoby {PH['FULLNAME']}.",
        f"Wydanie karty {PH['CARD']} wymaga podania daty urodzenia {PH['DOB']}.",
        f"Data {PH['DOB']} została przekazana do działu HR w {PH['COMPANY']} wraz z informacją o wieku {PH['AGE']}.",
        f"Weryfikacja daty urodzenia {PH['DOB']} jest wymagana do dostępu do konta {PH['USERNAME']}.",
        f"Przelew na konto {PH['BANK']} dla {PH['FULLNAME']} został zrealizowany po weryfikacji {PH['DOB']}.",
        f"Data {PH['DOB']} jest chroniona kluczem {PH['SECRET']} i adresem {PH['EMAIL']}.",
        f"Osoba urodzona {PH['DOB']} **wyznaje** {PH['RELIGION']} i ma poglądy {PH['POLITICAL-VIEW']}.",
        f"Dokumenty z {PH['SCHOOL']} potwierdzają datę urodzenia {PH['DOB']}."
    ],
    "DATE": [
        f"Ostatnia aktywność na koncie {PH['BANK']} została odnotowana w dniu {PH['DATE']}.",
        f"Ostatnia aktualizacja nastąpiła w dniu {PH['DATE']}, co potwierdza {PH['DOCNR']}.",
        f"Termin płatności za fakturę upływa w dniu {PH['DATE']}.",
        f"Karta płatnicza {PH['CARD']} **została zablokowana** w dniu {PH['DATE']} po próbie transakcji.",
        f"Burmistrz **nakazał** {PH['FULLNAME']} **uzupełnić** wniosek do dnia {PH['DATE']}.",
        f"**Otrzymano** potwierdzenie płatności kartą {PH['CARD']} dla użytkownika {PH['USERNAME']} w dniu {PH['DATE']}.",
        f"**Zażądano** numeru telefonu {PH['PHONE']} w kontekście historycznych danych medycznych z {PH['DATE']}.",
        f"**Wydano** zaświadczenie numer {PH['DOCNR']} dla {PH['FULLNAME']} w dniu {PH['DATE']}.",
        f"**Skorygowano** numer dokumentu {PH['DOCNR']} oraz **zaktualizowano** datę {PH['DATE']} na dokumencie.",
        f"Decyzja **wchodzi w życie** z dniem jej ogłoszenia ({PH['DATE']}) i dotyczy adresu {PH['ADDRESS']}.",
        f"Firma {PH['COMPANY']} **zatrudnia** {PH['FULLNAME']} od {PH['DATE']} (wiek {PH['AGE']}).",
        f"**Wystawiono** certyfikat potwierdzający pracę do dnia {PH['DATE']} na stanowisku {PH['JOB']}.",
        f"Zgłoszenie e-mail {PH['EMAIL']} zostało wysłane w dniu {PH['DATE']} z {PH['CITY']}.",
        f"**Zarejestrowano** nowy numer PESEL: {PH['PESEL']} w bazie danych z uwzględnieniem daty {PH['DATE']}.",
        f"Pani {PH['NAME']} opuściła {PH['SCHOOL']} w dniu {PH['DATE']}."
    ],
    "CITY": [
        f"Firma {PH['COMPANY']} ma swoją siedzibę w mieście {PH['CITY']}.",
        f"Adres korespondencyjny znajduje się w mieście {PH['CITY']}.",
        f"**Monitoruje się** stan {PH['HEALTH']} u osoby zamieszkałej w {PH['CITY']}.",
        f"Adres zamieszkania to: {PH['ADDRESS']} w {PH['CITY']}.",
        f"**Przekazano** numer karty {PH['CARD']} do działu bezpieczeństwa po **wykryciu** użycia go w {PH['CITY']}.",
        f"Decyzja **zostanie podjęta** w terminie 14 dni roboczych od daty {PH['DATE']}, co ogłoszono w Biuletynie {PH['CITY']}.",
        f"Sprawa **została przekazana** do archiwizacji i będzie dostępna do wglądu w Urzędzie Miasta {PH['CITY']}.",
        f"Inspektor **sprawdził** tożsamość {PH['FULLNAME']} i **zarejestrował** {PH['CITY']}.",
        f"**Zobowiązuje się** {PH['FULLNAME']} do dostarczenia zaświadczenia o zatrudnieniu w {PH['COMPANY']} w {PH['CITY']}.",
        f"**Zlecono** kontrolę adresu {PH['ADDRESS']} {PH['CITY']} po otrzymaniu zgłoszenia od {PH['REL']}.",
        f"W urzędzie **odrzucono** wniosek z powodu braków w adresie {PH['ADDRESS']} {PH['CITY']}.",
        f"Pacjent {PH['NAME']} z {PH['CITY']} ma PESEL {PH['PESEL']}.",
        f"W {PH['CITY']} odbył się zjazd osób o pochodzeniu {PH['ETHNICITY']}.",
        f"Skontaktowano się z {PH['PHONE']} z regionu {PH['CITY']}.",
        f"Wiek {PH['AGE']} osoby z {PH['CITY']} jest w aktach sprawy."
    ],
    "ADDRESS": [
        f"Wysłano wezwanie pod adres {PH['ADDRESS']} (dokument {PH['DOCNR']}).",
        f"Adres zamieszkania to: {PH['ADDRESS']} w {PH['CITY']}.",
        f"**Zaktualizowano** adres {PH['ADDRESS']} w systemie po **potwierdzeniu** tożsamości numerem PESEL {PH['PESEL']}.",
        f"Pełnomocnik {PH['FULLNAME']} **przedstawił** nowy adres do korespondencji {PH['ADDRESS']}.",
        f"**Zlecono** kontrolę adresu {PH['ADDRESS']} {PH['CITY']} po **otrzymaniu** zgłoszenia od {PH['REL']}.",
        f"**Odnotowano** zmianę adresu zamieszkania dla osoby {PH['FULLNAME']} na: {PH['ADDRESS']}.",
        f"W terminie 7 dni **przysługuje** odwołanie za pośrednictwem adresu: {PH['ADDRESS']}.",
        f"Decyzja **wchodzi w życie** z dniem jej ogłoszenia i dotyczy adresu {PH['ADDRESS']}.",
        f"Numer telefonu {PH['PHONE']} jest powiązany z adresem {PH['ADDRESS']}.",
        f"Adres {PH['ADDRESS']} należy do osoby płci {PH['SEX']} (wiek {PH['AGE']}).",
        f"Dokument **odnosi się** do {PH['SEXUAL-ORIENTATION']} osoby zamieszkałej pod adresem {PH['ADDRESS']}.",
        f"**Przyjęto** do wiadomości oświadczenie o nowym adresie korespondencyjnym {PH['ADDRESS']} (email: {PH['EMAIL']}).",
        f"W urzędzie **odrzucono** wniosek z powodu braków w adresie {PH['ADDRESS']} {PH['CITY']}.",
        f"Użycie klucza {PH['SECRET']} odnotowano pod adresem {PH['ADDRESS']} w dniu {PH['DATE']}.",
        f"Zmieniono dane na karcie {PH['CARD']} powiązane z adresem {PH['ADDRESS']}."
    ],
    "PHONE": [
        f"Proszę o kontakt telefoniczny pod numerem {PH['PHONE']} po godzinie {PH['DATE']}.",
        f"Kontakt telefoniczny pod numerem {PH['PHONE']} jest kluczowy dla sprawy {PH['DOCNR']}.",
        f"Pisemne **potwierdzenie** doręczenia jest dostępne pod numerem {PH['PHONE']} w Urzędzie.",
        f"Klient **podał** dane kontaktowe {PH['PHONE']} i {PH['EMAIL']} w związku z historią zdrowotną {PH['HEALTH']}.",
        f"**Zażądano** numeru telefonu {PH['PHONE']} w kontekście historycznych danych medycznych z {PH['DATE']}.",
        f"**Zaleca się** kontakt mailowy na adres {PH['EMAIL']} lub telefoniczny {PH['PHONE']} w celu omówienia dalszych kroków.",
        f"Pełnomocnik {PH['FULLNAME']} **przedstawił** numer telefonu {PH['PHONE']} do kontaktu.",
        f"Sprawę **prowadzi** urzędnik {PH['FULLNAME']}, kontakt telefoniczny pod numerem {PH['PHONE']}.",
        f"**Ustalono**, że adres {PH['ADDRESS']} jest zbieżny z podanym numerem {PH['PHONE']}.",
        f"W związku z koniecznością **prowadzenia** spraw, {PH['FULLNAME']} **prosi** o kontakt na {PH['PHONE']}.",
        f"**Wprowadzono** nowy numer dokumentu {PH['DOCNR']} oraz **zaktualizowano** numer telefonu {PH['PHONE']}.",
        f"Profesor {PH['FULLNAME']} **wykłada** w {PH['SCHOOL']} i **podał** swój numer telefonu {PH['PHONE']} do kontaktu.",
        f"Zarejestrowano numer {PH['PHONE']} jako dane do **weryfikacji** transakcji {PH['BANK']}.",
        f"Klient w wieku {PH['AGE']} skontaktował się z {PH['PHONE']} w sprawie {PH['CARD']}.",
        f"Numer {PH['PHONE']} należy do krewnego {PH['REL']} mieszkającego w {PH['CITY']}."
    ],
    "EMAIL": [
        f"Zaleca się kontakt mailowy na adres {PH['EMAIL']} w celu omówienia dalszych kroków.",
        f"Kontakt elektroniczny pod adresem {PH['EMAIL']} jest w aktach sprawy {PH['DOCNR']}.",
        f"Klient **podał** dane kontaktowe {PH['PHONE']} i {PH['EMAIL']} w związku z historią zdrowotną {PH['HEALTH']}.",
        f"**Wykryto**, że {PH['FULLNAME']} **użył** służbowego e-maila {PH['EMAIL']} do **zapisania** numeru karty {PH['CARD']}.",
        f"Administrator **odblokował** konto {PH['USERNAME']} i **wysłał** nowe hasło na adres {PH['EMAIL']}.",
        f"**Zobowiązuje się** stronę {PH['FULLNAME']} do **uzupełnienia** braków formalnych, przesyłając je na adres {PH['EMAIL']}.",
        f"Wniosek **został uzupełniony** przez {PH['FULLNAME']} po kontakcie mailowym {PH['EMAIL']} w dniu {PH['DATE']}.",
        f"**Zgłoszenie** wymaga podania adresu e-mail {PH['EMAIL']} i **potwierdzenia** tożsamości numerem {PH['PESEL']}.",
        f"Księgowy **skontaktował się** z {PH['FULLNAME']} na adres {PH['EMAIL']} w sprawie wynagrodzenia na konto {PH['BANK']}.",
        f"**Zarejestrowano** adres {PH['EMAIL']} i numer telefonu {PH['PHONE']} jako dane do **weryfikacji** transakcji.",
        f"Adres {PH['EMAIL']} jest identyfikatorem konta {PH['USERNAME']} w firmie {PH['COMPANY']}.",
        f"Adres e-mail {PH['EMAIL']} jest powiązany z adresem zamieszkania {PH['ADDRESS']} w {PH['CITY']}.",
        f"W związku z koniecznością **prowadzenia** spraw, {PH['FULLNAME']} **prosi** o kontakt na {PH['EMAIL']}.",
        f"Adres {PH['EMAIL']} został podany przez krewnego {PH['REL']} (wiek {PH['AGE']}).",
        f"Zapisano, że adres {PH['EMAIL']} jest chroniony kluczem {PH['SECRET']}."
    ],
    "PESEL": [
        f"Wprowadzono numer identyfikacyjny PESEL: {PH['PESEL']} w dniu {PH['DATE']}.",
        f"**Zaktualizowano** adres {PH['ADDRESS']} w systemie po **potwierdzeniu** tożsamości numerem PESEL {PH['PESEL']}.",
        f"Sprawa **dotyczy** orientacji {PH['SEXUAL-ORIENTATION']} oraz numeru PESEL: {PH['PESEL']}.",
        f"Inspektor **sprawdził** tożsamość {PH['FULLNAME']} (PESEL {PH['PESEL']}) i **zarejestrował** adres.",
        f"Wójt gminy **rozpatruje** prośbę **dotyczącą** zmiany daty urodzenia {PH['DOB']} i numeru PESEL {PH['PESEL']}.",
        f"**Odmówiono** ujawnienia PESEL {PH['PESEL']} ze względu na wrażliwość danych {PH['HEALTH']}.",
        f"Bank **odrzucił** wniosek {PH['FULLNAME']} o kredyt po **sprawdzeniu** numeru {PH['PESEL']}.",
        f"Uczelnia {PH['SCHOOL']} **przyznała** {PH['FULLNAME']} numer identyfikacyjny {PH['PESEL']} do celów rekrutacyjnych.",
        f"**Zarejestrowano** nowy numer PESEL: {PH['PESEL']} w bazie danych z uwzględnieniem daty {PH['DATE']}.",
        f"Zgłoszenie **wymaga** podania adresu e-mail {PH['EMAIL']} i **potwierdzenia** tożsamości numerem {PH['PESEL']}.",
        f"Numer {PH['PESEL']} jest chroniony kluczem {PH['SECRET']} i powiązany z kontem {PH['BANK']}.",
        f"PESEL {PH['PESEL']} potwierdza wiek {PH['AGE']} i płeć {PH['SEX']} osoby {PH['NAME']}.",
        f"Numer {PH['PESEL']} jest wymagany do podjęcia pracy jako {PH['JOB']} w firmie {PH['COMPANY']}.",
        f"W systemie medycznym numer {PH['PESEL']} służy do identyfikacji stanu {PH['HEALTH']}.",
        f"Numer PESEL {PH['PESEL']} został podany przez krewnego {PH['REL']} w {PH['CITY']}."
    ],
    "DOCNR": [
        f"Numer referencyjny dokumentu to: {PH['DOCNR']} i dotyczy sprawy {PH['FULLNAME']}.",
        f"**Wprowadzono** nowy numer dokumentu {PH['DOCNR']} oraz **zaktualizowano** numer telefonu {PH['PHONE']}.",
        f"Burmistrz **nakazał** {PH['FULLNAME']} **uzupełnić** wniosek (nr {PH['DOCNR']}) do dnia {PH['DATE']}.",
        f"**Wydano** zaświadczenie numer {PH['DOCNR']} dla {PH['FULLNAME']} w dniu {PH['DATE']}, **potwierdzające** wiek {PH['AGE']}.",
        f"**Skorygowano** numer dokumentu {PH['DOCNR']} oraz **zaktualizowano** datę {PH['DATE']} na dokumencie powiązanym.",
        f"W urzędzie **odrzucono** wniosek {PH['DOCNR']} **złożony** przez {PH['FULLNAME']} z powodu braków w adresie {PH['ADDRESS']}.",
        f"**Sprawdzono** poprawność numeru identyfikacyjnego {PH['DOCNR']} w Centralnym Rejestrze Danych Administracyjnych.",
        f"Postępowanie **nie wymaga** dalszych czynności i zostaje zamknięte z dniem {PH['DATE']} pod numerem {PH['DOCNR']}.",
        f"{PH['FULLNAME']} **awansował** i **otrzymał** nowe uprawnienia (numer {PH['DOCNR']}).",
        f"**Wystawiono** certyfikat numer {PH['DOCNR']} potwierdzający, że {PH['FULLNAME']} **pracował** na stanowisku {PH['JOB']}.",
        f"**Odnotowano**, że dokument {PH['DOCNR']} **zawierał** sprzeczne informacje na temat stanu {PH['HEALTH']}.",
        f"Wprowadzono ostateczną adnotację w rejestrze pod numerem {PH['DOCNR']} dotyczącą osoby {PH['FULLNAME']}.",
        f"Petent {PH['FULLNAME']} **wniósł** o wydanie duplikatu dokumentu {PH['DOCNR']} w związku ze zmianą adresu.",
        f"Numer referencyjny dokumentu {PH['DOCNR']} jest powiązany z PESEL {PH['PESEL']} i kluczem {PH['SECRET']}.",
        f"Numer {PH['DOCNR']} jest wymagany do uzyskania dostępu do konta {PH['USERNAME']} w firmie {PH['COMPANY']}."
    ],
    "COMPANY": [
        f"Obecny pracodawca to {PH['COMPANY']}, z siedzibą w {PH['CITY']}.",
        f"Klient {PH['FULLNAME']} **zażądał** zwrotu środków po **wykryciu** wycieku danych z firmy {PH['COMPANY']}.",
        f"Firma {PH['COMPANY']} **zatrudnia** {PH['FULLNAME']} na stanowisku {PH['JOB']} od {PH['DATE']}.",
        f"Inspektor {PH['FULLNAME']} **nadzoruje** projekt w {PH['COMPANY']} i **wymaga** klucza {PH['SECRET']}.",
        f"System **wygenerował** tymczasowy klucz API {PH['SECRET']} dla pracownika {PH['FULLNAME']} z firmy {PH['COMPANY']}.",
        f"**Zobowiązuje się** {PH['FULLNAME']} do dostarczenia zaświadczenia o zatrudnieniu w {PH['COMPANY']} na stanowisku {PH['JOB']}.",
        f"Zgłoszenie **wymaga** dostarczenia dokumentacji (nr {PH['DOCNR']}) przez podmiot {PH['COMPANY']}.",
        f"Brak reakcji ze strony {PH['COMPANY']} jest niedopuszczalny (email: {PH['EMAIL']}).",
        f"Konto bankowe {PH['BANK']} należy do firmy {PH['COMPANY']}.",
        f"**Przekazano** dane {PH['FULLNAME']} do działu HR w {PH['COMPANY']} wraz z informacją o wieku {PH['AGE']}.",
        f"Wymagany jest klucz {PH['SECRET']} do weryfikacji konta pracownika {PH['USERNAME']} w {PH['COMPANY']}.",
        f"Pracownik firmy {PH['COMPANY']} zgłosił urlop z powodu {PH['HEALTH']} (PESEL {PH['PESEL']}).",
        f"Całość dokumentacji **została zdigitalizowana** i przekazana do {PH['COMPANY']} w dniu {PH['DATE']}.",
        f"Firma {PH['COMPANY']} odnotowała pochodzenie {PH['ETHNICITY']} pracownika {PH['NAME']}.",
        f"Zarejestrowano adres {PH['ADDRESS']} jako siedzibę firmy {PH['COMPANY']}."
    ],
    "SCHOOL": [
        f"Osoba uczęszczała do {PH['SCHOOL']} w wieku {PH['AGE']}.",
        f"Po **ukończeniu** {PH['SCHOOL']}, {PH['FULLNAME']} **podjął** pracę jako {PH['JOB']} w {PH['COMPANY']}.",
        f"Profesor {PH['FULLNAME']} **wykłada** w {PH['SCHOOL']} i **podał** swój numer telefonu {PH['PHONE']}.",
        f"Uczelnia {PH['SCHOOL']} **przyznała** {PH['FULLNAME']} numer identyfikacyjny {PH['PESEL']} do celów rekrutacyjnych.",
        f"Student {PH['FULLNAME']} **złożył** podanie o urlop dziekański w {PH['SCHOOL']} z powodu {PH['HEALTH']}.",
        f"Wprowadzono fałszywy numer {PH['PESEL']} podczas rejestracji do {PH['SCHOOL']} w {PH['CITY']}.",
        f"Absolwent {PH['SCHOOL']} uzyskał numer dokumentu {PH['DOCNR']} w dniu {PH['DATE']}.",
        f"Dokumenty z {PH['SCHOOL']} potwierdzają datę urodzenia {PH['DOB']}.",
        f"Pani {PH['NAME']} ukończyła {PH['SCHOOL']} w wieku {PH['AGE']}.",
        f"Zgłoszono dyskryminację w {PH['SCHOOL']} z powodu {PH['SEXUAL-ORIENTATION']} i pochodzenia {PH['ETHNICITY']}.",
        f"Adres {PH['ADDRESS']} jest adresem korespondencyjnym uczelni {PH['SCHOOL']}.",
        f"Rektor {PH['FULLNAME']} z {PH['SCHOOL']} prosi o przelew na konto {PH['BANK']}.",
        f"Uczeń {PH['FULLNAME']} z {PH['SCHOOL']} ma konto {PH['USERNAME']} w systemie.",
        f"W {PH['SCHOOL']} odnotowano płeć {PH['SEX']} studenta {PH['NAME']}.",
        f"Wysłano informację o studentach z {PH['SCHOOL']} na adres {PH['EMAIL']}."
    ],
    "JOB": [
        f"Zajmowane stanowisko to {PH['JOB']} w firmie {PH['COMPANY']}.",
        f"Po **ukończeniu** {PH['SCHOOL']}, {PH['FULLNAME']} **podjął** pracę jako {PH['JOB']} w {PH['COMPANY']}.",
        f"**Zobowiązuje się** {PH['FULLNAME']} do dostarczenia zaświadczenia o zatrudnieniu na stanowisku {PH['JOB']}.",
        f"**Wystawiono** certyfikat potwierdzający, że {PH['FULLNAME']} **pracował** na stanowisku {PH['JOB']} do dnia {PH['DATE']}.",
        f"{PH['FULLNAME']} **awansował** ze stanowiska {PH['JOB']} i **otrzymał** nowe uprawnienia {PH['DOCNR']}.",
        f"**Odnotowano**, że {PH['FULLNAME']} **zrezygnował** ze stanowiska {PH['JOB']} i **podał** numer konta {PH['BANK']} do rozliczenia.",
        f"Doświadczenie zawodowe jako {PH['JOB']} jest niezbędne w {PH['CITY']} dla {PH['COMPANY']}.",
        f"Pracownik firmy {PH['COMPANY']} na stanowisku {PH['JOB']} zgłosił urlop z powodu {PH['HEALTH']}.",
        f"Numer dokumentu {PH['DOCNR']} jest wymagany do podjęcia pracy jako {PH['JOB']}.",
        f"Zgłoszono problem z wypłatą dla {PH['FULLNAME']} na stanowisku {PH['JOB']} (wiek {PH['AGE']}).",
        f"Stanowisko {PH['JOB']} jest kluczowe i wymaga klucza {PH['SECRET']}.",
        f"Pani {PH['NAME']} na stanowisku {PH['JOB']} podała adres {PH['ADDRESS']} i telefon {PH['PHONE']}.",
        f"Wymagane jest doświadczenie na stanowisku {PH['JOB']} dla kandydatów płci {PH['SEX']}.",
        f"Osoba na stanowisku {PH['JOB']} z {PH['COMPANY']} ma PESEL {PH['PESEL']}.",
        f"Pełnomocnictwo dla {PH['REL']} jest ważne dla osoby na stanowisku {PH['JOB']}."
    ],
    "BANK": [
        f"Wprowadzono numer konta bankowego: {PH['BANK']} dla {PH['FULLNAME']}.",
        f"Karta płatnicza {PH['CARD']} **została zablokowana** po próbie transakcji na rachunek {PH['BANK']}.",
        f"Klient {PH['FULLNAME']} **zażądał** zwrotu środków na numer konta {PH['BANK']} po **wykryciu** wycieku danych.",
        f"Konto bankowe {PH['BANK']} **zostało zablokowane** po nieudanych próbach logowania na login {PH['USERNAME']}.",
        f"**Przelał** środki z konta {PH['BANK']} na inną jednostkę w dniu {PH['DATE']}.",
        f"**Odnotowano**, że {PH['FULLNAME']} **zrezygnował** ze stanowiska {PH['JOB']} i **podał** numer konta {PH['BANK']} do rozliczenia.",
        f"Księgowy **skontaktował się** z {PH['FULLNAME']} w sprawie wynagrodzenia na konto {PH['BANK']} (email: {PH['EMAIL']}).",
        f"**Zarejestrowano** numer telefonu {PH['PHONE']} jako dane do **weryfikacji** transakcji {PH['BANK']}.",
        f"Wniosek o kredyt na konto {PH['BANK']} został odrzucony (PESEL {PH['PESEL']}).",
        f"Minimalny wiek {PH['AGE']} jest wymagany do otwarcia konta {PH['BANK']} w firmie {PH['COMPANY']}.",
        f"Numer konta {PH['BANK']} jest chroniony kluczem {PH['SECRET']}.",
        f"Przelew na konto {PH['BANK']} dla {PH['NAME']} {PH['SURNAME']} został zatwierdzony.",
        f"Konto {PH['BANK']} należy do osoby zamieszkałej pod adresem {PH['ADDRESS']} w {PH['CITY']}.",
        f"Wypłata wynagrodzenia dla {PH['FULLNAME']} nastąpi na konto {PH['BANK']} w dniu {PH['DATE']}.",
        f"Numer konta {PH['BANK']} jest powiązany z datą urodzenia {PH['DOB']}."
    ],
    "CARD": [
        f"Zapisano numer karty płatniczej: {PH['CARD']} dla {PH['USERNAME']}.",
        f"Karta płatnicza {PH['CARD']} **została zablokowana** w dniu {PH['DATE']} po próbie transakcji na rachunek {PH['BANK']}.",
        f"**Otrzymano** potwierdzenie płatności kartą {PH['CARD']} dla użytkownika {PH['USERNAME']}.",
        f"**Wykryto**, że {PH['FULLNAME']} **użył** służbowego e-maila {PH['EMAIL']} do **zapisania** numeru karty {PH['CARD']}.",
        f"**Autoryzowano** przelew z karty {PH['CARD']} na kwotę widniejącą w raporcie z dnia {PH['DATE']}.",
        f"**Przekazano** numer karty {PH['CARD']} do działu bezpieczeństwa po **wykryciu** użycia go w {PH['CITY']}.",
        f"Numer karty {PH['CARD']} jest powiązany z adresem e-mail {PH['EMAIL']} i telefonem {PH['PHONE']}.",
        f"Zgłoszono problem z kartą {PH['CARD']} należącą do {PH['FULLNAME']} (PESEL {PH['PESEL']}).",
        f"Wprowadzono dane karty {PH['CARD']} w celu opłacenia rachunku w firmie {PH['COMPANY']}.",
        f"Wydanie karty {PH['CARD']} wymaga podania daty urodzenia {PH['DOB']} i adresu {PH['ADDRESS']}.",
        f"Osoba mająca {PH['AGE']} lat podała zły numer karty {PH['CARD']}.",
        f"Karta {PH['CARD']} jest chroniona kluczem {PH['SECRET']} i dokumentem {PH['DOCNR']}.",
        f"Zgłoszono użycie karty {PH['CARD']} przez krewnego {PH['REL']} w {PH['SCHOOL']}.",
        f"Wprowadzono klucz {PH['SECRET']} w celu autoryzacji transakcji kartą {PH['CARD']}.",
        f"Numer karty {PH['CARD']} jest powiązany z kontem {PH['BANK']} należącym do {PH['FULLNAME']}."
    ],
    "USERNAME": [
        f"ID użytkownika w systemie to: {PH['USERNAME']} (e-mail: {PH['EMAIL']}).",
        f"System **odnotował** nieudane **logowanie** na konto {PH['USERNAME']} z kluczem {PH['SECRET']}.",
        f"Administrator **odblokował** konto {PH['USERNAME']} i **wysłał** nowe hasło na adres {PH['EMAIL']}.",
        f"Konto bankowe {PH['BANK']} **zostało zablokowane** po nieudanych próbach logowania na login {PH['USERNAME']}.",
        f"**Otrzymano** potwierdzenie płatności kartą {PH['CARD']} dla użytkownika {PH['USERNAME']}.",
        f"**Przydzielono** nowy login {PH['USERNAME']} i **zażądano** zmiany hasła {PH['SECRET']} dla {PH['FULLNAME']} w {PH['COMPANY']}.",
        f"Adres e-mail {PH['EMAIL']} jest identyfikatorem konta {PH['USERNAME']} w systemie.",
        f"Weryfikacja wieku {PH['AGE']} jest wymagana do dostępu do konta {PH['USERNAME']}.",
        f"Konto {PH['USERNAME']} zostało zablokowane ze względu na naruszenie regulaminu.",
        f"Konto {PH['USERNAME']} należy do {PH['FULLNAME']} zamieszkałego w {PH['CITY']} (PESEL {PH['PESEL']}).",
        f"Numer {PH['DOCNR']} jest wymagany do uzyskania dostępu do konta {PH['USERNAME']} w firmie {PH['COMPANY']}.",
        f"Użytkownik {PH['USERNAME']} podał kontaktowy numer telefonu {PH['PHONE']} i adres {PH['ADDRESS']}.",
        f"W systemie figuruje login {PH['USERNAME']} dla {PH['NAME']} {PH['SURNAME']}.",
        f"Zgłoszono problem z kontem {PH['USERNAME']} należącym do krewnego {PH['REL']}.",
        f"Konto {PH['USERNAME']} zostało udostępnione przez {PH['REL']}."
    ],
    "REL": [
        f"Informacje dotyczą bliskiego krewnego: {PH['REL']} {PH['FULLNAME']}.",
        f"Klient **podał** dane kontaktowe w związku z historią zdrowotną {PH['HEALTH']} swojego krewnego {PH['REL']}.",
        f"Lekarz **poprosił** o kontakt do {PH['REL']} po zbadaniu {PH['HEALTH']} pacjenta {PH['FULLNAME']}.",
        f"**Zgłoszono** podejrzenie, że {PH['REL']} **kwestionuje** datę urodzenia {PH['DOB']} swojego brata {PH['NAME']}.",
        f"Psycholog **zażądał** informacji o {PH['REL']} w związku ze stanem zdrowia {PH['HEALTH']} pacjenta {PH['NAME']}.",
        f"**Zlecono** kontrolę adresu {PH['ADDRESS']} {PH['CITY']} po **otrzymaniu** zgłoszenia od {PH['REL']}.",
        f"**Uzupełniono** wniosek o dane {PH['FULLNAME']} oraz **załączono** oświadczenie dotyczące relacji {PH['REL']}.",
        f"Zeznanie {PH['REL']} jest kluczowe dla rozpatrzenia wniosku nr {PH['DOCNR']}.",
        f"Klient {PH['FULLNAME']} prosi o kontakt z {PH['REL']} pod numerem {PH['PHONE']} lub {PH['EMAIL']}.",
        f"Wiek {PH['AGE']} {PH['REL']} ma znaczenie w kontekście daty {PH['DATE']}.",
        f"Konto {PH['USERNAME']} zostało udostępnione przez {PH['REL']} w firmie {PH['COMPANY']}.",
        f"Ubezpieczenie zdrowotne obejmuje także {PH['REL']} (PESEL {PH['PESEL']}).",
        f"Zapisano, że {PH['REL']} ma poglądy {PH['POLITICAL-VIEW']} i wyznanie {PH['RELIGION']}.",
        f"Zgłoszono użycie karty {PH['CARD']} przez krewnego {PH['REL']}.",
        f"{PH['REL']} zgłosił problem w {PH['SCHOOL']}."
    ],
    "HEALTH": [
        f"Odnotowano dane zdrowotne: {PH['HEALTH']} pacjenta {PH['FULLNAME']}.",
        f"Pacjent {PH['FULLNAME']} **zgłosił** problem zdrowotny: {PH['HEALTH']} i **wymaga** pilnej konsultacji.",
        f"Klient **podał** dane kontaktowe w związku z historią zdrowotną {PH['HEALTH']} swojego krewnego {PH['REL']}.",
        f"Lekarz **badał** stan zdrowia {PH['HEALTH']} pacjenta {PH['FULLNAME']} (wiek {PH['AGE']}).",
        f"**Monitoruje się** stan {PH['HEALTH']} u osoby w wieku {PH['AGE']} zamieszkałej w {PH['CITY']}.",
        f"**Odmówiono** ujawnienia PESEL {PH['PESEL']} ze względu na wrażliwość danych {PH['HEALTH']} osoby {PH['FULLNAME']}.",
        f"**Odnotowano**, że dokument {PH['DOCNR']} **zawierał** sprzeczne informacje na temat stanu {PH['HEALTH']} i adresu {PH['ADDRESS']}.",
        f"**Weryfikuje się** dane {PH['HEALTH']} i {PH['SEX']} w aktach {PH['FULLNAME']} o numerze {PH['DOCNR']}.",
        f"**Przetwarzano** dane dotyczące wieku {PH['AGE']} i stanu {PH['HEALTH']} osoby {PH['FULLNAME']} ur. {PH['DOB']}.",
        f"Student {PH['FULLNAME']} **złożył** podanie o urlop dziekański w {PH['SCHOOL']} z powodu stanu zdrowia {PH['HEALTH']}.",
        f"Dane zdrowotne {PH['HEALTH']} są objęte klauzulą tajności {PH['SECRET']} i adresem {PH['EMAIL']}.",
        f"W związku z {PH['HEALTH']}, {PH['FULLNAME']} **wskazał** wiek {PH['AGE']} i datę urodzenia {PH['DOB']} jako dane krytyczne.",
        f"Zażądano numeru telefonu {PH['PHONE']} w kontekście historycznych danych medycznych {PH['HEALTH']} z {PH['DATE']}.",
        f"Raport **weryfikuje** dane {PH['HEALTH']} i pochodzenie {PH['ETHNICITY']}.",
        f"Pracownik firmy {PH['COMPANY']} zgłosił urlop z powodu {PH['HEALTH']} (PESEL {PH['PESEL']})."
    ],
    "SECRET": [
        f"W systemie zapisano klucz bezpieczeństwa: {PH['SECRET']} (klucz poufny).",
        f"Klucz {PH['SECRET']} jest wymagany do dostępu do danych {PH['PESEL']} osoby {PH['FULLNAME']}.",
        f"Hasło awaryjne {PH['SECRET']} zostało wysłane na adres {PH['EMAIL']} w dniu {PH['DATE']}.",
        f"Klucz {PH['SECRET']} jest chroniony zgodnie z procedurami firmy {PH['COMPANY']}.",
        f"Numer {PH['DOCNR']} jest powiązany z kluczem szyfrującym {PH['SECRET']} i adresem {PH['ADDRESS']}.",
        f"Brak klucza {PH['SECRET']} uniemożliwia weryfikację konta {PH['USERNAME']} i {PH['CARD']}.",
        f"Zapisano, że dane {PH['HEALTH']} są chronione kluczem {PH['SECRET']}.",
        f"Klucz {PH['SECRET']} musi zostać zmieniony co {PH['AGE']} dni.",
        f"Zlecono kontrolę użycia klucza {PH['SECRET']} w dniu {PH['DATE']} przez {PH['FULLNAME']}.",
        f"Inspektor {PH['FULLNAME']} **nadzoruje** projekt i **wymaga** klucza {PH['SECRET']} od {PH['JOB']}.",
        f"Klucz {PH['SECRET']} jest związany z kontem bankowym {PH['BANK']} i telefonem {PH['PHONE']}.",
        f"Użycie klucza {PH['SECRET']} odnotowano pod adresem {PH['ADDRESS']} w {PH['CITY']}.",
        f"Dane {PH['RELIGION']} i {PH['POLITICAL-VIEW']} są chronione kluczem {PH['SECRET']}.",
        f"Wprowadzono klucz {PH['SECRET']} w celu autoryzacji transakcji kartą {PH['CARD']}.",
        f"Pracownik {PH['JOB']} otrzymał nowy klucz {PH['SECRET']} po ukończeniu {PH['SCHOOL']}."
    ],
    "SEX": [
        f"Zgłaszający jest płci: {PH['SEX']} (wiek {PH['AGE']}).",
        f"W trakcie wywiadu {PH['FULLNAME']} **oświadczył**, że jest płci {PH['SEX']} i **wyznaje** {PH['RELIGION']}.",
        f"**Weryfikuje się** dane {PH['HEALTH']} i {PH['SEX']} w aktach {PH['FULLNAME']} o numerze {PH['DOCNR']}.",
        f"Raport **zawiera** szczegółowe dane na temat płci {PH['SEX']} osoby {PH['NAME']} {PH['SURNAME']}.",
        f"Weryfikacja płci {PH['SEX']} jest niezbędna do rozpatrzenia sprawy {PH['DOCNR']} w dniu {PH['DATE']}.",
        f"Osoba o płci {PH['SEX']} zgłosiła poglądy {PH['POLITICAL-VIEW']} i pochodzenie {PH['ETHNICITY']}.",
        f"Pacjent płci {PH['SEX']} zgłosił problem {PH['HEALTH']} i adres {PH['ADDRESS']} w {PH['CITY']}.",
        f"Ankieta wykazała, że płeć {PH['SEX']} najczęściej **wyznaje** {PH['RELIGION']}.",
        f"W systemie zarejestrowano płeć {PH['SEX']} dla numeru PESEL {PH['PESEL']} (DOB: {PH['DOB']}).",
        f"Dokument zawiera notatkę o płci {PH['SEX']} osoby {PH['NAME']} (e-mail {PH['EMAIL']}).",
        f"Płeć {PH['SEX']} jest ujęta w oświadczeniu o orientacji {PH['SEXUAL-ORIENTATION']}.",
        f"Pracownik płci {PH['SEX']} w firmie {PH['COMPANY']} ma konto {PH['USERNAME']} i telefon {PH['PHONE']}.",
        f"Osoba płci {PH['SEX']} ma konto {PH['BANK']} i używa karty {PH['CARD']}.",
        f"Płeć {PH['SEX']} jest badana w kontekście krewnego {PH['REL']} i {PH['SCHOOL']}.",
        f"Wymagane jest doświadczenie na stanowisku {PH['JOB']} dla kandydatów płci {PH['SEX']}."
    ],
    "RELIGION": [
        f"Osoba wyraziła swoje wyznanie: {PH['RELIGION']} w ankiecie.",
        f"W trakcie wywiadu {PH['FULLNAME']} **oświadczył**, że jest płci {PH['SEX']} i **wyznaje** {PH['RELIGION']}.",
        f"Dokumentacja **wskazuje**, że {PH['FULLNAME']} **wyznaje** {PH['RELIGION']} i posiada poglądy {PH['POLITICAL-VIEW']}.",
        f"**Monitoruje się** dane dotyczące wyznania {PH['RELIGION']} w regionie {PH['CITY']} w dniu {PH['DATE']}.",
        f"Zgłoszenie dotyczy dyskryminacji ze względu na {PH['RELIGION']} w firmie {PH['COMPANY']}.",
        f"Pochodzenie {PH['ETHNICITY']} jest powiązane z wyznaniem {PH['RELIGION']}.",
        f"Wiek {PH['AGE']} osoby {PH['NAME']} i jej {PH['RELIGION']} są danymi wrażliwymi (PESEL {PH['PESEL']}).",
        f"Zapisano, że {PH['RELIGION']} jest chronione kluczem {PH['SECRET']}.",
        f"Numer {PH['PESEL']} należy do osoby wyznania {PH['RELIGION']} (DOB {PH['DOB']}).",
        f"Wniosek o urlop ze względu na święto {PH['RELIGION']} został zatwierdzony w dniu {PH['DATE']}.",
        f"Orientacja {PH['SEXUAL-ORIENTATION']} i {PH['RELIGION']} są badane przez psychologa w {PH['SCHOOL']}.",
        f"Pani {PH['NAME']} wskazała {PH['RELIGION']} w ankiecie na adres {PH['EMAIL']}.",
        f"Wyznanie {PH['RELIGION']} jest chronione prawnie (dokument {PH['DOCNR']}).",
        f"Poglądy {PH['POLITICAL-VIEW']} i wyznanie {PH['RELIGION']} to dane wrażliwe.",
        f"Zeznanie {PH['REL']} dotyczy swobody wyznania {PH['RELIGION']} w {PH['ADDRESS']}."
    ],
    "POLITICAL-VIEW": [
        f"Podano poglądy polityczne: {PH['POLITICAL-VIEW']} w sekcji opinii.",
        f"Dokumentacja **wskazuje**, że {PH['FULLNAME']} **jest objęty** ochroną ze względu na poglądy {PH['POLITICAL-VIEW']}.",
        f"W wywiadzie {PH['FULLNAME']} **oświadczył**, że jego poglądy są {PH['POLITICAL-VIEW']} i {PH['RELIGION']}.",
        f"Wiek {PH['AGE']} i poglądy {PH['POLITICAL-VIEW']} są danymi statystycznymi w {PH['CITY']}.",
        f"Osoba płci {PH['SEX']} zgłosiła poglądy {PH['POLITICAL-VIEW']} i pochodzenie {PH['ETHNICITY']}.",
        f"Dział HR w {PH['COMPANY']} odnotował, że {PH['NAME']} ma poglądy {PH['POLITICAL-VIEW']} (email {PH['EMAIL']}).",
        f"Zgłoszono dyskryminację z powodu poglądów {PH['POLITICAL-VIEW']} w dniu {PH['DATE']}.",
        f"**Kwestionuje się** bezstronność urzędnika ze względu na {PH['POLITICAL-VIEW']} (PESEL {PH['PESEL']}).",
        f"Poglądy {PH['POLITICAL-VIEW']} są powiązane z datą urodzenia {PH['DOB']} i adresem {PH['ADDRESS']}.",
        f"Organizacje **chronią** {PH['FULLNAME']} ze względu na jego poglądy {PH['POLITICAL-VIEW']} (DOCNR {PH['DOCNR']}).",
        f"Zapisano, że {PH['POLITICAL-VIEW']} jest chronione kluczem {PH['SECRET']}.",
        f"Raport **zawiera** szczegółowe dane na temat poglądów {PH['POLITICAL-VIEW']} i stanu {PH['HEALTH']}.",
        f"Poglądy {PH['POLITICAL-VIEW']} są powiązane z przelewami na konto {PH['BANK']} z karty {PH['CARD']}.",
        f"Pracownik socjalny **przeprowadził** wywiad dotyczący {PH['RELIGION']} i {PH['POLITICAL-VIEW']} z {PH['FULLNAME']}.",
        f"Wniosek **mówi** o wieku {PH['AGE']} w kontekście poglądów {PH['POLITICAL-VIEW']}."
    ],
    "ETHNICITY": [
        f"Wskazano pochodzenie etniczne: {PH['ETHNICITY']} dla {PH['FULLNAME']}.",
        f"Pochodzenie {PH['ETHNICITY']} i orientacja {PH['SEXUAL-ORIENTATION']} są objęte ochroną (PESEL {PH['PESEL']}).",
        f"Organizacje **chronią** {PH['FULLNAME']} ze względu na jego pochodzenie {PH['ETHNICITY']} w {PH['CITY']}.",
        f"Wiek {PH['AGE']} osoby {PH['NAME']} i jej pochodzenie {PH['ETHNICITY']} są danymi wrażliwymi.",
        f"Dokument **odnosi się** do pochodzenia {PH['ETHNICITY']} osoby {PH['FULLNAME']} zamieszkałej pod adresem {PH['ADDRESS']}.",
        f"Pochodzenie {PH['ETHNICITY']} jest badane w kontekście wyznania {PH['RELIGION']} i daty {PH['DATE']}.",
        f"Zgłoszono problem dyskryminacji w {PH['CITY']} ze względu na {PH['ETHNICITY']} (email {PH['EMAIL']}).",
        f"Numer {PH['DOCNR']} zawiera dane o pochodzeniu {PH['ETHNICITY']} osoby płci {PH['SEX']}.",
        f"Raport **zawiera** szczegółowe dane na temat {PH['ETHNICITY']} i stanu {PH['HEALTH']}.",
        f"W firmie {PH['COMPANY']} odnotowano pochodzenie {PH['ETHNICITY']} pracownika {PH['JOB']}.",
        f"Zeznanie {PH['REL']} dotyczy pochodzenia {PH['ETHNICITY']} i jego krewnego {PH['NAME']}.",
        f"**Monitoruje się** dane dotyczące pochodzenia {PH['ETHNICITY']} (klucz {PH['SECRET']}).",
        f"Pani {PH['NAME']} wskazała {PH['ETHNICITY']} w ankiecie z datą urodzenia {PH['DOB']}.",
        f"Poglądy {PH['POLITICAL-VIEW']} są powiązane z pochodzeniem {PH['ETHNICITY']}.",
        f"Zapisano, że {PH['ETHNICITY']} jest chronione prawnie (telefon {PH['PHONE']})."
    ],
    "SEXUAL-ORIENTATION": [
        f"Potwierdzono orientację seksualną: {PH['SEXUAL-ORIENTATION']} w oświadczeniu.",
        f"Sprawa **dotyczy** orientacji {PH['SEXUAL-ORIENTATION']} oraz numeru PESEL: {PH['PESEL']} osoby {PH['FULLNAME']}.",
        f"Organizacje **chronią** {PH['FULLNAME']} ze względu na jego orientację {PH['SEXUAL-ORIENTATION']} i pochodzenie {PH['ETHNICITY']}.",
        f"Wiek {PH['AGE']} i orientacja {PH['SEXUAL-ORIENTATION']} są danymi statystycznymi (płeć {PH['SEX']}).",
        f"Raport **zawiera** szczegółowe dane na temat {PH['SEXUAL-ORIENTATION']} osoby o imieniu {PH['NAME']} {PH['SURNAME']}.",
        f"Zgłoszono dyskryminację w {PH['SCHOOL']} z powodu {PH['SEXUAL-ORIENTATION']} w dniu {PH['DATE']}.",
        f"W wywiadzie {PH['FULLNAME']} **oświadczył** swoją orientację {PH['SEXUAL-ORIENTATION']} i {PH['RELIGION']}.",
        f"Orientacja {PH['SEXUAL-ORIENTATION']} i wyznanie {PH['RELIGION']} są danymi wrażliwymi (adres {PH['ADDRESS']}).",
        f"Zapisano, że {PH['SEXUAL-ORIENTATION']} jest chronione kluczem {PH['SECRET']} i dokumentem {PH['DOCNR']}.",
        f"Pani {PH['NAME']} podała, że jej orientacja to {PH['SEXUAL-ORIENTATION']} (email {PH['EMAIL']}).",
        f"W związku z {PH['SEXUAL-ORIENTATION']}, wymagana jest zmiana adresu {PH['ADDRESS']} w {PH['CITY']}.",
        f"Orientacja {PH['SEXUAL-ORIENTATION']} jest badana przez psychologa w kontekście {PH['HEALTH']} i {PH['REL']}.",
        f"Osoba płci {PH['SEX']} zgłosiła orientację {PH['SEXUAL-ORIENTATION']} (wiek {PH['AGE']}).",
        f"Dane {PH['SEXUAL-ORIENTATION']} zostały przekazane do działu HR w {PH['COMPANY']} (telefon {PH['PHONE']}).",
        f"Orientacja {PH['SEXUAL-ORIENTATION']} jest chroniona (bank {PH['BANK']}, karta {PH['CARD']})."
    ]
}

# 1. Scenariusze SENSYTYWNE (Więcej czasowników: zgłosił, wymaga, oświadczył, dotyczy)
coverage_templates = [
    f"Zweryfikowano dane: Imię {PH['NAME']}, Nazwisko {PH['SURNAME']}.",
    f"Osoba {PH['FULLNAME']} ma {PH['AGE']} lat.",
    f"Potwierdza się, że data urodzenia to {PH['DOB']}.",
    f"Ostatnia aktualizacja nastąpiła w dniu {PH['DATE']}.",
    f"Adres korespondencyjny znajduje się w mieście {PH['CITY']}.",
    f"Adres zamieszkania to: {PH['ADDRESS']}.",
    f"Kontakt telefoniczny pod numerem {PH['PHONE']}.",
    f"Kontakt elektroniczny pod adresem {PH['EMAIL']}.",
    f"Wprowadzono numer identyfikacyjny PESEL: {PH['PESEL']}.",
    f"Numer referencyjny dokumentu to: {PH['DOCNR']}.",
    f"Obecny pracodawca to {PH['COMPANY']}.",
    f"Osoba uczęszczała do {PH['SCHOOL']}.",
    f"Zajmowane stanowisko to {PH['JOB']}.",
    f"Wprowadzono numer konta bankowego: {PH['BANK']}.",
    f"Zapisano numer karty płatniczej: {PH['CARD']}.",
    f"ID użytkownika w systemie to: {PH['USERNAME']}.",
    f"Informacje dotyczą bliskiego krewnego: {PH['REL']}.",
    f"Odnotowano dane zdrowotne: {PH['HEALTH']}.",
    f"W systemie zapisano klucz bezpieczeństwa: {PH['SECRET']} (klucz poufny).",
    f"Zgłaszający jest płci: {PH['SEX']}.",
    f"Osoba wyraziła swoje wyznanie: {PH['RELIGION']}.",
    f"Podano poglądy polityczne: {PH['POLITICAL-VIEW']}.",
    f"Wskazano pochodzenie etniczne: {PH['ETHNICITY']}.",
    f"Potwierdzono orientację seksualną: {PH['SEXUAL-ORIENTATION']}."
]

#
# ----- GENEROWANIE I ZAPIS -----
templates = []

print("Generowanie szablonów (15 dla każdego z 26 placeholderów)...")
for ph_key in tqdm(PH.keys(), desc="Generowanie szablonów"):
    current_templates = FULL_TEMPLATE_MAP.get(ph_key, [])
    
    for t in current_templates[:TARGET_COUNT_PER_PH]:
        # Oczyszczanie i kropka
        text = t.replace("  ", " ").strip()
        text = re.sub(r'(\s)([.,!?:;])', r'\2', text)
        if not text.endswith((".", "!", "?")):
            text += "."
        templates.append(text)

random.shuffle(templates)

# Zapis do pliku CSV
with open(f"{OUTPUT_FILE}", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["template"])
    for t in templates:
        w.writerow([t])

print("---")
print(f"Wygenerowano i zapisano: {len(templates)} szablonów (Docelowo: {len(PH) * TARGET_COUNT_PER_PH}).")

# --- WERYFIKACJA POKRYCIA PLACEHOLDERÓW ---
used_placeholders = set()
for template in templates:
    ph_in_template = re.findall(r"\[([^\]]+)\]", template)
    template_ph_set = set(p.lower().replace('-', '_') for p in ph_in_template)
    used_placeholders.update(template_ph_set)

all_placeholders = set(key.lower().replace('-', '_') for key in PH.keys())

# Sprawdzenie, czy wszystkie PH są w zdaniach
missing_placeholders = all_placeholders - used_placeholders

if not missing_placeholders:
    print("✅ Weryfikacja: Wszystkie placeholdery zostały użyte w generowanym korpusie.")
else:
    print(f"❌ UWAGA: Brakujące placeholdery: {missing_placeholders}")