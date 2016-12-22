# bluething-sensor
bluething IoT Sensor based on ESP8266

## Requirements

This code was tested with an Adafruit Feather HUZZAH and an Adafruit MCP9808
temperature sensor but any ESP8266 board should work.

* ESP8266 board
* Adafruit MCP9808
* MicroPython (tested with 1.8.6)


## Running the code

Please check the variables on top in main.py because you will likely want to
change a few of them.

You need to upload the python code to the board. Any method should work so you
can choose between ampy, WebREPL, rshell or mpfshell. I prefer the last one so:

<pre>
mpfshell
> open ttyUSB0
> put main.py
> put mcp9808.py
> exit
</pre>

Connect to the serial console to see the output.

<code>
miniterm.py /dev/ttyUSB0 115200
</code>

Reset the device to run the uploaded code.

