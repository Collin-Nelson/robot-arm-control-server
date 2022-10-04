import serial, queue

class serial_communication:
    def __init__(self):
        
        self.queue = queue.Queue()
        self.arm_waiting = True    # True if the microcontroller is currently waiting for a command from the RPi
        
        self.device_id = "/dev/serial/by-id/usb-Teensyduino_USB_Serial_11031620-if00"
        self.baudrate = 57600
        self.initialize_serial(self.device_id)
        
    def initialize_serial(self, device_id):
        self.device_id = device_id
        try:
            print("Initializing serial communication with: " + self.device_id)
            self.ser = serial.Serial(self.device_id, self.baudrate, timeout=1)
        except:
            print("Could not initialize serial communication with: " + self.device_id)
    
    # Write a command over USB serial to the microcontroller that is controlling the arm's stepper motors
    def serial_write(self, string):
        string = str(string)
        string = string.strip(' ')
        if self.arm_waiting:    # If the arm is waiting for a command, send the command, if not, add it to the queue
            my_str = string + "\n"    # Add a newline character to the end
            my_str = my_str.encode('utf-8')    # Encode in bytes
            self.ser.write(my_str)
            self.arm_waiting = False    # change waiting flag to flase to signify the arm is no longer waiting for us to send a command
            print("Command '" + string + "' sent")
        else:              # If the arm is not waiting for a command (i.e. if it is running a current command)
            self.queue.put(string)    # Add the command to a queue
            print("Command '" + string + "' added to queue")
    
    # Keep reading from serial until a response is recieved
    def serial_check(self):
        if self.ser.inWaiting() != 0:    # If there are bytes waiting to be read in, call serial_read()
            self.serial_read()
        if self.arm_waiting and not self.queue.empty():    # If the arm is waiting for a command and the queue is not empty, send a command (Should never happen)
            my_str = self.queue.get()
            self.serial_write(my_str)
            print("I should never get printed")
    
    # Read in a line from the microcontroller and respond appropriately
    def serial_read(self):
        line = self.ser.readline()
        line = line.decode("utf-8")
        line = line.strip()
        print("Line '" + line + "' was read from serial")
        
        if line == "Ready":    # If the line received from the microcontroller is "Ready", send the next command or update the waaiting flag if the queue is empty
            self.arm_waiting = True
            if not self.queue.empty():
                my_str = self.queue.get()
                self.serial_write(my_str)
                
        elif line == "Unknown":    # Deal with invalid commands or other commands that the microcontroller doesn't recognize
            print("Last command not recognized")
            
        elif line == "Cannot Execute":    # Deal with commands that were recognized, but could not be executed
            print("Last command was recognized, but could not be executed")
        
        # Add remaining commands or add a function call to deal with other commands
        # Add a line or function call to handle ack (acknowledgement) packets from the arm
        
        else:
            print("Last line from arm '" + line + "' was not recognized")