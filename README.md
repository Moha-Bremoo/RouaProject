# Ruua - Embedded Finance Platform Backend

A FastAPI-based backend for an embedded finance platform that provides loan offers, instant payments, and fraud detection capabilities.

## Features

- **Loan Offers**: Rule-based loan approval system with instant and installment options
- **Payment Processing**: Secure payment handling with transaction tracking
- **Fraud Detection**: Multi-factor fraud scoring and risk assessment
- **Admin Dashboard**: Transaction and offer management endpoints
- **RESTful API**: Clean, documented API endpoints

## Quick Start

### Prerequisites

- Python 3.8+
- pip or poetry

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd ruua_backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment configuration:
```bash
cp env_example.txt .env
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
docker build -t ruua-backend .
docker run -p 8000:8000 ruua-backend
```

## API Endpoints

### Core Endpoints

- `POST /api/offer` - Create a loan offer
- `POST /api/pay` - Process a payment
- `POST /api/fraud-check` - Perform fraud detection

### Admin Endpoints

- `GET /admin/transactions` - Get all transactions
- `GET /admin/offers` - Get all offers
- `GET /admin/fraud-checks` - Get fraud check results

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Business Rules

### Loan Offer Logic

1. **Instant Approval**: Orders ≤ $200
   - Amount offered: Full order amount
   - Term: 1 month
   - Interest rate: 3%

2. **Installment Approval**: Orders ≤ $1000 AND recent payments ≥ 3
   - Amount offered: Full order amount
   - Term: 2 months
   - Interest rate: 4%

3. **Manual Review**: All other cases

### Fraud Detection

- **Device/Billing Mismatch**: +30 points
- **High Failed Payments**: +40 points (>3 in 30 days)
- **Unusual Amount**: +20 points (>$5000)
- **Multiple Devices**: +25 points (>3 devices)

**Risk Levels**:
- 0-29: Approved
- 30-49: Suspicious (Review)
- 50+: Flagged (Block)

## Example Usage

### Create a Loan Offer

```bash
curl -X POST "http://localhost:8000/api/offer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "order_amount": 150.0,
    "recent_payments": 5,
    "failed_payments_last_30_days": 0,
    "device_country": "US",
    "billing_country": "US",
    "employer_enrolled": true,
    "salary_monthly": 5000.0
  }'
```

### Process Payment

```bash
curl -X POST "http://localhost:8000/api/pay" \
  -H "Content-Type: application/json" \
  -d '{
    "offer_id": "offer-uuid-here"
  }'
```

### Check for Fraud

```bash
curl -X POST "http://localhost:8000/api/fraud-check" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "transaction_amount": 500.0,
    "device_country": "US",
    "billing_country": "CA",
    "device_count": 2,
    "failed_payments_last_30_days": 1
  }'
```

## Database

The application uses SQLAlchemy with support for both SQLite (development) and PostgreSQL (production).

### Models

- **User**: User information and verification status
- **Offer**: Loan offers with terms and conditions
- **Transaction**: Payment transactions and status
- **FraudCheck**: Fraud detection results and flags

## Security Considerations

- Implement proper authentication and authorization
- Use HTTPS in production
- Sanitize all inputs
- Implement rate limiting
- Regular security audits

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
alembic upgrade head
```

### Code Formatting

```bash
black .
isort .
```

## Production Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Use process manager (systemd, supervisor)
5. Enable SSL/TLS
6. Set up monitoring and logging

## License

MIT License - see LICENSE file for details
