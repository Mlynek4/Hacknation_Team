#  ----- TEMPLATE GROUPS (Rozszerzone o wysoką koncentrację czasowników) -----

# # 1. Scenariusze SENSYTYWNE (Więcej czasowników: bada, weryfikuje, chroni, kwestionuje, odmówiono, monitoruje)
# sensitive_templates = [
#     f"Pacjent {PH['FULLNAME']} **zgłosił** problem zdrowotny: {PH['HEALTH']} i **wymaga** pilnej konsultacji.",
#     f"W trakcie wywiadu {PH['FULLNAME']} **oświadczył**, że jest płci {PH['SEX']} i **wyznaje** {PH['RELIGION']}.",
#     f"Dokumentacja **wskazuje**, że {PH['FULLNAME']} **jest objęty** ochroną ze względu na poglądy {PH['POLITICAL-VIEW']} i pochodzenie {PH['ETHNICITY']}.",
#     f"Sprawa **dotyczy** orientacji {PH['SEXUAL-ORIENTATION']} oraz numeru PESEL: {PH['PESEL']}, **zapewniono** anonimizację.",
#     f"Klient **podał** dane kontaktowe {PH['PHONE']} i {PH['EMAIL']} w związku z historią zdrowotną {PH['HEALTH']} swojego krewnego {PH['REL']}.",
#     f"Lekarz **badał** stan zdrowia {PH['HEALTH']} pacjenta {PH['FULLNAME']} i **poprosił** o kontakt do {PH['REL']}.",
#     f"W dokumentach **ujawniono**, że {PH['FULLNAME']} **wyznaje** {PH['RELIGION']} i **posiada** poglądy {PH['POLITICAL-VIEW']}.",
#     f"Organizacje **chronią** {PH['FULLNAME']} ze względu na jego orientację {PH['SEXUAL-ORIENTATION']} i pochodzenie {PH['ETHNICITY']}.",
#     f"**Odmówiono** ujawnienia PESEL {PH['PESEL']} ze względu na wrażliwość danych {PH['HEALTH']} osoby {PH['FULLNAME']}.",
#     f"**Zgłoszono** podejrzenie, że {PH['REL']} **kwestionuje** datę urodzenia {PH['DOB']} swojego brata {PH['NAME']}.",
#     f"**Monitoruje się** stan {PH['HEALTH']} u osoby w wieku {PH['AGE']} zamieszkałej w {PH['CITY']}.",
#     f"**Zażądano** numeru telefonu {PH['PHONE']} w kontekście historycznych danych medycznych {PH['HEALTH']} z {PH['DATE']}.",
#     f"Pracownik socjalny **przeprowadził** wywiad dotyczący {PH['RELIGION']} i {PH['POLITICAL-VIEW']} z {PH['FULLNAME']}.",
#     f"Dokument **odnosi się** do pochodzenia {PH['ETHNICITY']} i orientacji {PH['SEXUAL-ORIENTATION']} osoby {PH['FULLNAME']} zamieszkałej pod adresem {PH['ADDRESS']}.",
#     f"**Weryfikuje się** dane {PH['HEALTH']} i {PH['SEX']} w aktach {PH['FULLNAME']} o numerze {PH['DOCNR']}.",
#     f"**Przetwarzano** dane dotyczące wieku {PH['AGE']} i stanu {PH['HEALTH']} osoby {PH['FULLNAME']} ur. {PH['DOB']}.",
#     f"Psycholog **zażądał** informacji o {PH['REL']} w związku ze stanem zdrowia {PH['HEALTH']} pacjenta {PH['NAME']}.",
#     f"Raport **zawiera** szczegółowe dane na temat {PH['SEXUAL-ORIENTATION']} i {PH['ETHNICITY']} osoby o imieniu {PH['NAME']}.",
#     f"Wniosek **mówi** o wyznaniu {PH['RELIGION']} i wieku {PH['AGE']} w kontekście świadczeń medycznych."
# ]

