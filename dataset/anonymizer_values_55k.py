# generate_anonymizer_values_with_noise.py
# Python 3.8+
import random
import string
import os
import json
from datetime import datetime, timedelta
import pandas as pd


# --- ustawienia ---
NOISE_PROB = 0.1   # <--- tutaj ustawiasz ogólne prawdopodobieństwo wprowadzenia błędu/typu (0.1 = 10%)
POLISH_RATIO = 0.8 # 80% wpisów polskich tam, gdzie ma to sens
TOTAL_TARGET = 55000

# --- zasoby (przykładowe listy) ---
# Wartości dla placeholdera [name]
first_names = [
    "Jan","Anna","Piotr","Maria","Krzysztof","Agnieszka","Paweł","Katarzyna","Michał","Ewa",
    "Tomasz","Joanna","Andrzej","Magdalena","Mateusz","Monika","Marcin","Robert","Łukasz","Zuzanna",
    "Julia","Aleksander","Oliwia","Szymon","Natalia","Bartosz","Karolina","Damian","Adam","Patrycja",
    "Grzegorz","Helena","Jakub","Rafał","Iwona","Dawid","Beata","Kamil","Marta","Przemysław","Paulina",
    "Alicja","Olga","Wiktor","Nina","Hubert","Weronika","Eryk",
    "Oliiwa", "Zofia", "Andrz3j", 
    "Apolonia", "Leom", # Nowe z orig.txt
    "Apolonia", "|acek", "Kajefan", "Kaja", "Kacp€r", "Juliusz", "Dominik", "Sonia", "Gaja", "Kalina", 
    "Paweł", "Paulina", "Magdalena", "Julia", "Zuzanna", "Michał", "Oliiwa" # Nowe z CSV
]

addresses = [
    # Adresy znalezione w plikach (z zachowaniem literówek i formatu z plików)
    "al. Słonecznikowa 27, 10-776 Elbląg",
    "pl. 1askółcza 90, 69-948 Toruń",
    "al. Orzechowa 37/41, 27-233 Siemianowice Śląskie",
    "pl. Park0wa 67, 55-082 Tyc#y",
    "p1. Kopernika 507, 90-8b1 Żagań",
    "ulica Wrocławska l2/14, 79-741 Głogów",
    "al. Czarnieckiego 46, 65-296 Polkowice",
    "plac Podmiejska 93, 52-097 Żywiec",
    "aleja Reja 956, 93-500 Łódź",
    "ul. Kwiatowa 70, Czechowice-Dziedzice",
    "124 High St, Barcelona",
    "ul. Szeroka 4, Kostrzyn",
    "123 High St, Stockholm",
    "ul. Szkolna 73, PrVemyśl",
    "ul. Boczna 121, Zamość",
    "ul. Polna 116, Otwock",
    "ul. Moniuszki 189, Gostyń",
    "ul. Mickiewicza 51, Jaworzno",
    "ul. Lipowa 71, Ostrołęka",
    "ul. Piłsudskiego 100, Bydgoszcz",
    
    # Dodatkowe przykładowe adresy
    "ul. Nowy Świat 44, 00-001 Warszawa",
    "Aleje Jerozolimskie 123/5, 02-301 Kraków",
    "Rynek Główny 25, 31-042 Wrocław",
    "ul. Długa 10A, 80-800 Gdańsk",
    "ul. Piotrkowska 100, 90-004 Łódź",
    "plac Wolności 1, 61-738 Poznań",
    "ul. Słowackiego 5, 40-094 Katowice",
    "al. Niepodległości 200, 70-412 Szczecin",
    "ul. Kościuszki 15/3, 85-079 Bydgoszcz",
    "ul. Lubelska 7, 20-090 Lublin",
    "ul. Leśna 1, 15-001 Białystok",
    "pl. Konstytucji 3 Maja 10, 35-062 Rzeszów",
    "ul. Grabiszyńska 241, 53-234 Opole",
    "ul. Żeromskiego 33, 26-600 Radom",
    "ul. Grunwaldzka 55A, 10-544 Olsztyn",
    "ul. Targowa 2/4, 87-100 Toruń",
    "al. Jana Pawła II 88, 30-001 Kielce",
    "ul. Wrocławska 1, 65-001 Zielona Góra",
    "ul. Królewska 12, 59-220 Legnica",
    "ul. Mieszka I 3, 76-200 Słupsk"
]

