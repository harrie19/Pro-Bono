# Policy Check Service

## Endpoint
- **Host:** `127.0.0.1`
- **Port:** `8080`
- **Health:** `GET /health`
- **Decision:** `POST /policy_check`

## Request Example
```json
{
  "command": "read file.txt",
  "context": {
    "user_role": "admin",
    "user_id": "local_cli"
  }
}
```

## Response Example
```json
{
  "policy_status": "approved",
  "timestamp": "2025-12-08T16:00:00Z",
  "command": "read file.txt",
  "reason": "Command approved",
  "metadata": {
    "service": "policy-check-flask",
    "checked_at": "2025-12-08T16:00:00Z",
    "user_role": "admin"
  }
}
```

## Quick Test
```bash
curl -X POST http://127.0.0.1:8080/policy_check \
  -H "Content-Type: application/json" \
  -d '{"command": "read file.txt", "context": {"user_role": "admin"}}'
```

