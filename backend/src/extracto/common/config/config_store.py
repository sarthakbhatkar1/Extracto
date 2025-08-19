import configparser
import os
from pathlib import Path


class Section:
    def __init__(self, _config, section_name):
        self._config = _config
        self._section_name = section_name

    def __getattr__(self, key):
        try:
            return self._config[self._section_name][key]
        except KeyError:
            raise AttributeError(f"Key '{key}' not found in section '{self._section_name}'")


class ConfigStore:
    def __init__(self, config_dir_var='CONF_PATH', default_cfg='resource', env_var='ENV', default_env='dev'):
        # Determine the environment from the ENV variable or default to 'dev'
        env = os.getenv(env_var, default_env).lower()
        config_dir = os.getenv(config_dir_var, default_cfg)
        config_file = f"config_{env}.cfg"
        config_path = Path(config_dir) / config_file

        # Initialize configparser and read the file
        self._config = configparser.ConfigParser()
        if not config_path.exists():
            raise FileNotFoundError(f"Config file '{config_path}' not found")
        self._config.read(config_path)

    def __getattr__(self, section):
        if section in self._config:
            return Section(self._config, section)
        raise AttributeError(f"Section '{section}' not found in config")


# Example usage (for testing purposes, can be removed in production)
if __name__ == "__main__":
    config = ConfigStore()
    print(config.APP.ENV)
    print(config.APP.NAME)