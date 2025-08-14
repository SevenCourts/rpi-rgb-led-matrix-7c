import time
import subprocess
import os
import signal
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration ---
BATCH_FILE = "m1_emulator.bat"
DIRECTORY_TO_WATCH = "d:/dev/7c/git.github.com/rpi-rgb-led-matrix-7c"

# Global variable to hold the subprocess object
batch_process = None

def start_batch_file():
    """Starts the batch file and stores the process object."""
    global batch_process
    print(f"✅ Starting the batch file: {BATCH_FILE}")
    try:
        # Use subprocess.Popen to run the batch file in a new process
        # and store the process object.
        batch_process = subprocess.Popen(BATCH_FILE, creationflags=subprocess.CREATE_NEW_CONSOLE)
        print(f"➡️ Batch file started with PID: {batch_process.pid}")
    except FileNotFoundError:
        print(f"❌ Error: The batch file '{BATCH_FILE}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred while trying to start the batch file: {e}")
        sys.exit(1)

def stop_batch_file():
    """Stops the currently running batch file process."""
    global batch_process
    if batch_process and batch_process.poll() is None:
        print(f"🛑 Stopping the running batch file (PID: {batch_process.pid})")
        # Forcibly terminate the process and its children on Windows
        os.kill(batch_process.pid, signal.SIGTERM)
        # You may need a different method for other OS.
        batch_process.wait()  # Wait for the process to terminate
        print("✅ Batch file stopped.")
    else:
        print("➡️ No batch file process is currently running.")

def restart_batch_file():
    """Stops and then restarts the batch file."""
    stop_batch_file()
    start_batch_file()

# --- Event Handler Class ---
class MyHandler(FileSystemEventHandler):
    """
    A custom event handler that restarts the batch file on any file change.
    """
    def on_any_event(self, event):
        """
        Triggered for any file system event (created, modified, deleted).
        """
        # Exclude directory events to prevent multiple restarts for a single change
        if not event.is_directory:
            print(f"\n📁 Change detected in '{event.src_path}'.")
            restart_batch_file()

# --- Main Execution Loop ---
if __name__ == "__main__":
    # Start the batch file initially
    start_batch_file()
    
    # Set up and start the file system observer
    print(f"\n👀 Starting to monitor directory: {DIRECTORY_TO_WATCH}")
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DIRECTORY_TO_WATCH, recursive=False)
    observer.start()

    try:
        # Keep the main thread alive while the observer runs in the background
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Script stopped by user.")
    finally:
        observer.stop()
        observer.join()
        stop_batch_file()
        print("✅ Script finished.")