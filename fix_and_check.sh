#!/bin/bash
SERVER="100.99.70.10"
USER="aylan"
REMOTE_PATH="/home/aylan/purchase-tracker"

echo "Connecting to $SERVER..."
ssh -t "$USER@$SERVER" "
    # 1. Ensure Directory Exists
    mkdir -p $REMOTE_PATH
    cd $REMOTE_PATH || exit

    # 2. Create Virtual Environment if missing
    if [ ! -f ".venv/bin/python" ]; then
        echo 'Creating virtual environment...'
        # Ensure venv module is installed
        if ! dpkg -s python3-venv >/dev/null 2>&1; then
             echo 'Installing python3-venv...'
             sudo apt-get update && sudo apt-get install -y python3-venv
        fi
        python3 -m venv .venv
    fi

    # 3. Install Dependencies
    echo 'Installing dependencies...'
    .venv/bin/pip install -r requirements.txt

    # 4. Restart Service
    echo 'Restarting Service...'
    sudo systemctl restart purchase-tracker
    
    # 5. Check Service Status
    if systemctl is-active --quiet purchase-tracker; then
        echo '✅ Service is RUNNING.'
    else
        echo '❌ Service failed to start.'
        journalctl -u purchase-tracker -n 5 --no-pager
    fi

    # 6. Check Web Server Config
    echo '--- Web Server Discovery ---
    if [ -d /etc/nginx/sites-enabled ]; then
        echo 'Found Nginx sites:'
        ls -l /etc/nginx/sites-enabled/
        # Try to find config for serpilas.com
        grep -r 'serpilas.com' /etc/nginx/sites-enabled/ || echo 'serpilas.com not explicitly found in nginx sites'
    elif [ -d /etc/apache2/sites-enabled ]; then
        echo 'Found Apache sites:'
        ls -l /etc/apache2/sites-enabled/
    else
        echo 'Could not auto-detect web server sites folder.'
    fi
"
