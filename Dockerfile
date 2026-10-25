FROM python:3.14-alpine
WORKDIR /tmp
RUN pip install --upgrade pip
COPY ./pyproject.toml ./
RUN pip install . --break-system-packages
COPY *.* /tmp/
CMD ["pip", "list"]

