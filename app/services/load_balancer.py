import random
from typing import Dict
from app.services.metrics_collector import MetricsCollector
from app.utils.config_loader import ConfigLoader
import httpx

class LoadBalancer:
    def __init__(self, metrics_collector, config_loader):
        self.metrics_collector = metrics_collector
        self.config_loader = config_loader
        self.server_weights = {}  # 서버별 가중치 저장
        self.round_robin_counters = {}  # Weighted Round Robin 카운터

    async def select_server(self, model_name: str = None, is_generate: bool = False) -> str:
        """
        서버 선택 로직
        """
        if is_generate:
            # /generate 요청은 기본 서버로 라우팅
            return self.config_loader.get_default_generate_server()

        if not model_name:
            raise ValueError("model_name must be provided unless is_generate is True")

        servers_metrics = self.metrics_collector.get_metrics(model_name)
        if not servers_metrics:
            return None

        strategy = self.config_loader.get_strategy(model_name)
        if strategy == "real_time_metrics":
            return self._real_time_metrics(servers_metrics, model_name)
        elif strategy == "round_robin":
            return self._round_robin(servers_metrics.keys(), model_name)
        elif strategy == "least_connection":
            return self._least_connection(servers_metrics)
        elif strategy == "random":
            return self._random(servers_metrics.keys())
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

    def _real_time_metrics(self, servers_metrics, model_name):
        """
        Weighted Round Robin을 기반으로 real_time_metrics 방식으로 서버 선택.
        """
        self._update_weights(servers_metrics)

        if model_name not in self.round_robin_counters:
            self.round_robin_counters[model_name] = {server: 0 for server in self.server_weights}

        servers = list(self.server_weights.keys())
        weights = list(self.server_weights.values())

        # Weighted Round Robin 선택
        import random
        selected_index = random.choices(range(len(servers)), weights=weights, k=1)[0]
        selected_server = servers[selected_index]

        # 카운터 업데이트
        self.round_robin_counters[model_name][selected_server] += 1
        return selected_server

    def _update_weights(self, servers_metrics):
        """
        GPU 사용량과 대기 요청 수를 기반으로 가중치를 계산.
        """
        weights = {}
        k = 0.7  # GPU 사용량 중요도
        m = 0.3  # 대기 요청 수 중요도

        for server, metrics in servers_metrics.items():
            gpu_cache = metrics.get("gpu_cache_usage", 1.0)  # GPU 사용량
            num_waiting = metrics.get("num_requests_waiting", 0)  # 대기 요청 수
            weights[server] = 1 / ((k * gpu_cache) + (m * num_waiting) + 1e-6)

        # 가중치 정규화
        total_weight = sum(weights.values())
        for server in weights:
            weights[server] /= total_weight

        self.server_weights = weights

    def _round_robin(self, servers, model_name):
        if model_name not in self.round_robin_counters:
            self.round_robin_counters[model_name] = {server: 0 for server in servers}
        index = self.round_robin_counters[model_name] % len(servers)
        server = list(servers)[index]
        self.round_robin_counters[model_name] += 1
        return server

    def _least_connection(self, servers_metrics):
        if not servers_metrics:
            return None
        sorted_servers = sorted(
            servers_metrics.items(),
            key=lambda item: item[1].get("num_requests_running", float("inf"))
        )
        return sorted_servers[0][0]

    def _random(self, servers):
        if not servers:
            return None
        import random
        return random.choice(list(servers))
