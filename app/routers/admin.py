from fastapi import APIRouter, HTTPException
from app.utils.config_loader import ConfigLoader

router = APIRouter()
config_loader = ConfigLoader()

@router.get("/models")
async def list_models():
    return config_loader.get_models()

@router.post("/models")
async def add_model(model_name: str, servers: list[str], strategy: str = "round_robin"):
    models = config_loader.get_models()
    if model_name in models:
        raise HTTPException(status_code=400, detail="Model already exists")
    models[model_name] = {"servers": servers, "strategy": strategy}
    config_loader.save_config(models)
    return {"message": f"Model {model_name} added successfully."}

@router.put("/models/{model_name}")
async def update_model(model_name: str, servers: list[str] = None, strategy: str = None):
    models = config_loader.get_models()
    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    if servers:
        models[model_name]["servers"] = servers
    if strategy:
        models[model_name]["strategy"] = strategy
    config_loader.save_config(models)
    return {"message": f"Model {model_name} updated successfully."}

@router.delete("/models/{model_name}")
async def delete_model(model_name: str):
    models = config_loader.get_models()
    if model_name in models:
        del models[model_name]
        config_loader.save_config(models)
        return {"message": f"Model {model_name} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
