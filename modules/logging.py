import logging
import config

_logging_format = "%(asctime)s [%(levelname)s] %(message)s"

logging.basicConfig(level=logging.INFO,
                    format=_logging_format,
                    encoding="utf-8",
                    filename=config.LOG_PATH)

logger = logging.getLogger(__name__)