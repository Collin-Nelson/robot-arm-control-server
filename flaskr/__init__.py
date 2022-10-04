from flask import Flask, render_template, request, flash, redirect
from markupsafe import escape
from flaskr.serial_communication import serial_communication
import threading, time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cde4c167e10fc229668c7d560761654530639db4fbf18997'

recent_commands = []    # Make an array to store sent commands
serial = serial_communication()    # Initialize an instance of the serial_communication class to start serial communication

def serial_loop():    # Loop to check for serial communication from the arm periodically
    while(True):
        serial.serial_check()
        time.sleep(1)

serial_thread = threading.Thread(target=serial_loop)    # Initialize the serial loop thread
serial_thread.start()    # Start the serial loop thread

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':     # If loading page
        recent_commands.clear()
        recent_commands.append("No Recent Commands")    # Set the first command to be "No Recent Commands"
    elif request.method == 'POST':    # If form submitted
        if recent_commands[0] == "No Recent Commands":    # If no commands yet, prepare to add a command
            recent_commands[0] = ""
        last_command = escape(request.form['command'])  # Get the command from the form
        recent_commands.insert(0, last_command)     # Add the command to the list of recent commands
        serial.serial_write(last_command)    # Pass command to serial_communication class to deal with
    return render_template('index.html', recent_commands = recent_commands)

@app.route('/function', methods=['POST'])
def test():
    if recent_commands[0] == "No Recent Commands":
        recent_commands[0] = ""
    last_command = escape(request.form['function_id'])  # Get the command from the form
    recent_commands.insert(0, last_command)     # Add the command to the list of recent commands
    serial.serial_write(last_command)    # Pass command to serial_communication class to deal with
    return render_template('index.html', recent_commands = recent_commands)


