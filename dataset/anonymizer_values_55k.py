# generate_anonymizer_values_with_noise.py
# Python 3.8+
import random
import string
import os
import json
from datetime import datetime, timedelta
import pandas as pd

# random.seed(20251206)

# --- ustawienia ---
NOISE_PROB = 0.1   # <--- tutaj ustawiasz ogólne prawdopodobieństwo wprowadzenia błędu/typu (0.1 = 10%)
POLISH_RATIO = 0.8 # 80% wpisów polskich tam, gdzie ma to sens
TOTAL_TARGET = 55000

# --- zasoby (przykładowe listy) ---
first_names = [
    "Jan","Anna","Piotr","Maria","Krzysztof","Agnieszka","Paweł","Katarzyna","Michał","Ewa",
    "Tomasz","Joanna","Andrzej","Magdalena","Mateusz","Monika","Marcin","Robert","Łukasz","Zuzanna",
    "Julia","Aleksander","Oliwia","Szymon","Natalia","Bartosz","Karolina","Damian","Adam","Patrycja",
    "Grzegorz","Helena","Jakub","Rafał","Iwona","Dawid","Beata","Kamil","Marta","Przemysław","Paulina",
    "Alicja","Olga","Wiktor","Nina","Hubert","Weronika","Eryk"
]
surnames = [
    "Kowalski","Nowak","Wiśniewski","Wójcik","Kowalczyk","Kamiński","Lewandowski","Zieliński","Szymański",
    "Woźniak","Dąbrowski","Kołodziej","Kubiak","Kaczmarek","Mazur","Kozłowski","Jankowski","Wróbel","Zając",
    "Nowicki","Wojciechowski","Krawczyk","Kruk","Adamczyk","Wieczorek","Król","Pawlak","Walczak","Michalski",
    "Jaworski","Piotrowski","Olszewski","Malinowski","Stępień","Górski","Lis","Sikora","Czarnecki","Lipinski",
    "Urbański","Zawadzki","Marciniak","Bąk","Sokół","Wasilewski","Jabłoński","Siwek","Mroż","Cieślak","Kania"
]
cities_pl = [
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
    "Środa Śląska"
]
cities_foreign = [
    "Berlin","London","Paris","New York","Madrid","Rome","Prague","Vienna","Amsterdam","Brussels",
    "Budapest","Lisbon","Stockholm","Oslo","Helsinki","Copenhagen","Dublin","Tokyo","Seoul","Beijing",
    "Moscow","Toronto","Sydney","Melbourne","Los Angeles","San Francisco","Chicago","Miami","Barcelona","Valencia",
    "Munich","Hamburg","Zurich","Geneva","Luxembourg","Reykjavik","Athens","Lisbon","Warsaw","Krakow"
]
streets = ["Długa","Szeroka","Leśna","Kwiatowa","Szkolna","Polna","Lipowa","Królewska","Moniuszki","Mickiewicza",
           "Słowackiego","Kościuszki","Piłsudskiego","Świętokrzyska","Boczna","Nowa","Rynek","Kolejowa","Mostowa","Graniczna"]
companies = ["ABC Sp. z o.o.","XYZ S.A.","Tech Solutions Sp. z o.o.","Polska Energetyka S.A.","Firma Handlowa Nowak",
             "Nauka i Rozwój Sp. z o.o.","Kancelaria Kowalski i Wspólnicy","Sklep Internetowy.pl","Logistyka i Transport S.A.",
             "Agencja Marketingowa Creativa","Biuro Rachunkowe Alfa","Przychodnia Zdrowia Sp. z o.o.","Hurtownia Spożywcza","Restauracja Smak"]
schools = ["Szkoła Podstawowa nr 5","Liceum Ogólnokształcące im. M. Kopernika","Technikum Informatyczne","Uniwersytet Warszawski","Politechnika Wrocławska",
           "Akademia Górniczo-Hutnicza","Szkoła Policealna 'Nowa'","Przedszkole nr 12","Zespół Szkół Ekonomicznych"]
job_titles = ["kierownik","inżynier oprogramowania","nauczyciel","lekarz","pielęgniarka","księgowy","analityk danych","referent",
              "dyrektor","specjalista ds. HR","kierowca","magazynier","sprzedawca","programista","projektant UX","asystent","menedżer projektu"]
religions = ["katolik","prawosławny","brak wyznania","muzułmanin","żyd","świadek Jehowy","protestant","ateista"]
political_views = ["centrowe","lewicowe","prawicowe","liberalne","konserwatywne","socjalistyczne","niezdecydowane"]
ethnicities = ["Polak","Ukraińczyk","Niemiec","Rosjanin","Rom","Białorusin","Węgier","Litwin"]
sexual_orientations = ["heteroseksualny","homoseksualny","biseksualny","aseksualny","panseksualny","nieokreślony"]
health_conditions = ["brak chorób przewlekłych","cukrzyca","nadciśnienie","astma","choroba serca","COVID-19 - przebyte","depresja","alergia"]
sexes = ["mężczyzna","kobieta","inne","M","F","m","k"]

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

def random_city(polish=True):
    return introduce_typo(random.choice(cities_pl if polish else cities_foreign), prob=NOISE_PROB)

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
            rows.append((cat, random_name()))
        elif cat == "surname":
            rows.append((cat, random_surname()))
        elif cat == "age":
            rows.append((cat, str(random.randint(0,100))))
        elif cat == "date-of-birth":
            rows.append((cat, random_date_var(1920, 2005)))
        elif cat == "date":
            rows.append((cat, random_date_var(2000, 2025)))
        elif cat == "sex":
            rows.append((cat, random.choice(sexes)))
        elif cat == "religion":
            rows.append((cat, random.choice(religions)))
        elif cat == "political-view":
            rows.append((cat, random.choice(political_views)))
        elif cat == "ethnicity":
            rows.append((cat, random.choice(ethnicities)))
        elif cat == "sexual-orientation":
            rows.append((cat, random.choice(sexual_orientations)))
        elif cat == "health":
            rows.append((cat, random.choice(health_conditions)))
        elif cat == "relative":
            rows.append((cat, f"{random.choice(['mój brat','moja siostra','syn','córka'])} {random_name()} {random_surname()}"))
        elif cat == "city":
            rows.append((cat, random_city(polish=is_polish)))
        elif cat == "address":
            rows.append((cat, random_address(polish=is_polish)))
        elif cat == "email":
            rows.append((cat, random_email(polish=is_polish)))
        elif cat == "phone":
            rows.append((cat, random_phone(polish=is_polish)))
        elif cat == "pesel":
            dob = random_date_var(1920, 2005)
            rows.append((cat, generate_pesel_from_dob(dob)))
        elif cat == "document-number":
            rows.append((cat, generate_document_number(polish=is_polish)))
        elif cat == "company":
            rows.append((cat, random.choice(companies)))
        elif cat == "school-name":
            rows.append((cat, random.choice(schools)))
        elif cat == "job-title":
            rows.append((cat, random.choice(job_titles)))
        elif cat == "bank-account":
            rows.append((cat, generate_iban(polish=is_polish)))
        elif cat == "credit-card-number":
            rows.append((cat, generate_credit_card_number()))
        elif cat == "username":
            rows.append((cat, random_username()))
        elif cat == "secret":
            rows.append((cat, generate_secret()))
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
