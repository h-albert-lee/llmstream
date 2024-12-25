import json


class ConfigLoader:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error parsing configuration file: {e}")

    def get_model_config(self, model_name: str):
        return self.config.get("models", {}).get(model_name, {})

    def get_servers(self, model_name: str):
        model_config = self.get_model_config(model_name)
        return model_config.get("servers", [])

    def get_strategy(self, model_name: str):
        model_config = self.get_model_config(model_name)
        return model_config.get("strategy", "round_robin")

    def get_metrics_update_interval(self):
        return self.config.get("metrics_update_interval", 10)

    def get_default_generate_server(self):
        return self.config.get("default_generate_server")
