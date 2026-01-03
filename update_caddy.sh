#!/bin/bash

# Configuration
SERVER="100.99.70.10"
USER="aylan"
LOCAL_CADDYFILE="Caddyfile.tmp"

echo "=========================================="
echo "🌐 Updating Caddy Configuration on $SERVER"
echo "=========================================="

echo "1. Uploading Caddyfile..."
scp "$LOCAL_CADDYFILE" "$USER@$SERVER:/tmp/Caddyfile"

echo "2. Applying config..."
ssh -t "$USER@$SERVER" "
    echo 'Backing up current Caddyfile...'
    sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.bak_$(date +%s)
    
    echo 'Overwriting Caddyfile...'
    sudo mv /tmp/Caddyfile /etc/caddy/Caddyfile
    
    echo 'Reloading Caddy...'
    if sudo systemctl reload caddy; then
        echo '🎉 Caddy reloaded successfully!'
    else
        echo '❌ Caddy reload failed! Checking status...'
        sudo systemctl status caddy --no-pager
        exit 1
    fi
"
