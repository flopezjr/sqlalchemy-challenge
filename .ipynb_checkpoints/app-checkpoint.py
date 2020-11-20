# set up and dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#set up database
engine = create_engine("sqlite:///hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# save refrences to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link from python to DB
session = Session(engine)
#############
# Flask Setup
#############
app = Flask(__name__)

##########
#Flask Routes
###########

# create home page route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App Home Page!<br>"
        f"Available Routes Below:<br>"
        f"Precipitation measurement over the last 12 months: /api/v1.0/precipitation<br>"
        f"A list of stations and their respective station numbers: /api/v1.0/stations<br>"
        f"Temperature observations at the most active station over the previous 12 months: /api/v1.0/tobs<br>"
        f"Enter a start date (yyyy-mm-dd) to retrieve the minimum, maximum, and average temperatures for all dates after the specified date: /api/v1.0/<start><br>"
        f"Enter both a start and end date (yyyy-mm-dd) to retrieve the minimum, maximum, and average temperatures for that date range: /api/v1.0/<start>/<end><br>"
    )


# create precipitation route of last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Return the precipitation from the last year"""
    # Calculate the date 1 year ago from the last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurment.date >= prev_year).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


# create station route of a list of the stations in the dataset
@app.route("/api/v1.0/stations")
def stations():

    results = session.query(Station.station).all()

    # convert results into 1D array and convert to list
    stations =list(np.ravel(results))
    return jsonify(stations=stations)


# create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    #Query the primary station for all tobs from last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= '2016-08-23').\
        order_by(Measurement.date >= prev_year).all()
    
    #Unravel results into a 1D conversion list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# create start and start/end route
# min, average, and max temps for a given date range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX"""

    #Select Statement
    sel = [Func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        #Calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date>= start).all()
         #Unravel results into a 1D conversion list
        temps = list(np.ravel(results))
        return jsonify(temps)

        #Calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
       #Unravel results into a 1D conversion list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run(debug=True)