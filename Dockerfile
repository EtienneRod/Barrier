FROM python:3-slim

ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

RUN apt update && apt -y dist-upgrade && apt install -y python3-mariadb && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 Barrier && useradd -u 1000 -g Barrier -ms /bin/bash Barrier

USER Barrier

RUN pip3 install --upgrade pip

RUN pip3 install paho-mqtt

CMD ["python","/home/Barrier/Barrier.py"]
