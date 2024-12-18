class Logger:
    def log_request(self, request, response):
        print(f"Request: {request.dict()} | Response: {response}")

    def log_error(self, request, error_message):
        print(f"Request: {request.dict()} | Error: {error_message}")
