#  List all routes that are available.
#   /api/v1.0/precipitation
#   Convert the query results to a Dictionary using date as the key and prcp as the value.
#   Return the JSON representation of your dictionary.
#   /api/v1.0/stations
#    Return a JSON list of stations from the dataset.
#   /api/v1.0/tobs
#   query for the dates and temperature observations from a year from the last data point.
#   Return a JSON list of Temperature Observations (tobs) for the previous year.
#   /api/v1.0/<start> and /api/v1.0/<start>/<end>
#   Return a JSON list of the minimum temperature, the average temperature, 
#   and the max temperature for a given start or start-end range.
#   When given the start only, calculate TMIN, TAVG, and TMAX for all 
#   dates greater than and equal to the start date.
#   When given the start and the end date, calculate the TMIN, TAVG, and 
#   TMAX for dates between the start and end date inclusive.
#dependencies
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
# Python, SQL, toolkit, and engine stuff
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct
#db
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing db into new model
Base = automap_base()
# reflect the tbl
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save references to each tbl
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create sesh from Py to the DB
session = Session(engine)
# Flask now
app = Flask(__name__)
# Flask Routes
@app.route("/")
def welcome():
    """Available Routes"""
    return (
           f"Here are your available routes (endpoints):<br/><br/>"
           f"/api/v1.0/precipitation<br/>"
           f"/api/v1.0/stations<br/>"
           f"/api/v1.0/tobs<br/>"
           f"/api/v1.0/start_date&emsp;  i.e.:&emsp; /api/v1.0/2017-01-01 <br/>"
           f"/api/v1.0/start_date/end_date&emsp;  i.e.:&emsp; /api/v1.0/2017-01-01/2017-03-01 <br/>"
       )
@app.route("/api/v1.0/precipitation")
def precipitation():
       session = Session(engine)
       sel = [(Measurement.date).label("Date"), (Measurement.prcp).label("Precipitation")]
       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date_dt = pd.to_datetime(max_date)
       date_year_back = max_date_dt - dt.timedelta(days=365)
       year_back_str = date_year_back.strftime("%Y-%m-%d")[0]
       year_data = session.query(*sel).\
                     filter(Measurement.date >= year_back_str).\
                     order_by(Measurement.date).\
                     all()
       precipitation_dict = dict(year_data)
       return jsonify(precipitation_dict)
@app.route("/api/v1.0/stations")
def stations():
       session = Session(engine)
       active_stations = session.query(distinct(Measurement.station)).all()
       return jsonify(active_stations)       
@app.route("/api/v1.0/tobs")
def tobs():
       session = Session(engine)
       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date_dt = pd.to_datetime(max_date)
       date_year_back = max_date_dt - dt.timedelta(days=365)
       year_back_str = date_year_back.strftime("%Y-%m-%d")[0]

       year_data = session.query(Measurement.tobs).\
                filter(Measurement.date >= year_back_str).\
                order_by(Measurement.date).\
                all()
       return jsonify(year_data)
#url
@app.route("/api/v1.0/<start_date>")
def startonly(start_date):
       session = Session(engine)
       sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
       result = session.query(*sel).\
              filter(Measurement.date >= start_date).\
              all()      
       return jsonify(result)
#url
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
       session = Session(engine)
       sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
       result = session.query(*sel).\
       filter(Measurement.date >= start_date).\
       filter(Measurement.date <= end_date).\
       all()
       return jsonify(result)
if __name__ == "__main__":
   app.run(debug=True)