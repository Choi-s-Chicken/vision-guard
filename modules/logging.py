import logging

_logging_format = "%(asctime)s [%(levelname)s] %(message)s"

logging.basicConfig(level=logging.DEBUG,
                    format=_logging_format,
                    encoding="utf-8",
                    filename="log.log")

logger = logging.getLogger(__name__)