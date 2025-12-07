#!/usr/bin/env python3
"""
P2C2R Web GUI - The Uber of Game Compute
Modern web-based interface using Flask
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os
import signal
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Global state
network_state = {
    'running': False,
    'process': None,
    'start_time': None,
    'stats': {
        'coordinator': {'status': 'offline', 'port': 8765},
        'peers': 0,
        'users': 0,
        'tasks': {'total': 0, 'completed': 0, 'failed': 0},
        'uptime': 0,
    },
    'activity_log': []
}


def log_activity(message, level='info'):
    """Add activity to log"""
    entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'level': level
    }
    network_state['activity_log'].insert(0, entry)
    # Keep only last 100 entries
    network_state['activity_log'] = network_state['activity_log'][:100]


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current network status"""
    if network_state['running'] and network_state['start_time']:
        uptime = (datetime.now() - network_state['start_time']).total_seconds()
        network_state['stats']['uptime'] = int(uptime)
    
    return jsonify({
        'running': network_state['running'],
        'stats': network_state['stats'],
        'activity_log': network_state['activity_log'][:20]  # Last 20 entries
    })


@app.route('/api/start', methods=['POST'])
def start_network():
    """Start the P2C2R network"""
    if network_state['running']:
        return jsonify({'success': False, 'error': 'Network already running'})
    
    script_path = Path(__file__).parent / 'run_network.sh'
    
    if not script_path.exists():
        log_activity(f'✗ run_network.sh not found', 'error')
        return jsonify({'success': False, 'error': 'run_network.sh not found'})
    
    try:
        log_activity('Starting P2C2R network...', 'info')
        
        # Start the network
        process = subprocess.Popen(
            [str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_path.parent),
            preexec_fn=os.setsid  # Create new process group
        )
        
        network_state['running'] = True
        network_state['process'] = process
        network_state['start_time'] = datetime.now()
        
        # Update stats
        network_state['stats']['coordinator']['status'] = 'online'
        network_state['stats']['peers'] = 3
        network_state['stats']['users'] = 1
        
        log_activity('✓ Network started successfully', 'success')
        log_activity('Coordinator running on localhost:8765', 'info')
        
        return jsonify({'success': True})
        
    except Exception as e:
        log_activity(f'✗ Failed to start network: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/stop', methods=['POST'])
def stop_network():
    """Stop the P2C2R network"""
    if not network_state['running']:
        return jsonify({'success': False, 'error': 'Network not running'})
    
    try:
        log_activity('Stopping P2C2R network...', 'info')
        
        if network_state['process']:
            # Kill the entire process group
            os.killpg(os.getpgid(network_state['process'].pid), signal.SIGTERM)
            network_state['process'].wait(timeout=5)
            log_activity('✓ Network stopped', 'success')
        
        network_state['running'] = False
        network_state['process'] = None
        network_state['start_time'] = None
        
        # Reset stats
        network_state['stats']['coordinator']['status'] = 'offline'
        network_state['stats']['peers'] = 0
        network_state['stats']['users'] = 0
        network_state['stats']['uptime'] = 0
        
        return jsonify({'success': True})
        
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(network_state['process'].pid), signal.SIGKILL)
        log_activity('✓ Network force stopped', 'warning')
        return jsonify({'success': True})
    except Exception as e:
        log_activity(f'✗ Error stopping network: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/restart', methods=['POST'])
def restart_network():
    """Restart the network"""
    log_activity('Restarting network...', 'info')
    stop_result = stop_network()
    if not stop_result.json['success']:
        return stop_result
    
    # Wait a bit before restarting
    import time
    time.sleep(2)
    
    return start_network()


if __name__ == '__main__':
    log_activity('P2C2R Control Center initialized', 'info')
    log_activity('Open http://localhost:5000 in your browser', 'success')
    
    print("\n" + "="*60)
    print("🚀 P2C2R Control Center")
    print("="*60)
    print("\n📡 Server starting...")
    print("🌐 Open in browser: http://localhost:5001")
    print("\n💡 Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
