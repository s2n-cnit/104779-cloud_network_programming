from __future__ import annotations

from typing import Dict, List

import yaml
from logger import Log


class Config:
    def __init__(
        self: Config, log: Log, path: str = None, data: Dict[str, any] = dict()
    ) -> None:
        self.__config = {}
        self.__log: Log = log
        try:
            if path is not None:
                self.__config = yaml.safe_load(open(path, "r"))
        except FileNotFoundError as fnf_err:
            self.__log.exception(f"File {path} not found", error=fnf_err)
        self.__data = data
        self.__path: str = path

    @property
    def host(self: Config) -> str:
        o = self.__config["server"].get("host", None)
        if o is not None:
            return o
        o = self.__data["server"].get("host", None)
        if o is not None:
            return o
        self.__log.exception("Host not found in the configuration file/command line options", terminate=True)

    @property
    def port(self: Config) -> int:
        o = self.__config["server"].get("port", None)
        if o is not None:
            return o
        o = self.__data["server"].get("port", None)
        if o is not None:
            return o
        self.__log.exception("Port not found in the configuration file/command line options", terminate=True)


    @property
    def name(self: Config) -> str:
        o = self.__config.get("name", None)
        if o is not None:
            return o
        o = self.__data.get("name", None)
        if o is not None:
            return o
        self.__log.exception("Name not found in the configuration file/command line options", terminate=True)

