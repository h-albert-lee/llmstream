import logging


class Logger:
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        self.logger = logging.getLogger("LLMStreamLogger")

    def log_request(self, request, response):
        self.logger.info(f"Request: {request.dict()} | Response: {response}")

    def log_error(self, request, error_message):
        self.logger.error(f"Request: {request.dict()} | Error: {error_message}")
