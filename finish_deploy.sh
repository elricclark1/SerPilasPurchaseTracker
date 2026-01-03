#!/bin/bash

# Configuration
SERVER="100.99.70.10"
USER="aylan"
REMOTE_PATH="/home/aylan/purchase-tracker"

echo "=========================================="
echo "🔧 Finishing Deployment on $SERVER"
echo "=========================================="

echo "Connecting to server..."
ssh -t "$USER@$SERVER" "
    cd $REMOTE_PATH || exit

    # 1. Install Dependencies (using explicit venv pip to avoid system error)
    echo '📦 Installing dependencies...'
    .venv/bin/pip install -r requirements.txt

    # 2. Create Systemd Service
    echo '⚙️  Creating Systemd Service...'
    
    # Create service file in /tmp first
    cat > /tmp/purchase-tracker.service <<EOF
[Unit]
Description=Streamlit Purchase Tracker
After=network.target

[Service]
User=$USER
WorkingDirectory=$REMOTE_PATH
ExecStart=$REMOTE_PATH/.venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.baseUrlPath /PurchaseTracker
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Move to system location (requires sudo)
    echo 'Moving service file (sudo)...'
    sudo mv /tmp/purchase-tracker.service /etc/systemd/system/purchase-tracker.service
    
    # Reload and Start
    echo '🚀 Starting Service...'
    sudo systemctl daemon-reload
    sudo systemctl enable purchase-tracker
    sudo systemctl restart purchase-tracker
    
    # Check Status
    sleep 2
    if systemctl is-active --quiet purchase-tracker; then
        echo '✅ App is RUNNING (active)'
    else
        echo '❌ App failed to start. Checking logs:'
        journalctl -u purchase-tracker -n 10 --no-pager
    fi
"
