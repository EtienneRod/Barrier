FROM python:3-slim

ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

RUN apt-get update && apt-get install -y gcc g++ curl build-essential postgresql-server-dev-all && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 Barrier && useradd -u 1000 -g Barrier -ms /bin/bash Barrier

USER Barrier

RUN pip install paho-mqtt psycopg2-binary

CMD ["python","/home/Barrier/Barrier.py"]
