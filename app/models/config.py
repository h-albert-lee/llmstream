import json

class ConfigManager:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def get_all_models(self):
        return list(self.config["models"].keys())

    def get_servers_for_model(self, model_name):
        return self.config["models"].get(model_name, [])

    def add_model(self, model_name, servers):
        self.config["models"][model_name] = servers
        self._save_config()

    def remove_model(self, model_name):
        if model_name in self.config["models"]:
            del self.config["models"][model_name]
            self._save_config()

    def _save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)
