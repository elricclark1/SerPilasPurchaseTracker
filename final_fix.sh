#!/bin/bash
SERVER="100.99.70.10"
USER="aylan"
REMOTE_PATH="/home/aylan/purchase-tracker"

echo "=========================================="
echo "🛠️  Final Repair & Config Script"
echo "=========================================="

echo "Connecting to $SERVER..."
ssh -t "$USER@$SERVER" "
    # 1. FIX APP DEPENDENCIES
    echo '--- 📦 Re-installing App Dependencies ---"'
    cd $REMOTE_PATH || exit
    
    # Ensure venv exists
    if [ ! -d .venv ]; then
        python3 -m venv .venv
    fi
    
    # Force install streamlit explicitly
    .venv/bin/pip install streamlit pandas plotly watchdog
    
    # 2. RESTART APP
    echo '--- 🚀 Restarting App Service ---"'
    sudo systemctl restart purchase-tracker
    sleep 3
    
    if systemctl is-active --quiet purchase-tracker; then
        echo '✅ App is NOW RUNNING!'
    else
        echo '❌ App still failing. Logs:'
        journalctl -u purchase-tracker -n 5 --no-pager
        exit 1
    fi

    # 3. CONFIGURE NGINX
    echo '--- 🌐 Configuring Nginx for /PurchaseTracker ---"'
    
    # Define the config block
    CONFIG='
    location /PurchaseTracker {
        proxy_pass http://127.0.0.1:8501/;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    '
    
    # Check if already configured
    if grep -q 'location /PurchaseTracker' /etc/nginx/sites-available/default; then
        echo 'Nginx already configured.'
    else
        echo 'Adding config to /etc/nginx/sites-available/default...'
        # Backup first
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup_$(date +%s)
        
        # Insert before the last closing brace '}' of the server block
        # Assuming the standard default file structure
        sudo sed -i 's|try_files $uri $uri/ =404;|try_files $uri $uri/ =404;\n    }\n\n    location /PurchaseTracker/ {\n        proxy_pass http://127.0.0.1:8501/;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;|' /etc/nginx/sites-available/default
        
        # Test and Reload
        echo 'Testing Nginx config...'
        if sudo nginx -t; then
            echo 'Reloading Nginx...'
            sudo systemctl reload nginx
            echo '✅ Nginx Updated. Visit serpilas.com/PurchaseTracker/'
        else
            echo '❌ Nginx Config Invalid! Reverting...'
            sudo cp /etc/nginx/sites-available/default.backup_* /etc/nginx/sites-available/default
        fi
    fi
"