# # 2. Scenariusze FINANSOWE/CYFROWE (Więcej czasowników: anulował, otrzymał, wygenerowano, zablokował, użył, przelał, odrzucił)
# financial_digital_templates = [
#     f"Karta płatnicza {PH['CARD']} **została zablokowana** w dniu {PH['DATE']} po próbie **dokonania** transakcji na rachunek {PH['BANK']}.",
#     f"System **odnotował** nieudane **logowanie** na konto {PH['USERNAME']} z kluczem {PH['SECRET']}, **co naruszyło** procedury bezpieczeństwa.",
#     f"Klient {PH['FULLNAME']} **zażądał** zwrotu środków na numer konta {PH['BANK']} po **wykryciu** wycieku danych z firmy {PH['COMPANY']}.",
#     f"**Wprowadzono** nowy numer dokumentu {PH['DOCNR']} oraz **zaktualizowano** numer telefonu {PH['PHONE']} w związku z kontem {PH['USERNAME']}.",
#     f"Klient {PH['FULLNAME']} **anulował** przelew na numer konta {PH['BANK']} i **zmienił** swoje hasło {PH['SECRET']}.",
#     f"**Otrzymano** potwierdzenie płatności kartą {PH['CARD']} dla użytkownika {PH['USERNAME']} w dniu {PH['DATE']}.",
#     f"System **wygenerował** tymczasowy klucz API {PH['SECRET']} dla pracownika {PH['FULLNAME']} z firmy {PH['COMPANY']}.",
#     f"Konto bankowe {PH['BANK']} **zostało zablokowane** po nieudanych próbach logowania na login {PH['USERNAME']}.",
#     f"**Wykryto**, że {PH['FULLNAME']} **użył** służbowego e-maila {PH['EMAIL']} do **zapisania** numeru karty {PH['CARD']}.",
#     f"**Zmieniono** numer rachunku bankowego {PH['BANK']} i **odnotowano** nowy numer dokumentu {PH['DOCNR']}.",
#     f"**Przydzielono** nowy login {PH['USERNAME']} i **zażądano** zmiany hasła {PH['SECRET']} dla {PH['FULLNAME']} w {PH['COMPANY']}.",
#     f"**Autoryzowano** przelew z karty {PH['CARD']} na kwotę widniejącą w raporcie z dnia {PH['DATE']}.",
#     f"**Zarejestrowano** adres {PH['EMAIL']} i numer telefonu {PH['PHONE']} jako dane do **weryfikacji** transakcji {PH['BANK']}.",
#     f"**Przekazano** numer karty {PH['CARD']} do działu bezpieczeństwa po **wykryciu** użycia go w {PH['CITY']}.",
#     f"**Zaktualizowano** adres {PH['ADDRESS']} w systemie po **potwierdzeniu** tożsamości numerem PESEL {PH['PESEL']}.",
#     f"Bank **odrzucił** wniosek {PH['FULLNAME']} o kredyt po **sprawdzeniu** numeru {PH['PESEL']}.",
#     f"Administrator **odblokował** konto {PH['USERNAME']} i **wysłał** nowe hasło na adres {PH['EMAIL']}."
# ]

