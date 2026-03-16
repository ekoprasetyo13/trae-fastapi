# trae-fastapi

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: http://localhost:8000/docs-api

## Auth

- Register: `POST /register` (JSON body)
- Login: `POST /token` (form body: `username`, `password`) -> returns Bearer token
- Private endpoints require `Authorization: Bearer <token>`

## OpenTelemetry

Traces are exported via OTLP/HTTP.

- Default traces endpoint: `http://172.15.1.100:4318/v1/traces`
- Override endpoints:
  - `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://172.15.1.100:4318/v1/traces`
  - or `OTEL_EXPORTER_OTLP_ENDPOINT=http://172.15.1.100:4318` (base endpoint)
- Set service name: `OTEL_SERVICE_NAME=trae-fastapi`
- Disable telemetry: `OTEL_DISABLED=true`
