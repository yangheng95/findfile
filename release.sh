#!/bin/bash
# Author: Yang, Heng
# Date: 2023-01-26
# Description: Release to pypi and github
# Usage: ./release.sh "release note" [--force]

set -e  # Exit immediately if a command exits with a non-zero status

# Parse arguments
release_note=$1
force=$2
# Configuration
PYPI_TOKEN=${PYPI_TOKEN:-""}
BRANCH=${BRANCH:-"master"}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up build artifacts..."
    rm -rf build dist *.egg-info .eggs
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if required tools are installed
    if ! command -v python &> /dev/null; then
        log_error "Python is not installed or not in PATH"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        log_error "Git is not installed or not in PATH"
        exit 1
    fi

    if ! python -c "import twine" &> /dev/null; then
        log_error "Twine is not installed. Please run: pip install twine"
        exit 1
    fi

    if ! python -c "import black" &> /dev/null; then
        log_warning "Black is not installed. Skipping code formatting."
    fi

    # Check if PYPI_TOKEN is set
    if [ -z "$PYPI_TOKEN" ]; then
        log_error "PYPI_TOKEN environment variable is not set"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Validate arguments
validate_arguments() {
    if [ -z "$release_note" ]; then
        log_error "Please provide a release note"
        echo "Usage: $0 \"release note\" [--force]"
        exit 1
    fi

    if [ "$force" = "--force" ]; then
        log_warning "Force mode enabled - will skip some checks"
    fi
}

# Format code
format_code() {
    log_info "Formatting code with black..."
    if command -v black &> /dev/null; then
        black omnigenome omnigenbench || {
            log_warning "Black formatting failed, continuing anyway"
        }
    else
        log_warning "Black not available, skipping code formatting"
    fi
}

# Check git status
check_git_status() {
    if [ "$force" != "--force" ]; then
        log_info "Checking git status..."

        # Check if there are uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            log_warning "There are uncommitted changes in the working directory"
            if [ "$force" != "--force" ]; then
                read -p "Continue anyway? (y/n): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_error "Aborted by user"
                    exit 1
                fi
            fi
        fi

        # Check if current branch is up to date with remote
        git fetch origin
        if [ "$(git rev-parse HEAD)" != "$(git rev-parse @{u})" ]; then
            log_warning "Local branch is not up to date with remote"
            if [ "$force" != "--force" ]; then
                read -p "Continue anyway? (y/n): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_error "Aborted by user"
                    exit 1
                fi
            fi
        fi
    fi
}

# Commit and push changes
commit_and_push() {
    log_info "Committing and pushing changes..."

    git add -u

    git commit -m "$release_note" || {
        log_warning "Nothing to commit or commit failed"
    }

    git push origin "$BRANCH" || {
        log_error "Failed to push to origin"
        exit 1
    }

    # Push to mirror if it exists
    if git remote | grep -q "mirror"; then
        git push mirror "$BRANCH" || {
            log_warning "Failed to push to mirror (continuing anyway)"
        }
    fi

    log_success "Changes committed and pushed"
}

# Build packages
build_packages() {
    log_info "Building packages..."

    # Clean up first
    cleanup

    # Check if setup files exist
    if [ ! -f "setup_omnigenome.py" ]; then
        log_error "setup_omnigenome.py not found"
        exit 1
    fi

    if [ ! -f "setup_omnigenbench.py" ]; then
        log_error "setup_omnigenbench.py not found"
        exit 1
    fi

    # Build omnigenome first
    log_info "Building omnigenome package..."
    python setup_omnigenome.py sdist bdist_wheel || {
        log_error "Failed to build omnigenome package"
        exit 1
    }

    # Build omnigenbench
    log_info "Building omnigenbench package..."
    python setup_omnigenbench.py sdist bdist_wheel || {
        log_error "Failed to build omnigenbench package"
        exit 1
    }

    log_success "Packages built successfully"
}

# Upload to PyPI
upload_to_pypi() {
    log_info "Uploading packages to PyPI..."

    # Check if dist directory exists and has files
    if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
        log_error "No distribution files found in dist/"
        exit 1
    fi

    # Upload all packages
    python -m twine upload dist/* -u __token__ -p "$PYPI_TOKEN" || {
        log_error "Failed to upload packages to PyPI"
        exit 1
    }

    log_success "Packages uploaded to PyPI successfully"
}

# Main execution
main() {
    log_info "Starting release process..."

    validate_arguments
    check_prerequisites
    format_code
    check_git_status
    commit_and_push
    build_packages
    upload_to_pypi
    cleanup

    log_success "Release process completed successfully!"
    log_info "Your packages should be available on PyPI shortly."
}

# Error handling
trap 'log_error "An error occurred during the release process"; cleanup; exit 1' ERR

# Run main function
main "$@"
