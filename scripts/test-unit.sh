#!/bin/bash
set -e

# Unit Test Script - Fast isolated testing with SQLite
# Runs unit tests with SQLite in-memory database for speed and isolation

echo "🧪 Running Unit Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[UNIT]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[UNIT-SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[UNIT-ERROR]${NC} $1"
}

# Set environment for unit testing
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:
export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"

print_status "Unit test environment configured"
print_status "DATABASE_URL: $DATABASE_URL"

# Create test results directory
mkdir -p test-results coverage

# Change to app directory
cd app

# Run unit tests with pytest framework
# pytest: Python testing framework with excellent JUnit XML support
# Features: Fixtures, markers, coverage integration, CircleCI native reporting
print_status "Running unit tests with pytest framework and SQLite in-memory database..."
python -m pytest tests/ -v \
    --junit-xml=../test-results/junit.xml \
    --cov=app \
    --cov-report=xml:../coverage/unit-coverage.xml \
    --cov-report=html:../coverage/unit-html \
    --cov-report=term-missing \
    --tb=short \
    -m "unit and not integration and not container"

if [ $? -eq 0 ]; then
    print_success "Unit tests passed!"
else
    print_error "Unit tests failed!"
    exit 1
fi

# Generate unit test summary
print_status "Unit test summary:"
echo "✅ SQLite in-memory database"
echo "✅ Flask route testing"
echo "✅ Database model validation"
echo "✅ API endpoint verification"
echo "✅ Error handling scenarios"
echo "📊 Coverage report: ../coverage/unit-html/index.html"
echo "📋 JUnit XML: ../test-results/unit-tests.xml"

print_success "Unit tests completed successfully!"
exit 0
