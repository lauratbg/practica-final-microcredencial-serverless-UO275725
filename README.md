# practica-final-microcredencial-serverless-UO275725

**Alumno:** UO275725  
**URL del API:** https://it2l2ufpef.execute-api.eu-north-1.amazonaws.com/prod  
**Frontend:** http://practica-final-uo275725-bucket.s3-website.eu-north-1.amazonaws.com

---

## Descripción

Aplicación tipo tienda online (Kebab Palace) que permite crear pedidos y consultar su estado en tiempo real. Construida con una arquitectura serverless reactiva sobre AWS.

---

## Arquitectura

```
Frontend (S3)
     │
     ▼
API Gateway (practica-final-api-UO275725)
     │
     ├── POST /orders
     │        │
     │        ▼
     │   Lambda: orders-lambda-uo275725
     │        │
     │        ├──► DynamoDB (orders-practica-final-uo275725) → status: PENDING
     │        │
     │        └──► EventBridge (order-created-rule-uo275725)
     │                    │
     │                    ▼
     │              SQS (orders-queue-uo275725)
     │                    │
     │                    ▼
     │         Lambda: orders-processor-uo275725
     │                    │
     │                    ├──► DynamoDB → status: PROCESSED
     │                    │
     │                    └──► SNS (orders-notifications-uo275725) → Email
     │
     └── GET /orders/{id}
              │
              ▼
         Lambda: orders-lambda-uo275725
              │
              ▼
         DynamoDB → devuelve estado del pedido
```

---

## Servicios AWS utilizados

| Servicio | Nombre | Región |
|---|---|---|
| S3 | `practica-final-uo275725-bucket` | eu-north-1 |
| API Gateway | `practica-final-api-UO275725` | eu-north-1 |
| Lambda | `orders-lambda-uo275725` | eu-north-1 |
| Lambda | `orders-processor-uo275725` | eu-north-1 |
| DynamoDB | `orders-practica-final-uo275725` | us-east-1 |
| EventBridge | `order-created-rule-uo275725` | eu-north-1 |
| SQS | `orders-queue-uo275725` | eu-north-1 |
| SNS | `orders-notifications-uo275725` | eu-north-1 |

---

## Endpoints del API

### POST /orders — Crear pedido

**Request:**
```bash
curl -X POST https://it2l2ufpef.execute-api.eu-north-1.amazonaws.com/prod/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"id":"k1","qty":1,"name":"Kebab pollo","price":7.5}],"extras":[],"notes":""}'
```

**Response:**
```json
{
  "orderId": "kebab-pollo-683024",
  "status": "PENDING"
}
```

### GET /orders/{id} — Consultar estado

**Request:**
```bash
curl https://it2l2ufpef.execute-api.eu-north-1.amazonaws.com/prod/orders/kebab-pollo-683024
```

**Response:**
```json
{
  "orderId": "kebab-pollo-683024",
  "status": "PROCESSED"
}
```

---


## Flujo de un pedido

1. El usuario selecciona productos en el frontend y hace clic en **"Hacer pedido"**
2. El frontend hace `POST /orders` al API Gateway
3. La Lambda `orders-lambda-uo275725`:
   - Genera un ID corto (ej: `kebab-pollo-a3f9c2`)
   - Guarda el pedido en DynamoDB con estado `PENDING`
   - Publica el evento `order.created` en EventBridge
4. EventBridge captura el evento con la regla `order-created-rule-uo275725` y lo envía a la cola SQS `orders-queue-uo275725`
5. SQS dispara la Lambda `orders-processor-uo275725` que:
   - Actualiza el estado del pedido a `PROCESSED` en DynamoDB
   - Envía un email de confirmación via SNS al "UO275725@uniovi.es"
6. El usuario puede consultar el estado con `GET /orders/{id}`

---

