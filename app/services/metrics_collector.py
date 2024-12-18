import httpx
import asyncio
from typing import Dict


class MetricsCollector:
    def __init__(self, servers: Dict[str, str], update_interval: int = 10):
        self.servers = servers
        self.metrics = {model: {} for model in servers.keys()}
        self.update_interval = update_interval

    async def fetch_metrics(self, server_url: str) -> Dict[str, float]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{server_url}/metrics")
                response.raise_for_status()
                return self.parse_metrics(response.text)
        except httpx.RequestError as e:
            print(f"Failed to fetch metrics from {server_url}: {e}")
            return {}

    def parse_metrics(self, metrics_text: str) -> Dict[str, float]:
        metrics = {}
        for line in metrics_text.splitlines():
            if line.startswith("vllm:num_requests_waiting"):
                key, value = line.split()
                metrics["num_requests_waiting"] = float(value)
        return metrics

    async def update_metrics(self):
        while True:
            for model_name, servers in self.servers.items():
                for server in servers:
                    metrics = await self.fetch_metrics(server)
                    if metrics:
                        self.metrics[model_name][server] = metrics
            await asyncio.sleep(self.update_interval)

    def get_metrics(self, model_name: str) -> Dict[str, Dict[str, float]]:
        return self.metrics.get(model_name, {})
