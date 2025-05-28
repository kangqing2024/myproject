import codecs
import logging
import os
from logging.handlers import TimedRotatingFileHandler
   

class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: "[INFO]: %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d - %(message)s",
        logging.ERROR: "[ERROR]: %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d - %(message)s",
        logging.DEBUG: "[DEBUG]: %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d - %(message)s",
        logging.WARNING: "[WARNING]: %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d - %(message)s",
        logging.CRITICAL: "[CRITICAL]: %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d - %(message)s",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        self._style._fmt = log_fmt
        self.datefmt = "%Y-%m-%d %H:%M:%S"
        return super().format(record)


class UTF8TimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=0,
        encoding="utf-8",
        delay=False,
        utc=False,
        atTime=None,
    ):
        super().__init__(
            filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            utc=utc,
            atTime=atTime,
        )


def setup_logger(
    enable_console: bool = True,
    enable_file: bool = True,
    disable_logging: bool = False,
) -> None:

    app_logger = logging.getLogger("bpmn_assistant")
    app_logger.handlers.clear()

    if disable_logging:
        app_logger.setLevel(logging.CRITICAL)
    else:
        app_logger.setLevel(logging.DEBUG)

    # Set the logging level for the root logger to WARNING to suppress logs from external libraries
    logging.getLogger().setLevel(logging.WARNING)

    formatter = CustomFormatter()

    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        console_handler.encoding = "utf-8"
        app_logger.addHandler(console_handler)

    if enable_file:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        file_handler = UTF8TimedRotatingFileHandler(
            os.path.join("logs", "bpmn_assistant.log"),
            when="midnight",
            interval=1,
            backupCount=7,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        app_logger.addHandler(file_handler)

  

