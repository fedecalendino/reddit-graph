import logging
import subprocess
from time import time

logger = logging.getLogger(__name__)


def make():
    logger.info("Building release...")

    start = time()
    process = subprocess.run(
        "/app/release/make.sh",
        shell=True,
        executable="/bin/bash",
        capture_output=True,
    )
    finish = time()

    for line in process.stdout.decode().splitlines():
        logger.info(line)

    logger.info(f"Release completed in {(finish - start):0.2f} seconds...")
