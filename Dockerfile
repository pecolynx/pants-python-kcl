FROM python:3.9.16-slim-buster

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.1

ENV APP_PATH=src/python/kcl-app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless=11.0.22+7-2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN python -m venv venv && \
    pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false && \
    poetry install --only main

COPY pom.xml setup.py /app/
RUN mkdir -p amazon_kclpy/jars \
    && python setup.py download_jars

RUN useradd -r -s /bin/false appuser
USER appuser

COPY . /app/

ENV AWS_ACCESS_KEY_ID=dummy
ENV AWS_SECRET_ACCESS_KEY=dummy
ENV AWS_PROFILE=localstack
ENV AWS_ENDPOINT_URL=http://127.0.0.1:4566

CMD ["sh", "-c" , "/app/run.sh"]

# FROM public.ecr.aws/amazonlinux/amazonlinux:2
# RUN yum install python3 git java-11-amazon-corretto-headless -y
# RUN git clone --depth 1 --branch v2.1.1 https://github.com/awslabs/amazon-kinesis-client-python
# RUN cd amazon-kinesis-client-python &&\
#     python3 setup.py download_jars &&\
#     python3 setup.py install &&\
#     chmod 777 /usr/bin

# COPY record_processor.py logback.xml run.sh  set_properties.py sample.properties /usr/bin/
# ENTRYPOINT ["sh", "/usr/bin/run.sh"]