# Wartości dla placeholdera [surname]
surnames = [
    "Kowalski","Nowak","Wiśniewski","Wójcik","Kowalczyk","Kamiński","Lewandowski","Zieliński","Szymański",
    "Woźniak","Dąbrowski","Kołodziej","Kubiak","Kaczmarek","Mazur","Kozłowski","Jankowski","Wróbel","Zając",
    "Nowicki","Wojciechowski","Krawczyk","Kruk","Adamczyk","Wieczorek","Król","Pawlak","Walczak","Michalski",
    "Jaworski","Piotrowski","Olszewski","Malinowski","Stępień","Górski","Lis","Sikora","Czarnecki","Lipinski",
    "Urbański","Zawadzki","Marciniak","Bąk","Sokół","Wasilewski","Jabłoński","Siwek","Mroż","Cieślak","Kania",
    "Kościesza", "5abak", "Bakiera", "Baster", # Nowe z orig.txt
    "Olszewski", "Michalski", "Nowicki", "Zawadzki", "Siw1k", "Kołodziej",
    "Nagórka", "B€ck", "Lizurej", "Materka", "Linka", "Bodzak", "Skrzecz", "Borysiak"
]

# Wartości dla placeholderów [city], [city_pl], [city_foreign] (połączone)
cities = [
    "Warszawa","Kraków","Łódź","Wrocław","Poznań","Gdańsk","Szczecin","Bydgoszcz","Lublin","Białystok",
    "Katowice","Gdynia","Częstochowa","Radom","Sosnowiec","Toruń","Kielce","Rzeszów","Gliwice","Zabrze",
    "Olsztyn","Opole","Bytom","Gorzów Wielkopolski","Elbląg","Płock","Wałbrzych","Włocławek","Tarnów","Chorzów",
    "Kalisz","Koszalin","Legnica","Grudziądz","Słupsk","Jaworzno","Jastrzębie-Zdrój","Nowy Sącz","Jelenia Góra","Konin",
    "Piotrków Trybunalski","Inowrocław","Lubin","Gniezno","Suwałki","Leszno","Zielona Góra","Tychy","Przemyśl","Ostrowiec Świętokrzyski",
    "Siemianowice Śląskie","Pabianice","Stalowa Wola","Mysłowice","Chełm","Świętochłowice","Zamość","Kędzierzyn-Koźle","Tarnobrzeg","Łomża",
    "Siedlce","Pruszków","Piła","Ostrołęka","Świdnica","Kętrzyn","Sokółka","Bielsko-Biała","Rybnik","Chojnice",
    "Malbork","Kołobrzeg","Żory","Kwidzyn","Krosno","Nowa Sól","Ełk","Świnoujście","Ciechanów","Mińsk Mazowiecki",
    "Radomsko","Skarżysko-Kamienna","Tczew","Sieradz","Lubartów","Puławy","Nowy Dwór Mazowiecki","Zgierz","Otwock","Zawiercie",
    "Świecie","Łowicz","Gostyń","Płońsk","Brzeg","Chrzanów","Kościerzyna","Mrągowo","Kłodzko","Dębica",
    "Węgorzewo","Bogatynia","Sopot","Wejherowo","Żyrardów","Pisz","Piaseczno","Bolesławiec","Czechowice-Dziedzice","Lębork",
    "Racibórz","Knurów","Tomaszów Mazowiecki","Pułtusk","Radziejów","Starachowice","Lubaczów","Nowy Targ","Kostrzyn","Węgrów",
    "Goleniów","Kępno","Ciechocinek","Nowy Tomyśl","Oświęcim","Mikołów","Głogów","Środa Wielkopolska","Gryfice","Działdowo",
    "Nidzica","Końskie","Żary","Nowa Ruda","Chodzież","Mielec","Kościan","Skierniewice","Złotów","Człuchów",
    "Turek","Kamienna Góra","Oleśnica","Olecko","Łask","Szczytno","Żuromin","Szczyrk","Bartoszyce","Krosno Odrzańskie",
    "Środa Śląska",
    "Polkowice", "Zakopane", "Wieluń", "Wągrowiec", # Nowe z orig.txt
    "Berlin","London","Paris","New York","Madrid","Rome","Prague","Vienna","Amsterdam","Brussels",
    "Budapest","Lisbon","Stockholm","Oslo","Helsinki","Copenhagen","Dublin","Tokyo","Seoul","Beijing",
    "Moscow","Toronto","Sydney","Melbourne","Los Angeles","San Francisco","Chicago","Miami","Barcelona","Valencia",
    "Munich","Hamburg","Zurich","Geneva","Luxembourg","Reykjavik","Athens","Krakow",
    "Stockholm", "Grudziądz", "Mielec", "Kościa", "Kępno", "Łomża", "Bydgoszcz", "Chodzież" # Nowe z CSV
]

