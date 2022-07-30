import logging

from . import analyze

logger = logging.getLogger(__name__)


AMOUNT = 20


def run():
    for i in range(AMOUNT):
        analyze.random(nsfw=i % 4 == 0)
