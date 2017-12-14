import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
app = Flask(__name__)

one_year = datetime.datetime.now() - datetime.timedelta(days=365)
last_year = "%s-%s-%s" % (one_year.year,one_year.month,one_year.day)

@app.route("/")
def welcome():
    return(
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation for the last year<br/>"

        f"/api/v1.0/stations"
        f"- List of stations<br/>"
        
        f"/api/v1.0/tobs"
        f"- Temperature Observations for the last Year<br/>"
        
        f"/api/v1.0/<start>"
        f"- Temperatures from start date<br/>"
        
        f"/api/v1.0/<start>/<end>"
        f"- Temperature from the start-end dates provided<br/>"
    )


## Create last year of precipitation query
@app.route("/api/v1.0/precipitation")
def precipitation(start=last_year):
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start).all()
    yr_precip = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Precip'] = float(result[1])
        yr_precip.append(row)
    return jsonify(yr_precip)

#Stations query
@app.route("/api/v1.0/stations")
def station_list():
    results = session.query(Measurement.station).distinct().all()
    stations = list(np.ravel(results))
    return jsonify(stations)

#Temp query over last year
@app.route("/api/v1.0/tobs")
def temperatures(start=last_year):
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start).all()
    yr_temps = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Temp'] = float(result[1])
        yr_temps.append(row)
    return jsonify(yr_temps)


#Temp query from start time
@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    result = session.query(Measurement.tobs).filter(Measurement.date >= start)
    results = [a[0] for a in result[:]]
    df = pd.DataFrame(results)[0]
    temp_mean = df.mean()
    temp_max = df.max()
    temp_min = df.min()
    averages = {"Min_Temp":str(temp_min), "Avg_Temp": temp_mean, "Max_Temp":str(temp_max)}
    return jsonify(averages)

#Temp query between start and end times
@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start,end):
    result = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end)
    results = [a[0] for a in result[:]]
    df = pd.DataFrame(results)[0]
    temp_mean = df.mean()
    temp_max = df.max()
    temp_min = df.min()
    averages = {"Min_Temp":str(temp_min), "Avg_Temp": temp_mean, "Max_Temp":str(temp_max)}
    return jsonify(averages)


if __name__ =='__main__':
    app.run(debug=True)