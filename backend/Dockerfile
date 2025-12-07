FROM python:3.12

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

RUN python -m spacy download pl_core_news_sm

COPY . /app

EXPOSE 8080

# CMD ["uvicorn", "api.entry:create_api", "--host", "0.0.0.0", "--port", "9000", "--reload"]
CMD ["uvicorn", "main:app",  "--host", "0.0.0.0", "--port", "8080", "--reload"]