# Wartości dla placeholdera [street]
streets = [
    "Długa","Szeroka","Leśna","Kwiatowa","Szkolna","Polna","Lipowa","Królewska","Moniuszki","Mickiewicza",
    "Słowackiego","Kościuszki","Piłsudskiego","Świętokrzyska","Boczna","Nowa","Rynek","Kolejowa","Mostowa","Graniczna",
    "al. Słonecznikowa 27", "pl. Łaskółcza 90", "al. Orzechowa 37/41", "pl. Park0wa 67", # Nowe z orig.txt (adresy)
    "al. Czarnieckiego 46", "plac Podmiejska 93", "al. Maj4 43/93", "ul. Dobra", # Nowe z orig.txt (adresy)
    "ul. Kwiatowa 70", "124 High St", "ul. Szeroka 4", "ul. Szkolna 73", "ul. Lipowa 71", "ul. Piłsudskiego 100", "123 High St" # Nowe z CSV (części adresów)
]

# Wartości dla placeholdera [company]
companies = [
    "ABC Sp. z o.o.","XYZ S.A.","Tech Solutions Sp. z o.o.","Polska Energetyka S.A.","Firma Handlowa Nowak",
    "Nauka i Rozwój Sp. z o.o.","Kancelaria Kowalski i Wspólnicy","Sklep Internetowy.pl","Logistyka i Transport S.A.",
    "Agencja Marketingowa Creativa","Biuro Rachunkowe Alfa","Przychodnia Zdrowia Sp. z o.o.","Hurtownia Spożywcza","Restauracja Smak",
    "Gabinety Wiese", "Fundacja Zatoń", "Gabinety Ośkap1.", '"FPUH Matulewi(z"', 
    "FPUH Kołpak", '"PPUH Latuszek i syn s.c."', '"Korzekwa-Broniek Sp.k."', '"Świerkosz-Lisak s.c."', # Nowe z orig.txt
    "Związek Międzygminny PUSZCZA ZIELONKA", "GMINA Nowa Ruda", "Burmistrz Miasta i Gminy w Oleśnica", "Wielkopolski Wojewódzki Konserwator Zabytków", # Nowe z orig.txt
    "Agencja Marketingowa Creativa", "Przychodnia Zdrowia Sp. z o.o.", "Kancelaria Kowalski i Wspólnicy" # Nowe z CSV
]

# Wartości dla placeholdera [school]
schools = [
    "Szkoła Podstawowa nr 5","Liceum Ogólnokształcące im. M. Kopernika","Technikum Informatyczne","Uniwersytet Warszawski","Politechnika Wrocławska",
    "Akademia Górniczo-Hutnicza","Szkoła Policealna 'Nowa'","Przedszkole nr 12","Zespół Szkół Ekonomicznych",
    "Szkoła Policealna 'Nowa'", "Uniwersytet Warszawski", "Akademia...", "Szkoła Podstawowa nr 5" # Nowe z CSV
]

# Wartości dla placeholdera [job]
job_titles = [
    "kierownik","inżynier oprogramowania","nauczyciel","lekarz","pielęgniarka","księgowy","analityk danych","referent",
    "dyrektor","specjalista ds. HR","kierowca","magazynier","sprzedawca","programista","projektant UX","asystent","menedżer projektu",
    "księgowy", "projektant UX", "kierowca", "sprzedawca", "referent" # Nowe z CSV
]

# Wartości dla placeholdera [religion]
religions = ["katolik","prawosławny","brak wyznania","muzułmanin","żyd","świadek Jehowy","protestant","ateista",
             "prawosławny"] # Nowe z CSV

# Wartości dla placeholdera [political-view]
political_views = ["centrowe","lewicowe","prawicowe","liberalne","konserwatywne","socjalistyczne","niezdecydowane",
                   "konserwatywne", "liberalne", "prawicowe", "centrowe", "niezdecydowane", "lewicowe"] # Nowe z CSV

