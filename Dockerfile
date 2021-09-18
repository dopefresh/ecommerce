FROM python:latest
WORKDIR /app
COPY . /app
RUN pip3 install poetry && poetry config virtualenvs.create false && poetry install --no-dev && poetry shell
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
EXPOSE 8000
CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "ecommerce.wsgi:application"]
