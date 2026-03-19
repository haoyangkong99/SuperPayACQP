# SuperPayACQP

A Django-based ACQP (Acquiring Partner) system that integrates with Alipay+ payment network, supporting payment processing, cancellation, refund, inquiry, and notification workflows.

## Features

- **Place Order API**: Create orders and initiate payments
- **Cancel Payment API**: Cancel pending payments
- **Refund API**: Process refund requests
- **Inquiry Payment API**: Query payment status
- **Notify Payment Callback**: Receive payment notifications from Alipay+

## Project Structure

```
SuperPayACQP/
├── superpayacqp/          # Django project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── apps/                  # Django applications
│   ├── users/             # User management
│   ├── merchants/         # Merchant management
│   ├── orders/            # Order management
│   ├── payments/          # Payment processing
│   ├── refunds/           # Refund management
│   └── api_records/       # API logging
├── dtos/                  # Data Transfer Objects
│   ├── __init__.py        # Base DTOs
│   ├── request.py         # Request DTOs
│   ├── response.py        # Response DTOs
│   └── alipay_request.py  # Alipay+ specific DTOs
├── services/              # Business services
│   ├── alipay_client.py   # Alipay+ API client
│   └── signature_service.py # RSA signature handling
├── middleware/            # Custom middleware
│   └── merchant_auth.py   # Merchant authentication
├── utils/                 # Utility functions
│   ├── constants.py       # Constants and enums
│   ├── exceptions.py      # Custom exceptions
│   └── helpers.py         # Helper functions
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variables template
```

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone the repository**
   ```bash
   cd SuperPayACQP
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/place-order` | POST | Place an order and initiate payment |
| `/api/cancel-payment` | POST | Cancel a payment |
| `/api/refund` | POST | Initiate a refund |
| `/api/inquiryPayment` | POST | Query payment status |
| `/alipay/notifyPayment` | POST | Receive Alipay+ notifications |
| `/api/docs/` | GET | Swagger API documentation |
| `/api/schema/` | GET | OpenAPI schema |

## Request Headers

All merchant-facing endpoints require the following headers:

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Must be `application/json` |
| `Merchant-ID` | Yes | Merchant identifier |

## Example Requests

### Place Order

```bash
curl -X POST http://localhost:8000/api/place-order \
  -H "Content-Type: application/json" \
  -H "Merchant-ID: your-merchant-id" \
  -d '{
    "order": {
      "referenceOrderId": "ORDER-001",
      "orderDescription": "Test Order",
      "orderAmount": {
        "currency": "MYR",
        "value": 1000
      },
      "merchantId": "your-merchant-id"
    }
  }'
```

### Cancel Payment

```bash
curl -X POST http://localhost:8000/api/cancel-payment \
  -H "Content-Type: application/json" \
  -H "Merchant-ID: your-merchant-id" \
  -d '{
    "paymentId": "payment-id",
    "paymentRequestId": "request-id"
  }'
```

### Refund

```bash
curl -X POST http://localhost:8000/api/refund \
  -H "Content-Type: application/json" \
  -H "Merchant-ID: your-merchant-id" \
  -d '{
    "paymentRequestId": "request-id",
    "paymentId": "payment-id",
    "refundRequestId": "refund-001",
    "refundAmount": {
      "currency": "MYR",
      "value": 500
    },
    "refundReason": "Customer request"
  }'
```

### Inquiry Payment

```bash
curl -X POST http://localhost:8000/api/inquiryPayment \
  -H "Content-Type: application/json" \
  -H "Merchant-ID: your-merchant-id" \
  -d '{
    "paymentId": "payment-id",
    "paymentRequestId": "request-id"
  }'
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DEBUG` | Enable debug mode (True/False) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `ALIPAY_PUBLIC_KEY` | Alipay+ public key (Base64) |
| `ALIPAY_PRIVATE_KEY` | SuperPayACQP private key (Base64) |
| `ALIPAY_CLIENT_ID` | Alipay+ client identifier |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins |

## Security

- **RSA-SHA256 Signatures**: All Alipay+ API requests/responses are signed
- **Merchant Authentication**: Merchant-ID header validation
- **Request Validation**: Pydantic DTOs for type-safe request handling

## Testing

Run tests with pytest:

```bash
pytest
```

## License

This project is proprietary and confidential.

## Support

For support, please contact the development team.
