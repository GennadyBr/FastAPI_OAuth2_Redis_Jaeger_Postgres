FROM python:3.11

WORKDIR /usr/src/tests/functional

COPY requirements.txt requirements.txt

RUN  pip3 install --no-cache-dir --upgrade pip \
     && pip3 install --no-cache-dir -r requirements.txt \
     && rm requirements.txt

COPY /functional .

ENTRYPOINT ["sh", "-c" , "python3 utils/wait_for_redis.py && pytest -s -v /usr/src/tests/functional/src"]