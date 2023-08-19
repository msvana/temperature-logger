import base64
import datetime
import sqlite3
from io import BytesIO

import matplotlib.pyplot as plt
from more_itertools import batched
from quart import Quart, render_template_string

db_con = sqlite3.connect("temperatures.db")
app = Quart(__name__)


TEMPLATE = """
    <!DOCTYPE html>
    <html>
        <body>
            <center>
            Last reading<br>
            <big>{{last_temperature[1]}}&deg;C</big><br>
            <small>{{last_temperature[0]}}</small><br>
            <img src=data:image/png;base64,{{plot}}>
            </center>
        </body>
    </html>
"""


@app.get("/")
async def chart():
    db_cursor = db_con.cursor()
    db_cursor.execute("SELECT * FROM temperatures ORDER BY timestamp ASC")
    temperature_records = [(datetime.datetime.fromtimestamp(r[0]), r[1]) for r in db_cursor]
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
    return await render_template_string(TEMPLATE, plot=figdata.decode(), last_temperature=temperature_records[-1])


def main():
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
