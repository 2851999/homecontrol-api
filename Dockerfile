FROM python:3.11

WORKDIR /homecontrol

COPY ./requirements.txt /homecontrol/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /homecontrol/requirements.txt

COPY ./homecontrol_api /homecontrol/homecontrol_api

CMD ["uvicorn", "homecontrol_api.main:app", "--host", "0.0.0.0", "--port", "8000"]