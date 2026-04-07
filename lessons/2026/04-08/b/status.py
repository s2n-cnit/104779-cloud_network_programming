import click
from config import Config
from logger import Log
import redis
import json
from datetime import datetime


@click.command()
@click.option(
    "-c",
    "--config",
    help="The configuration file must be in YAML format",
)
@click.option("-s", "--host", help="Hostname (or IP) of the Chat Room Server", type=str)
@click.option("-p", "--port", help="TCP port of the Chat Room Server", type=int)
def main(config: str, host: str, port: int) -> None:
    log: Log = Log(filename="log/yacr-redis.log")

    cfg: Config = Config(
        log=log,
        path=config,
        data={"name": "status", "server": {"host": host, "port": port}},
    )

    __redis = redis.StrictRedis(
        cfg.host,
        cfg.port,
        decode_responses=True,
    )
    connected_users = []

    log.info(f"Starting status service")

    while True:
        try:
            sub = __redis.pubsub()
            sub.subscribe(f"yacr-{cfg.name.lower()}")
        except redis.exceptions.ConnectionError as conn_err:
            log.exception(
                f"Connection error with pubsub system located at {cfg.host}:{cfg.port}",
                conn_err,
            )
        for message in sub.listen():
            if message is not None and isinstance(message, dict):
                data = message.get("data")
                if isinstance(data, int):
                    continue
                data = json.loads(data)
                user = data['name']
                topic = f"yacr-{user.lower()}"
                reply = None
                log.info(f"Received message from {user}: {data['message']}")
                match (data['message'].strip().lower()):
                    case "help":
                        reply = "Available Commands:\n" + \
                                   "- help: Show this message\n" + \
                                   "- list: Show the list of connected users\n"
                    case "joins":
                        if user not in connected_users and user.lower() != "status":
                            connected_users.append(user)
                        else:
                            reply = "Name not valid"
                    case "leaves":
                        if user in connected_users:
                            connected_users.remove(user)
                        else:
                            log.warning(f"Received leave message from {user} who is not in the connected users list")
                    case "list":
                        if len(connected_users) == 0:
                            reply = "No connected users"
                        else:
                            reply = "Connected users:\n" + \
                                        "\n".join(connected_users) + "\n"
                    case _:
                        log.warning(f"Received unknown command from {user}: {data['message']}")
                        reply = "Unknown command"
                if reply is not None:
                    __redis.publish(
                        topic,
                        json.dumps(
                            dict(
                                name=cfg.name,
                                type="!",
                                message=reply,
                                time=str(datetime.now()),
                            )
                        )
                    )
                    log.info(f"Sent reply to {user}: {reply} via topic {topic}")


if __name__ == "__main__":
    main()
