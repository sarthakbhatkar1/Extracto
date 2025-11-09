from extracto.common.config.config_store import ConfigStore


def get_db_schema():
    db_config = ConfigStore().DB
    db_schema = db_config.DB_SCHEMA
    if db_schema:
        return db_schema
    return
