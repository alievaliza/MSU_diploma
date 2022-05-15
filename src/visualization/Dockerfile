FROM python:3.8-slim

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN pip install -r /app/requirements.txt

CMD ["streamlit", "run", "streamlit_vis.py"]
