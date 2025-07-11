FROM python:3.11

RUN apt-get update && apt-get install -y xclip xsel

WORKDIR /web_ui

COPY requirements.txt /web_ui/

RUN pip install --upgrade pip && pip install -r /web_ui/requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]