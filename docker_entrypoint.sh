#!/bin/sh

homecontrol-base-alembic upgrade head && homecontrol-api-alembic upgrade head

# Run CMD
exec "$@"