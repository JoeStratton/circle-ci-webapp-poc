# CircleCI WebApp POC 

** AWS Cost-optimized CI/CD pipeline demonstration **

## 🎯 What This Project Does

This project demonstrates a production-ready Flask web application with PostgreSQL sidecar containers, comprehensive testing, and cost-optimized AWS deployment.

**Live Demo Features:**
- 🌐 **Interactive Web UI**: Modern responsive interface with dark mode toggle
- 👥 **User Management**: Real-time test operations with form validation
- 🔍 **Health Monitoring**: Database connectivity and application status endpoints
- 📊 **RESTful API**: Complete user management with JSON responses
- 🗄️ **PostgreSQL Sidecar**: Off-the-shelf database container architecture
- 🎨 **Dark Mode**: Persistent theme switching with localStorage
- ⚡ **Real-time Updates**: Dynamic UI updates without page refresh

## 🏗️ Architecture Overview

### High-Level Design
```
GitHub → CircleCI → AWS ECS (Flask + PostgreSQL Sidecars)
```

### Container Architecture
- **Main Container**: Flask web application
- **Sidecar Container**: PostgreSQL database (off-the-shelf `postgres:13` image)
- **Network**: Containers share localhost in same ECS task
- **Dependency**: App waits for database health before starting

### Database Strategy
- **Production**: PostgreSQL sidecar container (no RDS costs)
- **Testing**: PostgreSQL sidecar in CircleCI pipeline
- **Development**: SQLite fallback for local development

## 🚀 Quick Start

### Prerequisites
- GitHub account with admin access
- CircleCI account
- AWS account with ECS/ECR/S3 permissions
- Terraform installed locally

### 5-Minute Setup
```bash
# 1. Clone and test locally
git clone https://github.com/JoeStratton/circle-ci-webapp-poc.git
cd circle-ci-webapp-poc
./scripts/test-unit.sh  # Fast unit tests

# 2. Create S3 bucket for Terraform state (required first)
aws s3 mb s3://YOUR_UNIQUE_BUCKET_NAME --region us-east-1

# 3. Configure Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your values:
# - circleci_organization_id (from CircleCI dashboard)
# - circleci_project_id (from CircleCI dashboard)
# - state_bucket (use the bucket name from step 2)

# 4. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 5. Configure CircleCI context
# Add these environment variables to CircleCI project settings:
# - AWS_ACCOUNT_ID
# - AWS_ROLE_ARN (from terraform output)
# - AWS_REGION
# - DATABASE_PASSWORD
# - CIRCLECI_ORGANIZATION_ID
# - CIRCLECI_PROJECT_ID

# 6. Push to main branch triggers deployment
git push origin main
```

## 🧪 Local Testing

### Prerequisites for Local Testing
```bash
# Install Python dependencies
cd app
pip install -r requirements.txt

# Install additional testing tools (optional)
pip install bandit  # For security scanning
pip install flake8  # For code quality and linting
```

### Running Tests Locally

#### 1. Unit Tests (Fast & Isolated)
```bash
# Quick unit tests with SQLite in-memory database
./scripts/test-unit.sh

# Testing Framework: pytest + SQLite in-memory
# What it tests:
# ✅ Flask routes and API endpoints
# ✅ Database models and validation
# ✅ Error handling scenarios
# ✅ Fast execution (~30 seconds)
# 📊 Generates coverage report: coverage/unit-html/index.html
```

#### 2. Integration Tests (PostgreSQL Sidecar)
```bash
# Start PostgreSQL sidecar container
docker run -d --name test-postgres \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:13

# Run integration tests
./scripts/test-integration.sh

# Cleanup
docker stop test-postgres && docker rm test-postgres

# Testing Framework: pytest + PostgreSQL sidecar + bandit security scanning
# What it tests:
# ✅ PostgreSQL database connectivity
# ✅ Database transactions and migrations
# ✅ API integration workflows
# ✅ Security scanning with bandit
# 📊 Generates coverage report: coverage/integration-html/index.html
```

#### 3. Container Tests (Docker Validation)
```bash
# Test containerized application behavior
./scripts/test-container.sh

# Testing Framework: dgoss + pytest + Docker
# What it tests:
# ✅ Docker image builds successfully
# ✅ Container starts and responds to health checks
# ✅ Port 5000 is accessible
# ✅ Gunicorn process runs correctly
# ✅ Non-root user security (appuser:999)
# ✅ HTTP endpoints return expected responses
# 📋 Generates JUnit XML: test-results/container-validation.xml
```

#### 4. Code Quality & Linting
```bash
# Run code quality checks
flake8 app/app.py --max-line-length=120 --statistics

# Check Python syntax
python -m py_compile app/app.py

# Verify dependencies
pip check

# Testing Framework: flake8 + py_compile + pip check
# What it checks:
# ✅ Code style and formatting (PEP 8 compliance)
# ✅ Python syntax validation
# ✅ Dependency compatibility
# ✅ Line length limits (120 characters)
# 📊 Generates statistics on code quality issues
```

#### Test Output Locations
- **Unit Tests**: `coverage/unit-html/index.html`
- **Integration Tests**: `coverage/integration-html/index.html`
- **Container Tests**: `coverage/container-html/index.html`
- **JUnit XML**: `test-results/*.xml`
- **Security Report**: `test-results/security-report.json`

