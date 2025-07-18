FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /ml

COPY requirements.txt /ml/

RUN pip install --upgrade pip && pip install -r /ml/requirements.txt

#EXPOSE 8081

RUN adduser --disabled-password --gecos '' celeryuser

USER celeryuser

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--pool=solo"]
#CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--concurrency=2"]