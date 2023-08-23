import base64
import sqlite3
from datetime import date, timedelta, datetime
from io import BytesIO

import matplotlib.pyplot as plt
from more_itertools import batched
from quart import Quart, render_template_string, request

db_con = sqlite3.connect("temperatures.db")
app = Quart(__name__)


TEMPLATE = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>TempLogger</title>
        </head>
        <body>
            <center>
            
            Last reading<br>
            <big>{{last_temperature[1]}}&deg;C</big><br>
            <small>{{last_temperature[0]}}</small><br>
            
            <p>
                <form method="get">
                    From: <input type="date" name="from-date" value="{{from_date}}">
                    To: <input type="date" name="to-date" value={{to_date}}>
                    <input type="submit" value="Select">
                </form>
            </p>
            
            <img src=data:image/png;base64,{{plot}}>
            </center>
        </body>
    </html>
"""


def get_temperatures(cursor, from_date: date, to_date: date) -> list[tuple]:
    from_timestamp = datetime(year=from_date.year, month=from_date.month, day=from_date.day).timestamp()
    to_timestamp = datetime(year=to_date.year, month=to_date.month, day=to_date.day, hour=23, minute=59).timestamp()
    cursor.execute(
        "SELECT * FROM temperatures WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp ASC",
        (from_timestamp, to_timestamp),
    )
    temperature_records = [(datetime.fromtimestamp(r[0]), r[1]) for r in cursor]
    return temperature_records


def get_last_temperature(cursor) -> tuple:
    cursor.execute("SELECT * FROM temperatures ORDER BY timestamp DESC LIMIT 1")
    last_temperature = cursor.fetchone()
    app.logger.info(last_temperature)
    return datetime.fromtimestamp(last_temperature[0]), last_temperature[1]


@app.get("/")
async def chart():
    db_cursor = db_con.cursor()
    from_date = request.args.get("from-date", date.today() - timedelta(days=1))
    from_date = datetime.strptime(from_date, "%Y-%m-%d").date() if type(from_date) == str else from_date
    to_date = request.args.get("to-date", date.today())
    to_date = datetime.strptime(to_date, "%Y-%m-%d").date() if type(to_date) == str else to_date
    temperature_records = get_temperatures(db_cursor, from_date, to_date)
    last_temperature = get_last_temperature(db_cursor)
    plt.figure(figsize=(15, 5))
    plt.title("Temperature history")
    plt.grid()
    plt.xlabel("Time")
    plt.ylabel("Temperature")
    plt.plot([r[0] for r in temperature_records], [r[1] for r in temperature_records], color="tab:blue")
    batches = batched(temperature_records, 12)
    temperature_averages = [(b[-1][0], sum([r[1] for r in b]) / len(b)) for b in batches]
    plt.plot([r[0] for r in temperature_averages], [r[1] for r in temperature_averages], color="tab:green")
    figfile = BytesIO()
    plt.savefig(figfile, format="png")
    figfile.seek(0)
    figdata = base64.b64encode(figfile.getvalue())
    return await render_template_string(
        TEMPLATE, plot=figdata.decode(), last_temperature=last_temperature, from_date=from_date, to_date=to_date
    )


def main():
    app.run(debug=True, port=5000, host="0.0.0.0")


if __name__ == "__main__":
    main()
