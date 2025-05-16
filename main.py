import win32evtlog
import smtplib
from email.mime.text import MIMEText
import time
import threading
import tkinter as tk
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import os

EMAIL_ADDRESS = "shashankpaandey@gmail.com"
EMAIL_PASSWORD = "puescgaohabunobe"
TO_EMAIL = "shashankpaandey@gmail.com"

failed_count = 0
alert_threshold = 1

# Email alert function
def send_email_alert():
    msg = MIMEText('⚠️ Warning: Someone tried multiple wrong passwords on your laptop!')
    msg['Subject'] = 'Security Alert: Unauthorized Access Detected'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("❌ Email send failed:", e)

# Monitor failed login attempts
def monitor_failed_logins():
    global failed_count
    last_checked = time.time()

    while True:
        try:
            logs = win32evtlog.OpenEventLog(None, "Security")
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(logs, flags, 0)

            for event in events:
                if event.EventID == 4625 and event.TimeGenerated.timestamp() > last_checked:
                    failed_count += 1
                    print(f"❗ Failed login detected! Count: {failed_count}")
                    if failed_count >= alert_threshold:
                        send_email_alert()
                        failed_count = 0
            last_checked = time.time()
            time.sleep(10)
        except Exception as e:
            print("❌ Error reading event log:", e)
            time.sleep(30)

# Create system tray icon image
def create_image():
    image = Image.new("RGB", (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 0, 0))
    return image

# Quit function for system tray
def on_quit(icon, item):
    icon.stop()
    os._exit(0)

# Function to run system tray
def run_tray():
    icon = pystray.Icon("SecurityMonitor")
    icon.icon = create_image()
    icon.menu = pystray.Menu(pystray.MenuItem("Quit", on_quit))
    icon.run()

# Function to start the Tkinter GUI
def start_gui():
    root = tk.Tk()
    root.title("Security Monitor")
    root.geometry("300x100")
    tk.Label(root, text="Monitoring failed logins...", font=("Arial", 10)).pack(pady=20)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.mainloop()

# Main entry point
if __name__ == "__main__":
    print("🔒 Security Monitor started...")
    threading.Thread(target=monitor_failed_logins, daemon=True).start()  # Start monitoring
    threading.Thread(target=run_tray, daemon=True).start()  # Start system tray
    start_gui()  # Start the GUI
