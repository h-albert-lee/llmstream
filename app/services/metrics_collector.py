import httpx
import asyncio
from typing import Dict, List


class MetricsCollector:
    def __init__(self, servers: Dict[str, List[str]], update_interval: int = 10):
        """
        MetricsCollector 초기화.
        
        :param servers: 모델별 서버 목록 딕셔너리 {model_name: [server_url1, server_url2, ...]}
        :param update_interval: 메트릭 갱신 주기 (초 단위)
        """
        self.servers = servers
        self.metrics = {model: {} for model in servers.keys()}  # 모델별 메트릭 초기화
        self.update_interval = update_interval
        self.streaming_request_counts = {model: 0 for model in servers.keys()}  # 스트리밍 카운터 추가

    def increment_streaming_count(self, model_name: str):
        if model_name in self.streaming_request_counts:
            self.streaming_request_counts[model_name] += 1

    def get_streaming_count(self, model_name: str) -> int:
        return self.streaming_request_counts.get(model_name, 0)
    
    async def fetch_metrics(self, server_url: str) -> Dict[str, float]:
        """
        주어진 서버의 메트릭을 가져옵니다.
        
        :param server_url: 메트릭을 가져올 서버 URL
        :return: 메트릭 딕셔너리 {metric_name: value}
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{server_url}/metrics")
                response.raise_for_status()
                return self.parse_metrics(response.text)
        except httpx.RequestError as e:
            print(f"Failed to fetch metrics from {server_url}: {e}")
            return {}

    def parse_metrics(self, metrics_text: str) -> Dict[str, float]:
        """
        Prometheus 형식의 메트릭 텍스트를 파싱합니다.
        
        :param metrics_text: 메트릭 텍스트
        :return: 파싱된 메트릭 딕셔너리 {metric_name: value}
        """
        metrics = {}
        for line in metrics_text.splitlines():
            if line.startswith("vllm:num_requests_waiting"):
                _, value = line.split()
                metrics["num_requests_waiting"] = float(value)
        return metrics

    async def update_metrics(self):
        """
        주기적으로 메트릭을 갱신합니다.
        """
        while True:
            for model_name, servers in self.servers.items():
                for server in servers:
                    metrics = await self.fetch_metrics(server)
                    if metrics:
                        self.metrics[model_name][server] = metrics
            await asyncio.sleep(self.update_interval)

    def get_metrics(self, model_name: str) -> Dict[str, Dict[str, float]]:
        """
        특정 모델의 메트릭을 반환합니다.
        
        :param model_name: 모델 이름
        :return: 모델별 메트릭 {server_url: {metric_name: value}}
        """
        return self.metrics.get(model_name, {})
