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
# 1. Clone and push to your GitHub repository
git clone https://github.com/YOUR_USERNAME/circle-ci-webapp-poc.git
cd circle-ci-webapp-poc
git push origin main

# 2. Test locally first (recommended)
./scripts/test-unit.sh  # Fast unit tests
docker build --platform linux/amd64 -f docker/Dockerfile -t circle-ci-webapp-poc-app:latest .

# 3. Deploy complete infrastructure (simplified one-step)
cd terraform
terraform apply

# 4. Configure CircleCI context with OIDC role
# 5. Push to main branch triggers application deployment
```

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
- **Main Branch Only**: + ECR push → Terraform deployment
- **Dev Branches**: Full testing and Docker build, but no deployment

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
│   ├── pytest.ini           # Test configuration
│   ├── templates/           # HTML templates
│   │   └── index.html       # Main web interface
│   ├── static/              # Static assets
│   │   ├── css/style.css    # Styles with dark mode support
│   │   └── js/app.js        # JavaScript functionality
│   └── tests/               # Three-stage test suite
│
├── 📂 docker/                # Container configuration
│   ├── Dockerfile           # Multi-stage container build
│   └── .dockerignore        # Docker build exclusions
│
├── 📂 terraform/             # Complete infrastructure (OIDC, IAM, ECS, ECR, S3)
├── 📂 .circleci/             # CI/CD pipeline with terraform integration
└── 📂 scripts/               # Independent test scripts and database initialization
    ├── test-unit.sh         # Unit tests (pytest + SQLite + JUnit XML)
    ├── test-integration.sh  # Integration tests (pytest + PostgreSQL sidecar)
    ├── test-container.sh    # Container tests (dgoss + pytest)
    └── init-db.sql          # Database initialization
```
