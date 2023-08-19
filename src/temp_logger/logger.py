import argparse
import datetime
import sqlite3

import serial

parser = argparse.ArgumentParser(
    prog="Temperature Logger",
    description="Logs temperature reported by Arduino through a serial port and stores the records in an SQLite database",
)

parser.add_argument("serial", help="Path to the device representing the serial port e.g. /dev/ttyACM0", type=str)
parser.add_argument("db", help="Path to the SQLite DB for storing the results", type=str)


def main():
    args = parser.parse_args()
    db_con = sqlite3.connect(args.db)
    db_cursor = db_con.cursor()
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS temperatures (
            timestamp REAL NOT NULL,
            temperature REAL NOT NULL)
        """
    )
    arduino_output = serial.Serial(args.serial, 9600, timeout=11)

    while True:
        temperature_line = arduino_output.readline().decode()
        if not temperature_line.startswith("TMP"):
            continue
        temperature = float(temperature_line.split(":")[1].strip())
        time_current = datetime.datetime.now()
        db_cursor.execute("INSERT INTO temperatures VALUES (?, ?)", (time_current.timestamp(), temperature))
        db_con.commit()
        print(time_current, temperature)


if __name__ == "__main__":
    main()
