import random
import json
from typing import Dict, Generator
from concurrent.futures import ThreadPoolExecutor

import requests
import asyncio

from app.services.metrics_collector import MetricsCollector
from app.utils.config_loader import ConfigLoader

class LoadBalancer:
    def __init__(self, metrics_collector: MetricsCollector, config_loader: ConfigLoader):
        self.metrics_collector = metrics_collector
        self.config_loader = config_loader
        self.server_weights = {}
        self.round_robin_counters = {}

        # ThreadPoolExecutor 생성 (필요 시 max_workers 조정)
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def select_server(self, model_name: str = None, is_generate: bool = False) -> str:
        """
        서버 선택 로직.
        """
        if is_generate:
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
            return self._round_robin(list(servers_metrics.keys()), model_name)
        elif strategy == "least_connection":
            return self._least_connection(servers_metrics)
        elif strategy == "random":
            return self._random(list(servers_metrics.keys()))
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

    async def forward_request(
        self, url: str, payload: Dict, headers: Dict, stream: bool = False
    ) -> Generator or Dict:
        """
        요청을 서버에 전달하고 응답을 반환.
        스트리밍 요청을 지원.
        """
        # 동기로 실행할 실제 함수 정의
        def _sync_request(url: str, payload: Dict, headers: Dict, stream: bool):
            headers.pop("Content-Length", None)
            headers["Content-Type"] = "application/json"

            # 동기 requests 호출
            response = requests.post(url, json=payload, headers=headers, stream=stream, timeout=10)
            response.raise_for_status()

            if stream:
                return response.iter_lines(decode_unicode=True)
            else:
                return response.json()

        loop = asyncio.get_running_loop()
        try:
            # 스레드 풀에서 _sync_request 실행
            result = await loop.run_in_executor(
                self.executor,
                _sync_request,
                url,
                payload,
                headers,
                stream,
            )

            if stream:
                # 스트리밍 응답인 경우 제너레이터로 반환
                return result
            else:
                # 일반 응답 반환
                return result
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed to {url}: {e}")

    def _real_time_metrics(self, servers_metrics, model_name):
        self._update_weights(servers_metrics)
        if model_name not in self.round_robin_counters:
            self.round_robin_counters[model_name] = {server: 0 for server in self.server_weights}

        servers = list(self.server_weights.keys())
        weights = list(self.server_weights.values())

        selected_index = random.choices(range(len(servers)), weights=weights, k=1)[0]
        selected_server = servers[selected_index]
        self.round_robin_counters[model_name][selected_server] += 1
        return selected_server

    def _update_weights(self, servers_metrics):
        weights = {}
        k = 0.7  # GPU 사용량 중요도
        m = 0.3  # 대기 요청 수 중요도

        for server, metrics in servers_metrics.items():
            gpu_cache = metrics.get("gpu_cache_usage", 1.0)
            num_waiting = metrics.get("num_requests_waiting", 0)
            weights[server] = 1 / ((k * gpu_cache) + (m * num_waiting) + 1e-6)

        total_weight = sum(weights.values())
        for server in weights:
            weights[server] /= total_weight

        self.server_weights = weights

    def _round_robin(self, servers, model_name):
        if model_name not in self.round_robin_counters:
            self.round_robin_counters[model_name] = 0

        index = self.round_robin_counters[model_name] % len(servers)
        server = servers[index]
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
        return random.choice(servers)
