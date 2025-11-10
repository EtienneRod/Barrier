FROM python:3-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libmariadb-dev mariadb-client pkg-config && rm -rf /var/lib/apt/lists/*

RUN pip install mariadb

FROM python:3-slim

COPY --from=builder /usr/local/lib/python3.*/site-packages/mariadb /usr/local/lib/python3.*/site-packages/mariadb

COPY --from=builder /usr/lib/x86_64-linux-gnu/libmariadb.so.3 /usr/lib/x86_64-linux-gnu/libmariadb.so.3

RUN apt-get update && apt-get install -y --no-install-recommends libmariadb3 && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

RUN groupadd -g 1000 Barrier && useradd -u 1000 -g Barrier -ms /bin/bash Barrier

USER Barrier

RUN pip3 install --upgrade pip

RUN pip3 install paho-mqtt mariadb

CMD ["python","/home/Barrier/Barrier.py"]
