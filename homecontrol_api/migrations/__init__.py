import sys
from pathlib import Path

import alembic.config

alembic_args = [
    "-c",
    str(Path(__file__).parent / "alembic.ini"),
    *sys.argv[1:],
]


def main():
    alembic.config.main(argv=alembic_args)
