import threading
import time
from pynput import keyboard
from collections import deque

# A thread-safe queue (using collections.deque) to hold the pressed key codes
keys_buffer = deque()
exit_program_flag = threading.Event()


def _on_key_press(key):
    """
    Callback function executed when a key is pressed.
    Runs in the listener thread.
    """
    try:
        key_code = key.vk if hasattr(key, "vk") else key.char
        keys_buffer.append(key_code)
    except AttributeError:
        # Special keys (e.g., shift, ctrl, alt) don't have a .char attribute
        keys_buffer.append(str(key))

    # Check if the user wants to stop the program
    if key == keyboard.Key.esc:
        exit_program_flag.set()  # Set the event to signal the main thread to stop
        return False  # stop the listener thread


def _keyboard_listen():
    """
    Function for the keyboard listener thread.
    """
    print("✨ Key listener thread started. Press 'Esc' to stop the program.")
    with keyboard.Listener(on_press=_on_key_press) as listener:
        listener.join()
    print("❌ Key listener thread finished.")


def _display_pressed_keys():
    """
    Function for the display thread (main logic).
    """
    print("🖥️ Display thread started. Waiting for key presses...")

    while not exit_program_flag.is_set():
        # Check if there are keys in the buffer
        if keys_buffer:
            # Get the oldest key from the buffer
            key_code = keys_buffer.popleft()
            print(f"Key Pressed Code: {key_code}")

        # Short sleep to prevent the display thread from hogging the CPU
        time.sleep(0.01)

    print("🛑 Display thread finished.")


if __name__ == "__main__":
    # 1. Start the Listener Thread
    listener_t = threading.Thread(target=_keyboard_listen)
    listener_t.start()

    # 2. Start the Display Thread (this is also our main thread in this setup)
    # We could also create a dedicated display thread, but for simplicity,
    # we'll use a function for the logic in the main thread.

    # For a *truly* separate second thread, we'll launch a dedicated display_t:
    display_t = threading.Thread(target=_display_pressed_keys)
    display_t.start()

    # Wait for both threads to finish (which happens when 'Esc' is pressed)
    display_t.join()
    listener_t.join()
