#!/bin/bash
set -e

# Integration Test Script - PostgreSQL sidecar testing
# Runs integration tests with PostgreSQL database for realistic testing

echo "🔗 Running Integration Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INTEGRATION]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[INTEGRATION-SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[INTEGRATION-WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[INTEGRATION-ERROR]${NC} $1"
}

# Set environment for integration testing
export FLASK_ENV=testing
export DATABASE_URL=${DATABASE_URL:-postgresql://testuser:testpass@localhost:5432/testdb}
export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"

print_status "Integration test environment configured"
print_status "DATABASE_URL: $DATABASE_URL"

# Wait for PostgreSQL database (if using sidecar)
if command -v dockerize &> /dev/null; then
    print_status "Waiting for PostgreSQL database..."
    dockerize -wait tcp://localhost:5432 -timeout 2m
    print_success "PostgreSQL database is ready"
else
    print_warning "dockerize not available, assuming database is ready"
    sleep 5
fi

# Create test results directory
mkdir -p test-results coverage

# Change to app directory
cd app

# Run integration tests with pytest + PostgreSQL sidecar
# pytest: Comprehensive testing with database fixtures and markers
# PostgreSQL Sidecar: Off-the-shelf postgres:13 container for realistic testing
# JUnit XML: Native CircleCI integration for test result parsing
print_status "Running integration tests with pytest framework and PostgreSQL sidecar..."
python -m pytest tests/ -v \
    --junit-xml=../test-results/junit.xml \
    --cov=app \
    --cov-report=xml:../coverage/integration-coverage.xml \
    --cov-report=html:../coverage/integration-html \
    --cov-report=term-missing \
    --tb=short \
    -m "integration or database" \
    --cov-fail-under=55

if [ $? -eq 0 ]; then
    print_success "Integration tests passed!"
else
    print_error "Integration tests failed!"
    exit 1
fi

# Run security scan
print_status "Running security scan with bandit..."
cd ..
bandit -r app/app.py -f json -o test-results/security-report.json || print_warning "Security issues found"
bandit -r app/app.py -f txt || print_warning "Security issues found"

# Generate integration test summary
print_status "Integration test summary:"
echo "✅ PostgreSQL sidecar database"
echo "✅ Database connectivity testing"
echo "✅ API integration workflows"
echo "✅ Database transaction testing"
echo "✅ Security scanning completed"
echo "📊 Coverage report: coverage/integration-html/index.html"
echo "📋 JUnit XML: test-results/integration-tests.xml"
echo "🔒 Security report: test-results/security-report.json"

print_success "Integration tests completed successfully!"
exit 0
