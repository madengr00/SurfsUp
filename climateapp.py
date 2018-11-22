#Import Libraries
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

##---------- Database Setup ----------##
#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables from engine
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

##---------- Flask Setup ---------##
app = Flask(__name__)

##---------- Flask Routes ---------##
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to My Climate App.<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"--------------------------------------------<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"

        f"--------------------------------------------<br/>"
        f"Use these to find Minimum, Average, and Maximum Temperatures<br/>"
        f"Dates should be entered as 'YYYY-MM-DD'<br/>"
         f"--------------------------------------------<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitations():
    #Query Precipitation - All Data in the last year of data
    precipitation =session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').all()
    '''Convert the query results to a dictionary using date as the key and prcp as the value. Return the JSON representation of the dict.'''
    all_prcp = []
    for p in precipitation:
        prcp_dict = {}
        prcp_dict["date"] = p.date
        prcp_dict["prcp"] = p.prcp
        all_prcp.append(prcp_dict)
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Query the stations and the counts in descending order.
    station_activity = session.query(Measurement.station,func.count(Measurement.station).label('count')).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    all_stat = []
    for s in station_activity:
        stat_dict = {}
        stat_dict["Station ID"] = s.station
        stat_dict["Num Meas"] = s.count
        all_stat.append(stat_dict)
    return jsonify(all_stat)

@app.route("/api/v1.0/tobs")
def temp_observations():
    #Query the last 12 months of temperature observations
    temperatures =(session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').all())
    one_year_tobs = []
    for t in temperatures:
        tobs_dict = {}
        tobs_dict["date"] = t.date
        tobs_dict["tobs"] = t.tobs
        one_year_tobs.append(tobs_dict)
    return jsonify(one_year_tobs)

def calc_temps_start_only(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()


@app.route("/api/v1.0/<start_date>")
def start_temps(start_date):
    temps = calc_temps_start_only(start_date)
    temps = list(np.ravel(temps))
    print(temps)
    return jsonify(temps)


def calc_temps_start_end(start_date,end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_temps(start_date,end_date):
    temps = calc_temps_start_end(start_date,end_date)
    temps = list(np.ravel(temps))
    print(temps)
    return jsonify(temps)

       




if __name__ == '__main__':
    app.run(debug=True)