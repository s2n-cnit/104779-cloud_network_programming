from __future__ import annotations

import json
import os
from datetime import datetime
from threading import Thread
from typing import Self
import uuid
from functools import partial

import redis
from config import Config
from logger import Log
from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

class UI:
    help_text = """
YACR (Yet Another Chat Room)
Type \"end\" to terminate.
"""

    def __init__(self: Self, log: Log, config: Config) -> None:
        self.id = str(uuid.uuid4())
        self.__log = log
        self.__config = config
        self.__redis = redis.StrictRedis(
            self.__config.host,
            self.__config.port,
            decode_responses=True,
        )
        self.__join_validation()
        self.__layout()

    def __join_validation(self: Self) -> None:
        def __process(data: dict) -> None:
            if data['error'] is True:
                self.__log.error(f"Join validation failed: {data['message']}")
                self.__terminate()

        self.__log.info("Making join validation request. Please wait...")
        t: Thread = Thread(target=self.__subscribe,
                           kwargs={"topic": f"yacr-{self.id}", "action": __process, "loop": False})
        t.daemon = True
        t.start()

        self.__send_msg_to(user="status", message="joins")
        self.__send_msg_to(message="joins the chat")

    def __layout(self: Self) -> None:
        self.__output_field: TextArea = TextArea(
            style="class:output-field", text=UI.help_text
        )
        self.__search_field: SearchToolbar = SearchToolbar()  # For reverse search.
        self.__input_field: TextArea = TextArea(
            height=1,
            prompt=f"{self.__config.name} >>> ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
            search_field=self.__search_field,
        )
        self.__input_field.accept_handler = self.__accept
        self.__container: HSplit = HSplit(
            [
                self.__output_field,
                Window(height=1, char="-", style="class:line"),
                self.__input_field,
            ]
        )
        self.__layout: Layout = Layout(
            self.__container, focused_element=self.__input_field
        )
        self.__style = Style(
            [("input-field", "fg:ansired"), ("output-field", "fg:#00aaaa")]
        )
        self.__app: Application = Application(
            layout=self.__layout,
            style=self.__style,
            color_depth=ColorDepth.DEPTH_24_BIT,
            full_screen=True,
        )

    def __send_msg_to(self: UI, message: str, user: str = None) -> None:
        try:
            message = message.strip()
            if user is None:
                topic = "yacr"
            else:
                user = user.lower()
                topic = f"yacr-{user}"
            self.__redis.publish(
                topic,
                json.dumps(
                    dict(
                        id=self.id,
                        name=self.__config.name,
                        message=message,
                        time=str(datetime.now())
                    )
                )
            )
        except ConnectionError as conn_err:
            self.__log.exception(
                f"Connection error with pubsub system located at {self.__config.host}:{self.__config.port}",
                conn_err,
            )

    def __terminate(self: Self) -> None:
        os._exit(0)

    def __accept(self: Self, _: any) -> None:
        if self.__input_field.text.lower().strip() == "end":
            self.__send_msg_to(message="leaves", user="status")
            self.__send_msg_to(message="leaves the chat")
            self.__terminate()
        else:
            message = self.__input_field.text.strip()
            if message.startswith("@"):
                msg_list = message[1:].split(" ")
                user = msg_list[0]
                message = " ".join(msg_list[1:])
            else:
                user = None
            self.__input_field.text = ""
            self.__send_msg_to(message=message, user=user)
            if user is not None:
                message = f"(=> {user}) {message}"
                self.__send_msg_to(message=message, user=self.__config.name)

    def __subscribe(self: Self, topic: str, action: callable, loop: bool = True) -> None:
        while True:
            try:
                sub = self.__redis.pubsub()
                sub.subscribe(topic)
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
                    action(data=data)

    def run(self: Self) -> None:
        def __write(private: bool, data: dict) -> None:
            private_str = "(P) " if private else ""
            new_text = f'{self.__output_field.text}\n{private_str}{data["name"]} ' + \
                       f': {data["message"]} at {data["time"]}'
            self.__output_field.buffer.document = Document(
                text=new_text, cursor_position=len(new_text)
            )

        t: Thread = Thread(target=self.__subscribe, kwargs={"topic": "yacr",
                                                            "action": partial(__write, private=False)})
        t.daemon = True
        t.start()

        t_private: Thread = Thread(target=self.__subscribe,
                                   kwargs={"topic": f"yacr-{self.__config.name.lower()}",
                                           "action": partial(__write, private=True)})
        t_private.daemon = True
        t_private.start()

        self.__app.run()
