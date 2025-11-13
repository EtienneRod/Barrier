FROM python:3-slim

ENV TZ=America/Toronto
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

RUN apt-get update && apt install -y libmariadb3 libmariadb-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /Barrier

RUN python -m venv venv && . venv/bin/activate && pip install --no-cache-dir paho-mqtt mariadb && deactivate

CMD ["venv/bin/python","Barrier.py"]
