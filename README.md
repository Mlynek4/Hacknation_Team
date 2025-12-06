# Hacknation_Team
Repo draft for Hacknation project




## Wymagania

- Node.js >= 18  
- npm  
- Python >= 3.10  


## 1️⃣ Backend – FastAPI

1. Przejdź do folderu backend:
cd ./backend

python3 -m venv venv
source venv/bin/activate # Linux / macOS
# venv\Scripts\activate # Windows

pip install -r requirements.txt

uvicorn main:app --reload --host localhost --port 8080

## 1️⃣ Frontend – React
cd ./frontend

npm install
npm run dev