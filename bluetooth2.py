from base64 import decode
import tkinter as tk
import serial
import time
import threading


# Initialize the serial connection
def init_serial_connection(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Allow time for connection setup
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None


# Function to send data to the HC-06 module
def send_signal(signal):
    if serial_connection and serial_connection.is_open:
        serial_connection.write(signal.encode())
        print(f"Sent: {signal}")
    else:
        print("Serial connection not established.")


# Function to read temperature from serial
def read_temperature():
    global room_temperature
    temperature_data = ""  # Accumulator for temperature characters
    while serial_connection and serial_connection.is_open:
        try:
            data = serial_connection.read().decode("utf-8")
            temperature_data += data
            if len(temperature_data) == 2:
                room_temperature.set(f"~{temperature_data} °C")
                temperature_data = ""  # Reset accumulator for the next reading
        except Exception as e:
            print(f"Error reading temperature: {e}")
        time.sleep(0.1)


# Keyboard event handlers
def key_press(event):
    key = event.keysym.lower()
    if key == "up" and not button_states["up"]:
        send_signal("w")
        button_states["up"] = True
        change_button_state("up", True)
    elif key == "down" and not button_states["down"]:
        send_signal("s")
        button_states["down"] = True
        change_button_state("down", True)
    elif key == "right" and not button_states["right"]:
        send_signal("d")
        button_states["right"] = True
        change_button_state("right", True)
    elif key == "left" and not button_states["left"]:
        send_signal("a")
        button_states["left"] = True
        change_button_state("left", True)


def key_release(event):
    key = event.keysym.lower()
    if key in button_states and button_states[key]:
        send_signal("]")  # Send stop signal
        button_states[key] = False
        change_button_state(key, False)


# Change button state for visual feedback
def change_button_state(direction, pressed):
    if direction in buttons:
        button = buttons[direction]
        if pressed:
            button.config(bg="lightblue")  # Highlight color
        else:
            button.config(bg="SystemButtonFace")  # Default color


# Create GUI
def create_gui():
    root = tk.Tk()
    root.title("Car Controller")
    root.geometry("400x500")  # Adjusted size to fit temperature display
    root.resizable(False, False)  # Make the window not resizable

    # Instructions Label
    label = tk.Label(root, text="Control the car using arrow keys.", font=("Arial", 14))
    label.pack(pady=10)

    # Buttons Frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # Add arrow buttons
    global buttons
    buttons = {}
    global button_states
    button_states = {"up": False, "down": False, "left": False, "right": False}

    # Arrow buttons
    buttons["up"] = tk.Button(
        button_frame, text="↑", font=("Arial", 16), width=5, height=2
    )
    buttons["up"].grid(row=0, column=1, pady=(0, 10))

    buttons["left"] = tk.Button(
        button_frame, text="←", font=("Arial", 16), width=5, height=2
    )
    buttons["left"].grid(row=1, column=0)

    buttons["down"] = tk.Button(
        button_frame, text="↓", font=("Arial", 16), width=5, height=2
    )
    buttons["down"].grid(row=1, column=1)

    buttons["right"] = tk.Button(
        button_frame, text="→", font=("Arial", 16), width=5, height=2
    )
    buttons["right"].grid(row=1, column=2)

    # Temperature Label
    global room_temperature
    room_temperature = tk.StringVar()
    room_temperature.set("~-- °C")
    temp_label = tk.Label(
        root, textvariable=room_temperature, font=("Arial", 16), fg="green"
    )
    temp_label.pack(pady=20)

    # Bind key events
    root.bind("<KeyPress>", key_press)
    root.bind("<KeyRelease>", key_release)

    root.mainloop()


# Main program
if __name__ == "__main__":
    # Use the COM port where your HC-06 is connected
    SERIAL_PORT = "COM5"
    BAUD_RATE = 9600

    serial_connection = init_serial_connection(SERIAL_PORT, BAUD_RATE)

    if serial_connection:
        print("Serial connection established.")
        # Start temperature reading in a separate thread
        threading.Thread(target=read_temperature, daemon=True).start()
        create_gui()
    else:
        print("Failed to establish serial connection.")
