from app.services.load_balancer import LoadBalancer

# 전역적으로 초기화된 load_balancer를 가져오기 위한 의존성 함수
load_balancer = None

def init_dependencies(lb: LoadBalancer):
    global load_balancer
    load_balancer = lb

def get_load_balancer():
    return load_balancer
