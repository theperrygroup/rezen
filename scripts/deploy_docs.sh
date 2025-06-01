#!/bin/bash

# Documentation Deployment Script for ReZEN Python Client
# This script helps test and deploy documentation locally

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 7 ]; then
        print_error "Python 3.7+ is required, found $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Function to install dependencies
install_deps() {
    print_status "Installing documentation dependencies..."
    
    if [ -f "docs/requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r docs/requirements.txt
        print_success "Dependencies installed"
    else
        print_error "docs/requirements.txt not found"
        exit 1
    fi
}

# Function to validate configuration
validate_config() {
    print_status "Validating MkDocs configuration..."
    
    if [ ! -f "mkdocs.yml" ]; then
        print_error "mkdocs.yml not found"
        exit 1
    fi
    
    # Test MkDocs configuration (without strict mode for validation)
    if mkdocs build --clean --quiet >/dev/null 2>&1; then
        print_success "Configuration is valid"
    else
        print_error "Invalid MkDocs configuration"
        print_status "Run 'mkdocs build' for details"
        exit 1
    fi
}

# Function to build documentation
build_docs() {
    print_status "Building documentation..."
    
    if mkdocs build --clean; then
        print_success "Documentation built successfully"
        print_status "Built files are in ./site/ directory"
        
        # Show warnings if any
        if mkdocs build --clean --strict >/dev/null 2>&1; then
            print_success "No warnings detected"
        else
            print_warning "Some warnings detected (run 'mkdocs build --strict' for details)"
        fi
    else
        print_error "Documentation build failed"
        exit 1
    fi
}

# Function to serve documentation locally
serve_docs() {
    print_status "Starting local development server..."
    print_status "Documentation will be available at: http://127.0.0.1:8000"
    print_status "Press Ctrl+C to stop the server"
    
    mkdocs serve
}

# Function to deploy to GitHub Pages
deploy_github() {
    print_status "Deploying to GitHub Pages..."
    
    if [ ! -d ".git" ]; then
        print_error "Not a git repository"
        exit 1
    fi
    
    # Check if gh-pages branch exists
    if git show-ref --verify --quiet refs/heads/gh-pages; then
        print_status "gh-pages branch exists"
    else
        print_status "Creating gh-pages branch"
        git checkout --orphan gh-pages
        git rm -rf .
        git commit --allow-empty -m "Initial gh-pages commit"
        git checkout main || git checkout master
    fi
    
    mkdocs gh-deploy --clean
    print_success "Deployed to GitHub Pages"
}

# Function to check deployment readiness
check_deployment() {
    print_status "Checking deployment readiness..."
    
    # Check for required files
    REQUIRED_FILES=("mkdocs.yml" "docs/requirements.txt" ".github/workflows/docs.yml")
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "✓ $file exists"
        else
            print_error "✗ $file missing"
            exit 1
        fi
    done
    
    # Check for documentation files
    if [ -d "docs" ] && [ "$(ls -A docs)" ]; then
        print_success "✓ Documentation files found"
    else
        print_error "✗ No documentation files found in docs/"
        exit 1
    fi
    
    print_success "Deployment ready!"
}

# Function to show help
show_help() {
    echo "Documentation Deployment Script for ReZEN Python Client"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install documentation dependencies"
    echo "  validate    Validate MkDocs configuration"
    echo "  build       Build documentation locally"
    echo "  serve       Serve documentation locally for development"
    echo "  deploy      Deploy to GitHub Pages"
    echo "  check       Check if project is ready for deployment"
    echo "  test        Run all tests (validate + build)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install        # Install dependencies"
    echo "  $0 serve          # Start local development server"
    echo "  $0 build          # Build documentation"
    echo "  $0 deploy         # Deploy to GitHub Pages"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "install")
        check_python
        install_deps
        ;;
    "validate")
        validate_config
        ;;
    "build")
        check_python
        validate_config
        build_docs
        ;;
    "serve")
        check_python
        validate_config
        serve_docs
        ;;
    "deploy")
        check_python
        validate_config
        deploy_github
        ;;
    "check")
        check_python
        check_deployment
        ;;
    "test")
        check_python
        validate_config
        build_docs
        print_success "All tests passed!"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 