## 🧪 Testing Strategy

### Three-Stage Pipeline Testing
1. **Unit Tests** (`scripts/test-unit.sh`): SQLite in-memory for fast isolation
2. **Integration Tests** (`scripts/test-integration.sh`): PostgreSQL sidecar testing
3. **Container Tests** (`scripts/test-container.sh`): dgoss validation + container behavior

### CircleCI Integration
- **JUnit XML**: Native test result parsing in CircleCI UI
- **Coverage Reports**: HTML and XML artifacts with 70% minimum
- **Database Testing**: PostgreSQL sidecar containers in pipeline
- **Security Scanning**: bandit static analysis

## 🔐 Security Features

### OIDC Authentication
- **No Static Credentials**: All AWS access via temporary OIDC tokens
- **Branch Protection**: Production access restricted to main branch only
- **Least Privilege**: IAM roles with minimal required permissions

### Container Security
- **Non-Root User**: Application runs as dedicated user
- **Minimal Base**: Python slim image with only required packages
- **Secure Credentials**: Database credentials via CircleCI contexts (encrypted)
- **Security Scanning**: Automated vulnerability analysis
- **Network Isolation**: Default VPC with security groups

## 🔄 CI/CD Pipeline

### Branch-Based Execution
- **All Branches**: Code quality → Unit tests → Integration tests → Docker build → Container tests
- **Main Branch Only**: + ECR push → Terraform validation → Terraform plan → Terraform apply
- **Dev Branches**: Full testing and Docker build, but no AWS deployment

### Terraform Integration
- **Format Check**: `terraform fmt -check` validates code formatting
- **Validation**: `terraform validate` checks configuration syntax
- **Planning**: `terraform plan` shows infrastructure changes
- **Deployment**: `terraform apply` updates AWS resources

## 🗄️ Database Implementation

### PostgreSQL Sidecar Details
- **Container Image**: `postgres:13` (off-the-shelf Docker image)
- **Connection**: App connects to `localhost:5432` (same ECS task)
- **Health Check**: `pg_isready` validation before app startup
- **Initialization**: Automatic schema creation + sample data
- **Credentials**: Stored securely in CircleCI contexts (encrypted, branch-restricted)

### Database Models
```python
class User(db.Model):
    # User management with CRUD operations
    id, username, email, created_at
    # JSON serialization with null-safe datetime handling

class HealthCheck(db.Model):
    # Health monitoring with automatic logging
    id, timestamp, status
    # Tracks application and database health status
```

## 🔧 Key Technologies 

### Application Stack
- **Language**: Python
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with Flask-Migrate 
- **Web Server**: Gunicorn 
- **Frontend**: HTML5, CSS3, JavaScript
- **Testing**: pytest with JUnit XML integration

### Infrastructure Stack
- **Containers**: Docker
- **Orchestration**: AWS ECS Fargate
- **Registry**: Amazon ECR
- **Storage**: S3
- **Infrastructure**: Terraform

### CI/CD Stack
- **Source Control**: GitHub
- **CI/CD**: CircleCI
- **Testing Frameworks**: pytest (unit/integration), dgoss (container), JUnit XML
- **Security**: OIDC authentication
- **Container Testing**: dgoss for behavior validation
- **Deployment**: Terraform-managed infrastructure

## 📁 Repository Structure

```
circle-ci-webapp-poc/
├── 📖 README.md              # This overview
├── 🎨 architecture.mermaid   # Visual architecture diagram
│
├── 📂 app/                   # Application code
│   ├── app.py               # Flask application entry point
│   ├── models.py            # SQLAlchemy database models
│   ├── routes.py            # Flask routes and API endpoints
│   ├── config.py            # Application configuration
│   ├── requirements.txt     # Python dependencies
│   ├── templates/           # HTML templates
│   │   └── index.html       # Main web interface
│   ├── static/              # Static assets
│   │   ├── css/style.css    # Styles with dark mode support
│   │   └── js/app.js        # JavaScript functionality
│   └── tests/               # Test suite
│       ├── pytest.ini      # Test configuration
│       ├── conftest.py      # Test fixtures
│       ├── test_app.py      # Unit tests
│       ├── test_app_init.py # App initialization tests
│       └── test_container.py # Container tests
│
├── 📂 docker/                # Container configuration
│   ├── Dockerfile           # Multi-stage container build
│   └── .dockerignore        # Docker build exclusions
│
├── 📂 terraform/             # Complete infrastructure (OIDC, IAM, ECS, ECR, S3)
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Input variables
│   ├── terraform.tfvars.example # Example variables file
│   ├── ecs.tf               # ECS cluster and service
│   ├── ecr.tf               # ECR repository
│   ├── iam.tf               # IAM roles and policies
│   ├── oidc.tf              # OIDC configuration
│   └── outputs.tf           # Output values
│
├── 📂 .circleci/             # CI/CD pipeline
│   └── config.yml           # CircleCI configuration
│
└── 📂 scripts/               # Test scripts and utilities
    ├── test-unit.sh         # Unit tests (pytest + SQLite + JUnit XML)
    ├── test-integration.sh  # Integration tests (pytest + PostgreSQL sidecar)
    ├── test-container.sh    # Container tests (dgoss + pytest)
    └── init-db.sql          # Database initialization
```
