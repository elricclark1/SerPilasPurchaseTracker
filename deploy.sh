#!/bin/bash

# Configuration
SERVER="100.99.70.10"
USER="aylan"
REMOTE_PATH="/home/aylan/purchase-tracker"

echo "=========================================="
echo "🚀 Deploying Purchase Tracker to $SERVER"
echo "=========================================="

# 1. Sync Files (using tar file + scp to avoid pipe auth issues)
echo ""
echo "📦 Step 1: Syncing code..."

# Create local tarball
tar --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='.streamlit' \
    --exclude='*.sh' \
    -czf deploy_pkg.tar.gz .

# Upload tarball
scp deploy_pkg.tar.gz "$USER@$SERVER:$REMOTE_PATH/"

# Extract and cleanup remote
ssh -t "$USER@$SERVER" "cd $REMOTE_PATH && tar -xzf deploy_pkg.tar.gz && rm deploy_pkg.tar.gz"

# Cleanup local
rm deploy_pkg.tar.gz

# 2. Restart Application
echo ""
echo "🔄 Step 2: Restarting App Service..."
ssh -t "$USER@$SERVER" "sudo systemctl restart purchase-tracker && systemctl status purchase-tracker --no-pager"

echo ""
echo "✅ Deployment Complete! Visit: http://serpilas.com/PurchaseTracker/"