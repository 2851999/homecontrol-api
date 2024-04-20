import os
import sys

import alembic.config

here = os.path.dirname(os.path.abspath(__file__))

alembic_args = [
    "-c",
    os.path.join(here, "alembic.ini"),
    *sys.argv[1:],
]


def main():
    alembic.config.main(argv=alembic_args)
