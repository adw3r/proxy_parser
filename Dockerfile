FROM python:latest


WORKDIR /app

RUN pip install -U pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

COPY setup.py .
RUN pip install -e .

CMD python proxy_parser