# Wartości dla placeholdera [ethnicity]
ethnicities = ["Polak","Ukrainiec","Niemiec","Rosjanin","Rom","Białorusin","Węgier","Litwin",
               "Polak", "Niemiec", "Rosjanin", "Białorusin", "Węgier"] # Nowe z CSV

# Wartości dla placeholdera [sexual-orientation]
sexual_orientations = ["heteroseksualny","homoseksualny","biseksualny","aseksualny","panseksualny","nieokreślony",
                       "panseksualny", "heteroseksualny"] # Nowe z CSV

# Wartości dla placeholdera [health]
health_conditions = ["brak chorób przewlekłych","cukrzyca","nadciśnienie","astma","choroba serca","COVID-19 - przebyte","depresja","alergia",
                     "alergia", "astma", "brak chorób przewlekłych", "depresja"] # Nowe z CSV

# Wartości dla placeholdera [sex]
sexes = ["mężczyzna","kobieta","inne","M","F","m","k",
         "m"] # Nowe z CSV

# Wartości dla placeholdera [phone]
phones = [
    "+48 513 078 320",
    "514 588 331",
    "+48 787 728 331",
    "794 246 343",
    "+48 724 384 173",
    "+48 782 582 g00",
    "+48 78z 212 g01",
    "+48 609 487 192",
    "574 777 072", # Nowe z orig.txt
    "+48 650-820-73", "+48 566-801-54", "+48 513-945-33", "+48 513-635-35", "+48 532-407-55" # Nowe z CSV
]

# --- NOWE LISTY DLA BRAKUJĄCYCH PLACEHOLDERÓW (bank, card, dob, rel, docnr) ---

# Wartości dla placeholdera [bank-account]
bank_accounts = [
    "PL76700194873269176775628299", "PL02528571328836990477139111",
    "PL84303437592598493504705549", "PL07900114698198655381989505",
    "PL82963484249222472425546458", "SE31000407630544279087082314",
    "PL07506551766745781923488361", "PL34074083822208098581349311",
    "PL93241469668133316379683030", "PL14481950024103068771639405",
    "4281 3628 4213 4025", "8223 8855 6993 9975" # Nowe z orig.txt (mogą to być też karty, ale dla [bank-account] się nadadzą)
]

# Wartości dla placeholdera [credit-card-number]
credit_card_numbers = [
    "4925-1534-8731-1582", "3753-7168-1660-124", "5176 9889 1292 9216",
    "4773022733128616", "5434560361066861", "5482-9184-8710-..."
]

# Wartości dla placeholdera [date-of-birth]
dates_of_birth = [
    "23/01/1976", "1941-01-19", "13/01/1996", "23.02...", "29/08/1995"
]

# Wartości dla placeholdera [relative]
relatives = [
    "córka Maria Wróbel", "moja siostra Andrzej Czarnecki", "córka Karolina Kowalski",
    "mój brat Piotr Bąk", "syn Andrzej Kania", "syn Bartosz Wiśniewski"
]

# Wartości dla placeholdera [docnr]
document_numbers = [
    "64FW9HQ73", "NK1113479", "TK3983527", "CE2692728", "XJ6116767", 
    "5O41YUPUL", "IL0935108", "8371-8805-7449"
]

# Wartości dla placeholdera [pesel]
pesels = [
    "68051234513", "48050271102", "38062554742", "30061137111", 
    "78011780446", "95062298559", "38111351287", "76100500683", 
    "90112757578", "4308155045", "72050670333", "84080259259", 
    "3804084464", "50081362843", "72111996037", "35121847193", "51052206036", # Nowe z CSV/orig.txt
    "16320z09319", "15311231502" # Nowe z orig.txt
]

# Wartości dla placeholdera [email] (oraz potencjalnie [username])
emails = [
    "alicja.woźniak84@wp.pl", "aleksander.wieczorek18@example.com", 
    "anna.jabłoński94@wp.pl", "krzysztof.jankowski78@example.com", 
    "jakub.wojciechowski2@example.com", "marianna25@example.net" # Nowe z orig.txt
]

# Inne kategorie znalezione w plikach (dodane dla kompletności)

# Wartości dla placeholdera [username]
usernames = [
    "dawidzawadzki838", "natalia_636", "jakub.szymański", "rafałkaczmarek489", 
    "@wiktor36", "helena_1@2", "ana_933", "iwonakania290", 
    "@monika46", "dawid.nowak", "szymon.czarnecki", "andrzej.adamczyk"
]

