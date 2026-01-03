#!/bin/bash
SERVER="100.99.70.10"
USER="aylan"
REMOTE_PATH="/home/aylan/purchase-tracker"

echo "Connecting to $SERVER to repair..."
ssh -t "$USER@$SERVER" "
    set -e # Stop on error
    
    echo '--- 1. Checking System Packages ---
    if ! dpkg -s python3-venv >/dev/null 2>&1; then
         echo 'Installing python3-venv...'
         sudo apt-get update && sudo apt-get install -y python3-venv
    fi

    echo '--- 2. Resetting Virtual Environment ---
    cd $REMOTE_PATH
    
    # Nuke it to be sure
    if [ -d ".venv" ]; then
        echo 'Removing old .venv...'
        rm -rf .venv
    fi
    
    echo 'Creating fresh .venv...'
    python3 -m venv .venv
    
    echo '--- 3. Installing Dependencies ---
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
    
    echo '--- 4. Restarting Service ---
    sudo systemctl restart purchase-tracker
    
    echo '--- 5. Verification ---
    sleep 2
    if systemctl is-active --quiet purchase-tracker; then
        echo '✅ App is RUNNING.'
    else
        echo '❌ App failed to start. Logs:'
        journalctl -u purchase-tracker -n 10 --no-pager
        exit 1
    fi

    echo '--- 6. Web Server Check ---
    if [ -d /etc/nginx/sites-enabled ]; then
        echo 'Found Nginx configuration:'
        ls -F /etc/nginx/sites-enabled/
    elif [ -d /etc/apache2/sites-enabled ]; then
        echo 'Found Apache configuration:'
        ls -F /etc/apache2/sites-enabled/
    fi
"
