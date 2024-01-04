# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/Hawaii.sqlite")

# Reflect the database into a new model
Base = automap_base()

# Feflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
sql_session = Session(engine)

# Flask Setup
app = Flask(__name__)

def start_calc(date):
    return sql_session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= date).all()

def end_calc(start_date, end_date):
    return sql_session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).all()

# Flask Routes
@app.route("/")
def welcome():
    """Welcome to the App API!"""
    """List all available api routes."""
   # return render_template("index.html")

    urlapi1 = "/api/v1.0/precipitation"
    urlapi2 = "/api/v1.0/stations"
    urlapi3 = "/api/v1.0/tobs"
    urlapi4 = "/api/v1.0/temp/start"
    urlapi5 = "/api/v1.0/temp/start/end"

    return (
        f"Available Routes:<br/>"
        f"<a href={urlapi1}>/api/v1.0/precipitation</a><br/>"
        f"<a href={urlapi2}>/api/v1.0/stations</a><br/>"
        f"<a href={urlapi3}>/api/v1.0/tobs</a><br/>"
        f"<a href={urlapi4}>/api/v1.0/temp/start</a><br/>"
        f"<a href={urlapi5}>/api/v1.0/temp/start/end</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_calc = dt.date(2017,8,23) - dt.timedelta(days=365)

    year_precipitation = sql_session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_calc, Measurement.prcp != None).\
    order_by(Measurement.date).all()

    return jsonify(dict(year_precipitation))

@app.route("/api/v1.0/stations")
def stations():
    station_results = sql_session.query(Station.station).all()
    stations = list(np.ravel(station_results))

    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    year_calc = dt.date(2017,8,23) - dt.timedelta(days=365)

    tobs_results = sql_session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_calc).order_by(Measurement.tobs).all()
    year_temps = list(np.ravel(tobs_results))
    return jsonify(year_temps)
    
@app.route("/api/v1.0/temp/<start>")
def start_date(start):
    calc = start_calc(start)
    temp_calc = list(np.ravel(calc))

    return jsonify(temp_calc)

@app.route("/api/v1.0/temp/<start>/<end>")
def start_end_date(start, end):
    calc = end_calc(start, end)
    temp_calc = list(np.ravel(calc))

    return jsonify(temp_calc)

if __name__ == '__main__':
    app.run(debug=True)