FROM python:2.7

WORKDIR /src
ADD . /src

RUN set -ex \
    && curl -L https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh \
    && pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000
