FROM python:3.11

WORKDIR /homecontrol-api

COPY ./requirements.txt /homecontrol-api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /homecontrol-api/requirements.txt

COPY ./homecontrol_api /homecontrol-api/homecontrol_api

CMD ["uvicorn", "homecontrol_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]