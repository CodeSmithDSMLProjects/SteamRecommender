FROM python:3.8

COPY model.py .

COPY functions.py .

COPY requirements.txt .

COPY steam.csv .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python3", "model.py"]

