import asyncio

from daemon.worker import ExtractoWorker
from daemon.logger.log_utils import Logger

logger = Logger()


if __name__ == "__main__":
    logger.info("Starting Extracto Daemon...")
    worker = ExtractoWorker()
    asyncio.run(worker.run_forever())
