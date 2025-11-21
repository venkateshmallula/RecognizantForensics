#!/bin/bash

# Quick script to pull latest code and redeploy to Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Updating Recognizant Forensics Deployment${NC}"
echo ""

# Check if we're in a git repository
if [ -d .git ]; then
    echo -e "${YELLOW}📥 Pulling latest code from Git...${NC}"
    
    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}⚠️  You have uncommitted changes.${NC}"
        read -p "Stash changes and pull? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash
            git pull
            git stash pop
        else
            echo -e "${RED}❌ Aborted. Commit or stash your changes first.${NC}"
            exit 1
        fi
    else
        git pull
    fi
    
    echo -e "${GREEN}✓ Code updated${NC}"
    echo ""
else
    echo -e "${YELLOW}ℹ️  Not a git repository. Skipping git pull.${NC}"
    echo ""
fi

# Check if deploy.sh exists
if [ -f "./deploy.sh" ]; then
    echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
    echo ""
    ./deploy.sh
else
    echo -e "${RED}❌ deploy.sh not found.${NC}"
    echo "   Run deployment manually or ensure you're in the project directory."
    exit 1
fi

