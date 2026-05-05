from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

API_KEY = "test-key"
app = FastAPI()

state = {
    "pwm": 0,
    "relay": False,
    "online": True,
    "temperature": 22.4,
}


def check_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Bad API key")


@app.get("/api/v1/devices")
def devices(x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    return {
        "devices": [
            {
                "id": "esp32_pwm_test_1",
                "name": "ESP32 PWM Test",
                "model": "PWM Controller",
                "manufacturer": "RegSens",
                "entities": [
                    {"id": "pwm", "type": "number", "name": "PWM", "min": 0, "max": 1023, "step": 1, "state": state["pwm"]},
                    {"id": "online", "type": "binary_sensor", "name": "Online", "state": state["online"]},
                    {"id": "temperature", "type": "sensor", "name": "Temperature", "unit": "°C", "state": state["temperature"]},
                    {"id": "relay", "type": "switch", "name": "Relay", "state": state["relay"]}
                ]
            }
        ]
    }


class SetValue(BaseModel):
    value: object


@app.post("/api/v1/devices/{device_id}/entities/{entity_id}/set")
def set_entity(device_id: str, entity_id: str, cmd: SetValue, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    if entity_id == "pwm":
        state["pwm"] = max(0, min(1023, int(float(cmd.value))))
    elif entity_id == "relay":
        state["relay"] = bool(cmd.value)
    else:
        raise HTTPException(status_code=404, detail="Unknown entity")
    return {"ok": True, "device_id": device_id, "entity_id": entity_id, "value": state.get(entity_id)}
