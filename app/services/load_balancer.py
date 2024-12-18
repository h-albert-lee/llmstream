class LoadBalancer:
    def __init__(self, metrics_collector, config_loader):
        self.metrics_collector = metrics_collector
        self.config_loader = config_loader
        self.round_robin_counters = {}  # 모델별 라운드 로빈 카운터

    async def select_server(self, model_name: str) -> str:
        servers = self.config_loader.get_servers(model_name)
        if not servers:
            return None

        strategy = self.config_loader.get_strategy(model_name)
        servers_metrics = self.metrics_collector.get_metrics(model_name)

        if strategy == "round_robin":
            return self._round_robin(servers, model_name)
        elif strategy == "least_connection":
            return self._least_connection(servers_metrics)
        elif strategy == "real_time_metrics":
            return self._real_time_metrics(servers_metrics)
        elif strategy == "random":
            return self._random(servers)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

    def _round_robin(self, servers, model_name):
        if model_name not in self.round_robin_counters:
            self.round_robin_counters[model_name] = 0
        index = self.round_robin_counters[model_name] % len(servers)
        self.round_robin_counters[model_name] += 1
        return servers[index]

    def _least_connection(self, servers_metrics):
        if not servers_metrics:
            return None
        sorted_servers = sorted(
            servers_metrics.items(),
            key=lambda item: item[1].get("num_requests_running", float("inf"))
        )
        return sorted_servers[0][0]

    def _real_time_metrics(self, servers_metrics):
        sorted_servers = sorted(
            servers_metrics.items(),
            key=lambda item: item[1].get("num_requests_waiting", float("inf"))
        )
        return sorted_servers[0][0] if sorted_servers else None

    def _random(self, servers):
        if not servers:
            return None
        import random
        return random.choice(servers)