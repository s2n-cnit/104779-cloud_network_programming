import click
from config import Config
from logger import Log
from ui import UI
from typing import Self
import redis
from prompt_toolkit.document import Document
import json


class StatusUI(UI):
    def __init__(self: Self, log: Log, config: Config) -> None:
        super().__init__(log=log, config=config)

    def __write(self: UI, private: bool) -> None:
        while True:
            try:
                sub = self.__redis.pubsub()
                if private:
                    sub.subscribe(f"yacr-{self.__config.name.lower()}")
                else:
                    sub.subscribe("yacr")
            except redis.exceptions.ConnectionError as conn_err:
                self.__log.exception(
                    f"Connection error with pubsub system located at {self.__config.host}:{self.__config.port}",
                    conn_err,
                )
            for message in sub.listen():
                if message is not None and isinstance(message, dict):
                    data = message.get("data")
                    if isinstance(data, int):
                        continue
                    data = json.loads(data)
                    if data["message"] == "list":
                        self.


@click.command()
@click.option(
    "-c",
    "--config",
    help="The configuration file must be in YAML format",
)
@click.option("-n", "--name", help="Your name in the chat", type=str)
@click.option("-s", "--host", help="Hostname (or IP) of the Chat Room Server", type=str)
@click.option("-p", "--port", help="TCP port of the Chat Room Server", type=int)
def main(config: str, name: str, host: str, port: int) -> None:
    log: Log = Log(filename="log/yacr-redis.log")

    cfg: Config = Config(
        log=log,
        path=config,
        data={"name": name, "server": {"host": host, "port": port}},
    )

    ui: UI = UI(log=log, config=cfg)
    ui.run()


if __name__ == "__main__":
    main()
