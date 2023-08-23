# TempLogger

TempLogger reads temperature from a sensor attached to an Arduino board. It writes it into
an SQLite database. Temperature history can be viewed in a simple web application.

## How to use

### Setting up Arduino

Compile and upload the code from `./src/temperature.ino` to your Arduino board in Arduino IDE.
The code is designed to work with the TMP36 temperature sensor and input voltage of 5V. The sensor
output should be attached to the `A0` pin. Arduino writes the temperature to the serial port.

### Python environment

In this project I use [Rye](https://rye-up.com/) package manager. After installing it you can run

```shell
$ rye sync
```

to create a virtual environment for the project.

### Logger

Logger is responsible for reading the temperature from a serial port and storing it in a database.
You can start it like this:

```shell
$ rye run src/temp_logger/logger.py {path-to-serial-port} {path-to-database}
```

On Ubuntu 22.04 and Fedora 38, the serial port path was `/dev/ttyACM0`. Make sure that you
can read data from this device. On both Ubuntu and Fedora I achieved this by adding the user
to the `dialup` group.

### Web interface

You can start the web interface like this:

```shell
$ rye run src/temp_logger/web.py
```

This will start the web interface showing a temperature graph at port 5000. 
I use [Quart](https://palletsprojects.com/p/quart/) - an async version of Flask to implement the
web interface.