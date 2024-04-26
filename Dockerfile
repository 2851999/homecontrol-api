FROM python:3.11

WORKDIR /homecontrol-api

# To ensure scripts can be located
ENV PYTHONPATH "${PYTHONPATH}:/homecontrol-api"

COPY ./requirements.txt /homecontrol-api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /homecontrol-api/requirements.txt

COPY ./homecontrol_api /homecontrol-api/homecontrol_api

# For scripts need to install
COPY pyproject.toml /homecontrol-api/
RUN pip install .

COPY docker_entrypoint.sh /homecontrol-api
RUN ["chmod", "+x", "/homecontrol-api/docker_entrypoint.sh"]

ENTRYPOINT [ "/homecontrol-api/docker_entrypoint.sh" ]
CMD ["uvicorn", "homecontrol_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-config", "logging.ini"]