# # 3. Scenariusze ADMINISTRACYJNE (Więcej czasowników: skorygował, odrzucono, rozpatruje, wydano, przedstawił, zlecono, wniósł)
# administrative_complex_templates = [
#     f"Burmistrz **nakazał** {PH['FULLNAME']} **uzupełnić** wniosek (nr {PH['DOCNR']}) do dnia {PH['DATE']}, pod rygorem **odmowy** rozpatrzenia.",
#     f"**Zobowiązuje się** {PH['FULLNAME']} do **dostarczenia** zaświadczenia o zatrudnieniu w {PH['COMPANY']} na stanowisku {PH['JOB']} w {PH['CITY']}.",
#     f"Inspektor **sprawdził** tożsamość {PH['FULLNAME']} (PESEL {PH['PESEL']}) i **zarejestrował** adres zamieszkania {PH['ADDRESS']}.",
#     f"W związku z {PH['HEALTH']}, {PH['FULLNAME']} **wskazał** wiek {PH['AGE']} i datę urodzenia {PH['DOB']} jako dane krytyczne.",
#     f"W urzędzie **odrzucono** wniosek {PH['DOCNR']} **złożony** przez {PH['FULLNAME']} z powodu braków w adresie {PH['ADDRESS']} {PH['CITY']}.",
#     f"Wójt gminy **rozpatruje** prośbę {PH['FULLNAME']} **dotyczącą** zmiany daty urodzenia {PH['DOB']} i numeru PESEL {PH['PESEL']}.",
#     f"**Wydano** zaświadczenie numer {PH['DOCNR']} dla {PH['FULLNAME']} w dniu {PH['DATE']}, **potwierdzające** wiek {PH['AGE']}.",
#     f"Pełnomocnik {PH['FULLNAME']} **przedstawił** nowy adres do korespondencji {PH['ADDRESS']} i numer telefonu {PH['PHONE']}.",
#     f"**Zlecono** kontrolę adresu {PH['ADDRESS']} {PH['CITY']} po **otrzymaniu** zgłoszenia od {PH['REL']}.",
#     f"**Skorygowano** numer dokumentu {PH['DOCNR']} oraz **zaktualizowano** datę {PH['DATE']} na dokumencie powiązanym z {PH['FULLNAME']}.",
#     f"Zgłoszenie **wymaga** podania adresu e-mail {PH['EMAIL']} i **potwierdzenia** tożsamości numerem {PH['PESEL']}.",
#     f"**Sprawdzono** poprawność danych {PH['DOB']} i {PH['AGE']} w oparciu o dokumenty tożsamości {PH['DOCNR']}.",
#     f"W związku z koniecznością **prowadzenia** spraw, {PH['FULLNAME']} **prosi** o kontakt na {PH['PHONE']} lub {PH['EMAIL']}.",
#     f"**Odnotowano**, że dokument {PH['DOCNR']} **zawierał** sprzeczne informacje na temat stanu {PH['HEALTH']} i adresu {PH['ADDRESS']}.",
#     f"**Uzupełniono** wniosek o dane {PH['FULLNAME']} oraz **załączono** oświadczenie dotyczące relacji {PH['REL']}.",
#     f"Petent {PH['FULLNAME']} **wniósł** o wydanie duplikatu dokumentu {PH['DOCNR']} w związku ze zmianą adresu {PH['ADDRESS']}."
# ]

# # 4. Scenariusze EDUKACJA/KARIERA (Więcej czasowników: zatrudnia, awansował, nadzoruje, wykłada, ukończył, przyznało, złożył, zrezygnował)
# education_career_templates = [
#     f"Po **ukończeniu** {PH['SCHOOL']}, {PH['FULLNAME']} **podjął** pracę jako {PH['JOB']} w firmie {PH['COMPANY']} w {PH['CITY']}.",
#     f"**Wystawiono** certyfikat numer {PH['DOCNR']} potwierdzający, że {PH['FULLNAME']} **pracował** na stanowisku {PH['JOB']} do dnia {PH['DATE']}.",
#     f"**Zweryfikowano** historię zatrudnienia {PH['FULLNAME']} w {PH['COMPANY']} oraz **przeanalizowano** jego dane kontaktowe: {PH['EMAIL']} i {PH['PHONE']}.",
#     f"Firma {PH['COMPANY']} **zatrudnia** {PH['FULLNAME']} na stanowisku {PH['JOB']} od {PH['DATE']}.",
#     f"{PH['FULLNAME']} **awansował** ze stanowiska {PH['JOB']} i **otrzymał** nowe uprawnienia (numer {PH['DOCNR']}).",
#     f"Inspektor {PH['FULLNAME']} **nadzoruje** projekt w {PH['COMPANY']} i **wymaga** klucza {PH['SECRET']}.",
#     f"Profesor {PH['FULLNAME']} **wykłada** w {PH['SCHOOL']} i **podał** swój numer telefonu {PH['PHONE']} do kontaktu.",
#     f"Uczelnia {PH['SCHOOL']} **przyznała** {PH['FULLNAME']} numer identyfikacyjny {PH['PESEL']} do celów rekrutacyjnych.",
#     f"**Odnotowano**, że {PH['FULLNAME']} **zrezygnował** ze stanowiska {PH['JOB']} i **podał** numer konta {PH['BANK']} do rozliczenia.",
#     f"**Przekazano** dane {PH['FULLNAME']} do działu HR w {PH['COMPANY']} wraz z informacją o wieku {PH['AGE']} i dacie {PH['DOB']}.",
#     f"Księgowy **skontaktował się** z {PH['FULLNAME']} na adres {PH['EMAIL']} w sprawie wynagrodzenia na konto {PH['BANK']}.",
#     f"Student {PH['FULLNAME']} **złożył** podanie o urlop dziekański w {PH['SCHOOL']} z powodu stanu zdrowia {PH['HEALTH']}."
# ]

