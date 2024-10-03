#FROM python:3.12-slim-bookworm
FROM python:3.12-alpine
WORKDIR /tmp
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY *.* /tmp/
CMD ["pip", "list"]

