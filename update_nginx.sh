#!/bin/bash

# Configuration
SERVER="100.99.70.10"
USER="aylan"
LOCAL_CONFIG="nginx_config.tmp"

echo "=========================================="
echo "🌐 Updating Nginx Configuration on $SERVER"
echo "=========================================="

echo "1. Uploading config file..."
scp "$LOCAL_CONFIG" "$USER@$SERVER:/tmp/nginx_default"

echo "2. Applying config..."
ssh -t "$USER@$SERVER" "
    echo 'Backing up current config...'
    sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak_$(date +%s)
    
    echo 'Overwriting default config...'
    sudo mv /tmp/nginx_default /etc/nginx/sites-available/default
    
    echo 'Testing configuration...'
    if sudo nginx -t; then
        echo '✅ Configuration looks good. Reloading Nginx...'
        sudo systemctl reload nginx
        echo '🎉 Nginx updated successfully!'
    else
        echo '❌ Configuration test failed! Restoring backup...'
        sudo mv /etc/nginx/sites-available/default.bak_* /etc/nginx/sites-available/default
        sudo systemctl reload nginx
        exit 1
    fi
"
