from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",  # Twój frontend dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # które domeny mają dostęp
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS itp.
    allow_headers=["*"],  # nagłówki HTTP
)


# definiujesz model danych
class TextRequest(BaseModel):
    text: str  # FastAPI wie, że "text" musi być stringiem


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/anonymize")
def anonymize_text(req: TextRequest):
    text = req.text 
    
    #m nadpisac to wartosciami
    return {
        "textAnonymized": text.upper(),
        "textSynthetic": text.upper()
    }
