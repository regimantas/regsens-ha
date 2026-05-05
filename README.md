# RegSens Home Assistant Integration

HACS-ready custom integration for RegSens devices.

## Test API server

`example_server.py` is a local mock server for testing the integration. It is not a production server.

Run it with:

```bash
pip install fastapi uvicorn
uvicorn example_server:app --reload
```

Then add RegSens in Home Assistant with:

- API URL: `http://127.0.0.1:8000`
- API key: `test-key`

## Install with HACS custom repository

1. Upload this repository to GitHub, for example `regsens-ha`.
2. In Home Assistant open HACS.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add your GitHub repository URL.
5. Category: **Integration**.
6. Install **RegSens**.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add integration → RegSens**.

## API format expected

The integration expects an API endpoint:

`GET /api/v1/devices`

with header:

`X-API-Key: your-api-key`

Example response:

```json
{
  "devices": [
    {
      "id": "esp32_pwm_test_1",
      "name": "ESP32 PWM Test",
      "model": "PWM Controller",
      "manufacturer": "RegSens",
      "entities": [
        {"id":"pwm","type":"number","name":"PWM","min":0,"max":1023,"step":1,"state":0},
        {"id":"online","type":"binary_sensor","name":"Online","state":true},
        {"id":"temperature","type":"sensor","name":"Temperature","unit":"°C","state":22.4},
        {"id":"relay","type":"switch","name":"Relay","state":false}
      ]
    }
  ]
}
```

Commands:

`POST /api/v1/devices/{device_id}/entities/{entity_id}/set`

Payload:

```json
{"value": 500}
```
