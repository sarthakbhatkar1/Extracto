import time

from daemon.common.config.config_store import ConfigStore
from daemon.logger.log_utils import Logger
from daemon.db.azure.base import DBConnection
from daemon.db.model import Task
from daemon.utils.util import TaskStatumEnum


logger = Logger()


def fetch_pending_task():
    session = DBConnection().get_session()
    try: 
        task: Task = session.query(Task).filter(Task.STATUS == TaskStatumEnum.NOT_STARTED).order_by(Task.MODIFIED_AT.desc()).first()
        if not task:
            logger.info("Tasks are not available for processing.")
            time.sleep(60)
            return
    except Exception as e:
        logger.error(f"Error in fetching the pending task: {e}")

def execute():
    try:
        pass
    except Exception as e:
        logger.error(f"Exception in execute: {e}")

if __name__ == '__main__':
    execute()