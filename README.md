# LLMStream

LLMStream is a scalable and efficient REST API designed to handle load-balanced inference requests for large language models (LLMs) with OpenAI Compatible API. The system dynamically selects the optimal server based on real-time metrics or predefined strategies.

## **Cautions**
This is an experimental router for LLM. If you need a production-level router for LLM Service, please use [LiteLLM](https://github.com/BerriAI/litellm)

## **Features**

- **Chat and Completions APIs** (OpenAI Compatible APIs only (ex. vllm serve)):
  - `/v1/chat/completions`: Handles chat-based completion requests.
  - `/v1/completions`: Handles standard text generation requests.
- **Dynamic Load Balancing**:
  - Supports multiple strategies (e.g., round robin, least connection, real-time metrics).
  - Configurable per model via `config.json`.
- **Admin API**:
  - Manage models and server mappings dynamically via REST endpoints.
- **Real-Time Metrics Integration**:
  - Collects metrics from `/metrics` endpoints exposed by vLLM servers for intelligent load balancing. "Real-time metrics" Strategy dynamically selects servers using Weighted Round Robin based on real-time metrics such as GPU cache usage and the number of waiting requests. This ensures balanced load distribution and adapts to changing server conditions.

---

## **Setup**

### **1. Prerequisites**
- Python 3.9 or higher.
- `pip` package manager.

### **2. Installation**
Clone the repository and install the dependencies:
```bash
git clone https://github.com/your-username/llmstream.git
cd llmstream
pip install -r requirements.txt
```

### **3. Configuration**
Update the `config.json` file to define the models, servers, and load-balancing strategies:
```json
{
  "models": {
    "gpt-3.5-turbo": {
      "servers": ["http://node1:8000", "http://node2:8000"],
      "strategy": "round_robin"
    },
    "gpt-4": {
      "servers": ["http://node3:8000", "http://node4:8000"],
      "strategy": "real_time_metrics"
    }
  },
  "metrics_update_interval": 10
}
```

- `servers`: List of server endpoints hosting the model.
- `strategy`: Load-balancing strategy for the model (`round_robin`, `least_connection`, `real_time_metrics`, `random`).
- `metrics_update_interval`: Interval (in seconds) to fetch metrics from the servers.

### **4. Running the Server**
Start the FastAPI application using `uvicorn`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be accessible at `http://localhost:8000`.

---

## **Usage**

### **1. Chat Completions API**
Send a POST request to `/v1/chat/completions`:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": "Hello, how are you?"}],
  "max_tokens": 100,
  "temperature": 0.7
}'
```

### **2. Completions API**
Send a POST request to `/v1/completions`:
```bash
curl -X POST http://localhost:8000/v1/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "gpt-4",
  "prompt": "Write a story about AI",
  "max_tokens": 200,
  "temperature": 0.7
}'
```

### **3. Admin API**
#### **List Models**
```bash
curl -X GET http://localhost:8000/admin/models
```

#### **Add a New Model**
```bash
curl -X POST http://localhost:8000/admin/models \
-H "Content-Type: application/json" \
-d '{
  "model_name": "gpt-neo",
  "servers": ["http://node5:8000", "http://node6:8000"],
  "strategy": "least_connection"
}'
```

#### **Update a Model**
```bash
curl -X PUT http://localhost:8000/admin/models/gpt-4 \
-H "Content-Type: application/json" \
-d '{
  "servers": ["http://node3:8000", "http://node4:8000"],
  "strategy": "round_robin"
}'
```

#### **Delete a Model**
```bash
curl -X DELETE http://localhost:8000/admin/models/gpt-4
```

---

## **Customization**

### **Adding New Load Balancing Strategies**
To add a custom strategy:
1. Implement the strategy logic in `LoadBalancer` (in `services/load_balancer.py`).
2. Update the `config.json` file to use the new strategy.


---

## **Future Improvements**
- Add authentication and authorization for the Admin API.
- Extend metrics support for more performance indicators.
- Add more load balancing strategies (e.g., weighted round robin).
- Integrate monitoring tools like Prometheus and Grafana.




