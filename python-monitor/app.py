from flask import Flask, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading
import asyncio
import time
from bleak import BleakScanner
import queue

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devices.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default="Unknown")
    address = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default="Disconnected")
    last_seen = db.Column(db.String(50), default="N/A")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "status": self.status,
            "last_seen": self.last_seen,
        }

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(120))
    address = db.Column(db.String(50))
    status = db.Column(db.String(20))
    timestamp = db.Column(db.String(50))

event_queue = queue.Queue()

def record_event_threadsafe(name, address, status):
    event_queue.put((name, address, status))

def db_worker():
    """Handles database writes safely in one thread"""
    with app.app_context():
        while True:
            try:
                name, address, status = event_queue.get()
                event = History(
                    device_name=name,
                    address=address,
                    status=status,
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                db.session.add(event)
                db.session.commit()
            except Exception as e:
                print("Database write error:", e)
                db.session.rollback()
            finally:
                event_queue.task_done()
            time.sleep(0.05)

async def scan_devices():
    devices = await BleakScanner.discover()
    with app.app_context():
        known = {d.address: d for d in Device.query.all()}
        found_addresses = []

        for d in devices:
            name = d.name or "Unknown Device"
            addr = d.address
            found_addresses.append(addr)

            if addr not in known:
                new = Device(name=name, address=addr, status="Connected",
                             last_seen=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                db.session.add(new)
                record_event_threadsafe(name, addr, "Connected")
            else:
                dev = known[addr]
                dev.name = name
                dev.status = "Connected"
                dev.last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                record_event_threadsafe(name, addr, "Reconnected")
        db.session.commit()

        for addr, dev in known.items():
            if addr not in found_addresses:
                dev.status = "Disconnected"
                record_event_threadsafe(dev.name, addr, "Disconnected")
        db.session.commit()

def start_scanner():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            loop.run_until_complete(scan_devices())
        except Exception as e:
            print("Scan error:", e)
        time.sleep(10)

@app.route("/")
def index():
    devices = Device.query.all()
    return render_template_string(INDEX_TEMPLATE, devices=devices)

@app.route("/history")
def history():
    records = History.query.order_by(History.id.desc()).limit(100).all()
    return render_template_string(HISTORY_TEMPLATE, records=records)

@app.route("/api/devices")
def api_devices():
    return jsonify([d.to_dict() for d in Device.query.all()])

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TruTooth Monitor</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; background-color: white; color: black; }
    h1 { font-size: 26px; margin-bottom: 10px; }
    a { color: #0000EE; text-decoration: none; }
    a:hover { text-decoration: underline; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h1>TruTooth Device Monitor</h1>
  <p><a href="/history">View Connection History</a></p>
  <table>
    <thead>
      <tr><th>Name</th><th>Address</th><th>Status</th><th>Last Seen</th></tr>
    </thead>
    <tbody>
    {% for d in devices %}
      <tr>
        <td>{{ d.name }}</td>
        <td>{{ d.address }}</td>
        <td>{{ d.status }}</td>
        <td>{{ d.last_seen }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

HISTORY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Connection History</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; background-color: white; color: black; }
    h1 { font-size: 26px; margin-bottom: 10px; }
    a { color: #0000EE; text-decoration: none; }
    a:hover { text-decoration: underline; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h1>Connection History</h1>
  <p><a href="/">Back to Device List</a></p>
  <table>
    <thead><tr><th>Timestamp</th><th>Device</th><th>Address</th><th>Status</th></tr></thead>
    <tbody>
    {% for r in records %}
      <tr>
        <td>{{ r.timestamp }}</td>
        <td>{{ r.device_name }}</td>
        <td>{{ r.address }}</td>
        <td>{{ r.status }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

if __name__ == "__main__":
    print("Starting TruTooth Flask Bluetooth Monitor...")
    with app.app_context():
        db.create_all()
    threading.Thread(target=db_worker, daemon=True).start()
    threading.Thread(target=start_scanner, daemon=True).start()
    app.run(debug=True)
