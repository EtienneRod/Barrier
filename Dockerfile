FROM python:3-slim

ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

RUN curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash

RUN apt-get update && apt install -y libmariadb-dev libmariadb3 && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 Barrier && useradd -u 1000 -g Barrier -ms /bin/bash Barrier

USER Barrier

RUN pip install --upgrade pip && ip install --upgrade setuptools && pip install paho-mqtt mariadb

CMD ["python","/home/Barrier/Barrier.py"]