# Wartości dla placeholdera [date]
dates = [
    "02.12.2002", "22.08.2017", "2023-05-29", "2014-08-19", "03/09/2013", 
    "14/05/2023", "16 11 2006r", "23 06 2008 r", "23 09 2008 r", 
    "12 10 2005 r", "02 10 2007 r", "27.03.1990" # Nowe z orig.txt
]

# Wartości dla placeholdera [age]
ages = ["67", "70", "13", "74", "6", "80", "88", "40"]

# Wartości dla placeholdera [secret] (klucze API, hasła, tokeny)
secrets = [
    "AKIAVM7NMGN6WF780IHV", "passwd:eMajanvKOh", "token-322572-x", 
    "passwd:lbyEtZuEjG", "passwd:dkIucLhpya", "AKIA1O7CRQXK7HRK2K0D", 
    "passwd:nJGj1XdwLO", "AKIAABFFTUB64FWE75QN", "AKIAYQTKE87V71JWB7EV", "ćaMspiz..."
]

# --- helper functions ---
def introduce_typo(s, prob=NOISE_PROB):
    if not s or random.random() >= prob:
        return s
    t = random.choice(["sub", "drop", "swap", "char_replace", "leet", "diacritic_drop"])
    if t == "drop" and len(s) > 1:
        i = random.randrange(len(s))
        return s[:i] + s[i + 1 :]
    if t == "swap" and len(s) > 2:
        i = random.randrange(len(s) - 1)
        lst = list(s)
        lst[i], lst[i + 1] = lst[i + 1], lst[i]
        return "".join(lst)
    if t == "sub" and len(s) > 0:
        i = random.randrange(len(s))
        return s[:i] + random.choice(string.ascii_letters + "0123456789") + s[i + 1 :]
    if t == "char_replace" and len(s) > 0:
        repl = {"O": "0", "o": "0", "l": "1", "L": "1", "a": "@", "s": "5", "S": "5", "z": "2", "Z": "2"}
        i = random.randrange(len(s))
        ch = s[i]
        if ch in repl:
            return s[:i] + repl[ch] + s[i + 1 :]
        else:
            return s[:i] + random.choice(list(repl.values())) + s[i + 1 :]
    if t == "leet" and len(s) > 1:
        return s.replace("o", "0").replace("a", "4").replace("e", "3")
    if t == "diacritic_drop":
        return s.replace("ó", "o").replace("ł", "l").replace("ś", "s").replace("ż", "z").replace("ą", "a").replace("ę", "e").replace("ń", "n")
    return s