# # ----- GRUPY ZBIORCZE (Do losowania) -----
# administrative_openings = [
#     f"Na podstawie przedłożonych dokumentów **informujemy**, że numer sprawy {PH['DOCNR']} został przypisany do wniosku z dnia {PH['DATE']}.",
#     f"W związku z przekazanymi materiałami **zawiadamiamy**, że w dniu {PH['DATE']} wpłynęło zgłoszenie z adresu {PH['ADDRESS']}.",
#     f"**Oświadcza się**, że rozpatrywanie wniosku {PH['DOCNR']} wymaga dodatkowej weryfikacji tożsamości osoby {PH['FULLNAME']}.",
#     f"W świetle złożonego wniosku **stwierdza się**, że pełnomocnictwo dla {PH['FULLNAME']} jest ważne do dnia {PH['DATE']}.",
#     f"Organ administracji **potwierdza** przyjęcie dokumentu tożsamości o numerze {PH['DOCNR']} w dniu {PH['DATE']}.",
#     f"Decyzja **zostanie podjęta** w terminie 14 dni roboczych od daty {PH['DATE']}, co ogłoszono w Biuletynie {PH['CITY']}.",
#     f"Pisemne **potwierdzenie** doręczenia dokumentów jest dostępne pod numerem {PH['PHONE']} w godzinach pracy Urzędu.",
#     f"**Przyjęto** do wiadomości oświadczenie osoby {PH['FULLNAME']} zamieszkałej w {PH['CITY']} o nowym adresie korespondencyjnym {PH['ADDRESS']}."
# ]

# administrative_actions = [
#     f"Sprawę **prowadzi** urzędnik {PH['FULLNAME']}, kontakt telefoniczny pod numerem {PH['PHONE']}.",
#     f"Wniosek **został uzupełniony** przez {PH['FULLNAME']} w dniu {PH['DATE']}, po kontakcie mailowym {PH['EMAIL']}.",
#     f"**Ustalono**, że adres korespondencyjny to: {PH['ADDRESS']} w {PH['CITY']} i jest on zbieżny z podanym numerem {PH['PHONE']}.",
#     f"Kontrolę **przeprowadził** Inspektor {PH['FULLNAME']} w dniu {PH['DATE']}, o czym świadczy protokół nr {PH['DOCNR']}.",
#     f"**Zarejestrowano** nowy numer PESEL: {PH['PESEL']} w bazie danych z uwzględnieniem daty urodzenia {PH['DATE']}.",
#     f"W systemie **odnotowano** zmianę adresu zamieszkania dla osoby {PH['FULLNAME']} na: {PH['ADDRESS']}.",
#     f"**Sprawdzono** poprawność numeru identyfikacyjnego {PH['DOCNR']} w Centralnym Rejestrze Danych Administracyjnych.",
#     f"Zgłoszenie **wymaga** dostarczenia dodatkowej dokumentacji (numer sprawy {PH['DOCNR']}) przez podmiot {PH['COMPANY']}."
# ]

# administrative_closings = [
#     f"Postępowanie **nie wymaga** dalszych czynności i zostaje zamknięte z dniem {PH['DATE']} pod numerem {PH['DOCNR']}.",
#     f"**Zobowiązuje się** stronę {PH['FULLNAME']} do **uzupełnienia** braków formalnych, przesyłając je na adres {PH['EMAIL']}.",
#     f"Sprawa **została przekazana** do archiwizacji i będzie dostępna do wglądu w Urzędzie Miasta {PH['CITY']}.",
#     f"**Zaleca się** kontakt mailowy na adres {PH['EMAIL']} lub telefoniczny {PH['PHONE']} w celu omówienia dalszych kroków.",
#     f"Decyzja **wchodzi w życie** z dniem jej ogłoszenia ({PH['DATE']}) i dotyczy adresu {PH['ADDRESS']}.",
#     f"W terminie 7 dni **przysługuje** odwołanie do organu wyższej instancji za pośrednictwem adresu: {PH['ADDRESS']}.",
#     f"**Wprowadzono** ostateczną adnotację w rejestrze pod numerem {PH['DOCNR']} dotyczącą osoby {PH['FULLNAME']}.",
#     f"Całość dokumentacji **została zdigitalizowana** i przekazana do {PH['COMPANY']} w dniu {PH['DATE']}."
# ]