# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, redirect, url_for
import database
import scanner

app = Flask(__name__)

import time

@app.route('/')
def dashboard():
    # Check if a force refresh is requested via query param
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'

    # 1. Fetch current live devices on the network layout channel
    live_devices = scanner.scan_network(force_refresh=force_refresh)
    
    # 2. Get the list of all trusted MAC mappings from the SQLite DB
    trusted_map = database.get_all_trusted_macs()
    
    processed_devices = []
    intruder_detected = False
    
    # 3. Analyze every live device found
    for dev in live_devices:
        mac = dev['mac']
        is_trusted = mac in trusted_map
        
        # If even one live device is missing from the database, sound the visual alarm
        if not is_trusted:
            intruder_detected = True
            
        processed_devices.append({
            'ip': dev['ip'],
            'mac': mac,
            'is_trusted': is_trusted,
            'name': trusted_map.get(mac, "Unknown System Device Address")
        })
        
    # Calculate stats
    total_devices = len(processed_devices)
    trusted_count = sum(1 for d in processed_devices if d['is_trusted'])
    unknown_count = total_devices - trusted_count
    
    # Get metadata
    subnet_range = scanner.get_local_ip_range()
    local_ip = scanner.get_local_ip() or "127.0.0.1"
    
    # Formatting last scan time
    last_scan_timestamp = scanner.get_last_scan_time()
    if last_scan_timestamp == 0.0:
        last_scan_time_str = "Never scanned"
    else:
        elapsed = int(time.time() - last_scan_timestamp)
        if elapsed < 5:
            last_scan_time_str = "Just now"
        elif elapsed < 60:
            last_scan_time_str = f"{elapsed}s ago"
        else:
            last_scan_time_str = f"{elapsed // 60}m {elapsed % 60}s ago"
        
    return render_template(
        'dashboard.html', 
        devices=processed_devices, 
        intruder_detected=intruder_detected,
        total_devices=total_devices,
        trusted_count=trusted_count,
        unknown_count=unknown_count,
        subnet_range=subnet_range,
        local_ip=local_ip,
        last_scan_time_str=last_scan_time_str
    )

@app.route('/trust', methods=['POST'])
def trust_device():
    mac = request.form.get('mac')
    name = request.form.get('name')
    if mac and name:
        database.add_trusted_device(mac, name)
    return redirect(url_for('dashboard'))

@app.route('/untrust', methods=['POST'])
def untrust_device():
    mac = request.form.get('mac')
    if mac:
        database.remove_trusted_device(mac)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Start local development server profile
    app.run(debug=True, host='127.0.0.1', port=5000)
