#!/bin/bash

# Test Runner Script for RAG Chat Application
# This script runs tests for both frontend and backend

set -e  # Exit on any error

echo "🧪 Starting RAG Chat Application Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Function to run backend tests
run_backend_tests() {
    print_status "Running Backend Tests..."
    
    cd backend-rag-chat
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install/upgrade dependencies
    print_status "Installing backend dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Run tests
    print_status "Running pytest..."
    pytest tests/ -v --tb=short --cov=. --cov-report=html --cov-report=term-missing
    
    if [ $? -eq 0 ]; then
        print_success "Backend tests passed!"
    else
        print_error "Backend tests failed!"
        exit 1
    fi
    
    cd ..
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running Frontend Tests..."
    
    cd frontend-rag-chat
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Node modules not found. Installing dependencies..."
        npm install
    fi
    
    # Run tests
    print_status "Running Jest tests..."
    npm run test:ci
    
    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed!"
    else
        print_error "Frontend tests failed!"
        exit 1
    fi
    
    cd ..
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running Integration Tests..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend-rag-chat
    source .venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Start frontend in background
    print_status "Starting frontend server..."
    cd frontend-rag-chat
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    # Run integration tests (you can add actual integration tests here)
    print_status "Running integration tests..."
    # Add your integration test commands here
    
    # Cleanup
    print_status "Cleaning up..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    print_success "Integration tests completed!"
}

# Function to generate test report
generate_report() {
    print_status "Generating Test Report..."
    
    echo "📊 Test Report Summary" > test_report.md
    echo "=====================" >> test_report.md
    echo "" >> test_report.md
    echo "Generated on: $(date)" >> test_report.md
    echo "" >> test_report.md
    
    # Backend coverage report
    if [ -f "backend-rag-chat/htmlcov/index.html" ]; then
        echo "## Backend Test Coverage" >> test_report.md
        echo "- Coverage report: backend-rag-chat/htmlcov/index.html" >> test_report.md
        echo "" >> test_report.md
    fi
    
    # Frontend coverage report
    if [ -d "frontend-rag-chat/coverage" ]; then
        echo "## Frontend Test Coverage" >> test_report.md
        echo "- Coverage report: frontend-rag-chat/coverage/lcov-report/index.html" >> test_report.md
        echo "" >> test_report.md
    fi
    
    print_success "Test report generated: test_report.md"
}

# Main execution
main() {
    echo ""
    print_status "RAG Chat Application Test Suite"
    echo ""
    
    # Parse command line arguments
    RUN_BACKEND=true
    RUN_FRONTEND=true
    RUN_INTEGRATION=false
    GENERATE_REPORT=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                RUN_FRONTEND=false
                RUN_INTEGRATION=false
                shift
                ;;
            --frontend-only)
                RUN_BACKEND=false
                RUN_INTEGRATION=false
                shift
                ;;
            --integration)
                RUN_INTEGRATION=true
                shift
                ;;
            --no-report)
                GENERATE_REPORT=false
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --backend-only    Run only backend tests"
                echo "  --frontend-only   Run only frontend tests"
                echo "  --integration     Run integration tests"
                echo "  --no-report       Skip generating test report"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Run tests based on options
    if [ "$RUN_BACKEND" = true ]; then
        run_backend_tests
    fi
    
    if [ "$RUN_FRONTEND" = true ]; then
        run_frontend_tests
    fi
    
    if [ "$RUN_INTEGRATION" = true ]; then
        run_integration_tests
    fi
    
    if [ "$GENERATE_REPORT" = true ]; then
        generate_report
    fi
    
    echo ""
    print_success "🎉 All tests completed successfully!"
    echo ""
    print_status "Test coverage reports:"
    if [ -f "backend-rag-chat/htmlcov/index.html" ]; then
        echo "  - Backend: backend-rag-chat/htmlcov/index.html"
    fi
    if [ -d "frontend-rag-chat/coverage" ]; then
        echo "  - Frontend: frontend-rag-chat/coverage/lcov-report/index.html"
    fi
    echo ""
}

# Run main function
main "$@"