def random_date_var(start_year=1920, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_day = random.randint(0, delta.days)
    date = start + timedelta(days=random_day)
    fmt = random.choice(["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"])
    return introduce_typo(date.strftime(fmt), prob=NOISE_PROB)

# --- generate records ---
categories = [
    "name","surname","age","date-of-birth","date","sex","religion","political-view","ethnicity","sexual-orientation","health","relative",
    "city","address","email","phone","pesel","document-number","company","school-name","job-title","bank-account","credit-card-number","username","secret"
]

per_cat = TOTAL_TARGET // len(categories)
rows = []

# simple name/surname/etc. generators
def random_name():
    return introduce_typo(random.choice(first_names), prob=NOISE_PROB)

def random_surname():
    return introduce_typo(random.choice(surnames), prob=NOISE_PROB)


def random_address(polish=True):
    if polish:
        addr = f"ul. {random.choice(streets)} {random.randint(1,200)}, {random.choice(cities_pl)}"
    else:
        addr = f"{random.randint(1,200)} {random.choice(['Main St','High St'])}, {random.choice(cities_foreign)}"
    return introduce_typo(addr, prob=NOISE_PROB)

def random_phone(polish=True):
    if polish:
        ph = f"+48 {random.randint(500,699)}-{random.randint(100,999)}-{random.randint(10,99)}"
    else:
        ph = f"+{random.choice([1,44,33])} {random.randint(200,799)} {random.randint(100,999)}"
    return introduce_typo(ph, prob=NOISE_PROB)

def random_email(polish=True):
    domains = ["onet.pl","wp.pl","gmail.com","example.com"]
    email = f"{random.choice(first_names).lower()}.{random.choice(surnames).lower()}{random.randint(1,99)}@{random.choice(domains)}"
    return introduce_typo(email, prob=NOISE_PROB)

def generate_pesel_from_dob(dob):
    # very simple robust generator; may not parse all formats
    try:
        parts = dob.replace("r.","").replace("/","-").replace(" ", "-").split("-")
        if len(parts[0])==2 and len(parts[1])==2 and len(parts[2])==4:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            day, month, year = random.randint(1,28), random.randint(1,12), random.randint(1920,2005)
    except:
        day, month, year = random.randint(1,28), random.randint(1,12), random.randint(1920,2005)
    yy = year % 100
    mm = month
    if 1800 <= year <= 1899:
        mm += 80
    elif 1900 <= year <= 1999:
        mm += 0
    elif 2000 <= year <= 2099:
        mm += 20
    serial = random.randint(0, 999)
    sex_digit = random.randint(0,9)
    pesel_wo_check = f"{yy:02d}{mm:02d}{day:02d}{serial:03d}{sex_digit}"
    weights = [1,3,7,9,1,3,7,9,1,3]
    total = sum(int(a)*b for a,b in zip(pesel_wo_check, weights))
    check = (10 - (total % 10)) % 10
    pesel = pesel_wo_check + str(check)
    # occasionally malformed
    if random.random() < 0.03:
        pesel = pesel[:-1]
    return introduce_typo(pesel, prob=NOISE_PROB)

def generate_document_number(polish=True):
    if polish:
        if random.random() < 0.6:
            letters = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
            digits = "".join(str(random.randint(0,9)) for _ in range(7))
            num = letters + digits
        else:
            num = "".join(random.choice(string.ascii_uppercase+string.digits) for _ in range(9))
    else:
        num = "".join(random.choice(string.ascii_uppercase+string.digits) for _ in range(9))
    return introduce_typo(num, prob=NOISE_PROB)

def generate_credit_card_number():
    prefix = random.choice(["4","5","37"])
    length = 15 if prefix=="37" else 16
    number = prefix + "".join(str(random.randint(0,9)) for _ in range(length - len(prefix) - 1))
    for d in range(10):
        candidate = number + str(d)
        def digits_of(n): return [int(x) for x in str(n)]
        digits = digits_of(candidate)
        odd = digits[-1::-2]
        even = digits[-2::-2]
        checksum = sum(odd)
        for e in even:
            checksum += sum(digits_of(e*2))
        if checksum % 10 == 0:
            s = candidate
            break
    else:
        s = candidate + "0"
    fmt = random.choice([lambda s: s, lambda s: " ".join(s[i:i+4] for i in range(0,len(s),4)), lambda s: "-".join(s[i:i+4] for i in range(0,len(s),4))])
    return introduce_typo(fmt(s), prob=NOISE_PROB)

def generate_iban(polish=True):
    country = "PL" if (polish and random.random() < 0.9) else random.choice(["DE","FR","GB","ES","NL","IT","BE","SE"])
    bban = "".join(str(random.randint(0,9)) for _ in range(26))
    return introduce_typo(country + bban, prob=NOISE_PROB)

def random_username():
    name = random.choice(first_names).lower()
    surname = random.choice(surnames).lower()
    templates = [f"{name}{surname}{random.randint(1,999)}", f"{name}.{surname}", f"{name}_{random.randint(10,999)}", f"@{name}{random.randint(1,99)}"]
    return introduce_typo(random.choice(templates), prob=NOISE_PROB)

def generate_secret():
    patterns = [
        lambda: f"api_key_{random.randint(10000,999999)}",
        lambda: f"passwd:{''.join(random.choice(string.ascii_letters+string.digits) for _ in range(10))}",
        lambda: f"AKIA{''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))}",
        lambda: f"token-{random.randint(100000,999999)}-x"
    ]
    return introduce_typo(random.choice(patterns)(), prob=NOISE_PROB)

# populate rows
for cat in categories:
    for _ in range(per_cat):
        is_polish = random.random() < POLISH_RATIO
        if cat == "name":
            # Użycie listy first_names
            rows.append((cat, introduce_typo(random.choice(first_names), prob=NOISE_PROB)))
        elif cat == "surname":
            # Użycie listy surnames
            rows.append((cat, introduce_typo(random.choice(surnames), prob=NOISE_PROB)))
        elif cat == "age":
            # Użycie listy ages_values
            rows.append((cat, introduce_typo(random.choice(ages_values), prob=NOISE_PROB)))
        elif cat == "date-of-birth":
            # Użycie listy dates_of_birth_values
            rows.append((cat, introduce_typo(random.choice(dates_of_birth_values), prob=NOISE_PROB)))
        elif cat == "date":
            # Użycie listy dates_values
            rows.append((cat, introduce_typo(random.choice(dates_values), prob=NOISE_PROB)))
        elif cat == "sex":
            rows.append((cat, introduce_typo(random.choice(sexes), prob=NOISE_PROB)))
        elif cat == "phone":
            # Użycie listy phones
            rows.append((cat, introduce_typo(random.choice(phones), prob=NOISE_PROB)))
        elif cat == "religion":
            rows.append((cat, introduce_typo(random.choice(religions), prob=NOISE_PROB)))
        elif cat == "political-view":
            rows.append((cat, introduce_typo(random.choice(political_views), prob=NOISE_PROB)))
        elif cat == "ethnicity":
            rows.append((cat, introduce_typo(random.choice(ethnicities), prob=NOISE_PROB)))
        elif cat == "sexual-orientation":
            rows.append((cat, introduce_typo(random.choice(sexual_orientations), prob=NOISE_PROB)))
        elif cat == "health":
            rows.append((cat, introduce_typo(random.choice(health_conditions), prob=NOISE_PROB)))
        elif cat == "relative":
            rows.append((cat, introduce_typo(random.choice(relatives), prob=NOISE_PROB)))
        elif cat == "city":
            rows.append((cat, introduce_typo(random.choice(cities), prob=NOISE_PROB)))
        elif cat == "address":
            # Generowane losowo (Polska/Obca)
            rows.append((cat, introduce_typo(random.choice(addresses), prob=NOISE_PROB)))
        elif cat == "email":
            # Użycie listy emails_values
            rows.append((cat, introduce_typo(random.choice(emails), prob=NOISE_PROB)))
        elif cat == "pesel":
            # Użycie listy pesels_values
            rows.append((cat, introduce_typo(random.choice(pesels), prob=NOISE_PROB)))
        elif cat == "document-number":
            # Użycie listy document_numbers_values
            rows.append((cat, introduce_typo(random.choice(document_numbers), prob=NOISE_PROB)))
        elif cat == "company":
            rows.append((cat, introduce_typo(random.choice(companies), prob=NOISE_PROB)))
        elif cat == "school-name":
            rows.append((cat, introduce_typo(random.choice(schools), prob=NOISE_PROB)))
        elif cat == "job-title":
            rows.append((cat, introduce_typo(random.choice(job_titles), prob=NOISE_PROB)))
        elif cat == "bank-account":
            # Użycie listy bank_accounts_values
            rows.append((cat, introduce_typo(random.choice(bank_accounts), prob=NOISE_PROB)))
        elif cat == "credit-card-number":
            # Użycie listy credit_card_numbers_values
            rows.append((cat, introduce_typo(random.choice(credit_card_numbers), prob=NOISE_PROB)))
        elif cat == "username":
            # Użycie listy usernames_values
            rows.append((cat, introduce_typo(random.choice(usernames), prob=NOISE_PROB)))
        elif cat == "secret":
            # Użycie listy secrets_values
            rows.append((cat, introduce_typo(random.choice(secrets), prob=NOISE_PROB)))
        else:
            rows.append((cat, "brak"))

# If total less than target, add extras
while len(rows) < TOTAL_TARGET:
    cat = random.choice(categories)
    rows.append((cat, "brak"))

# ensure no empty values
rows = [(c, v if (v is not None and str(v).strip() != "") else "brak") for c,v in rows]

random.shuffle(rows)
df = pd.DataFrame(rows, columns=["category","value"])

# save outputs
df.to_csv("anonymizer_values_55k.csv", index=False, encoding="utf-8")
# df.to_json("anonymizer_values_55k.jsonl", orient="records", force_ascii=False, lines=True)

# optional: save per-category files
# for cat in categories:
#     sub = df[df["category"]==cat][["value"]].reset_index(drop=True)
#     sub.to_csv(f"category_{cat}.csv", index=False, encoding="utf-8")

print("Gotowe: anonymizer_values_55k.csv, anonymizer_values_55k.jsonl, category_<kategoria>.csv")
