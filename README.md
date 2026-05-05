# RegSens Home Assistant Integration

HACS-ready custom integration for RegSens devices.

## Install with HACS custom repository

1. In Home Assistant open HACS.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/regimantas/regsens-ha`.
4. Category: **Integration**.
5. Install **RegSens**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration → RegSens**.
8. Enter your RegSens API URL and API key.

## Server implementation

The RegSens server source code is intentionally not included in this repository.

The server can be written in Go, Python, Node.js, Rust, or any other language. The Home Assistant integration only needs an HTTP JSON API that matches the format below.

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
