import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify
import datetime as dt
import dateutil.parser as dparser

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a global session factory from Python to the DB
Session = sessionmaker(bind=engine)

#################################################
# Retrieve beginning date, last date and 1 year from the last date as first date 
#################################################
session = Session()
    
# Retrieve the last date 
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
begin_date = session.query(Measurement.date).order_by(Measurement.date).first()    

# Convert last date to String
last_date = "%s" %(last_date)
begin_date = "%s" %(begin_date)

# Calculate the date 1 year ago
first_date = dparser.parse(last_date, fuzzy=True) - dt.timedelta(days=365)

# Convert from datatime type to string in the format of yyyy-mm-dd
first_date = first_date.strftime('%Y-%m-%d')

session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    
    font_color = '#045FB4'
    bkg_color = '#E6E6E6'

    return (
        f"<p style='font-size:1.5em; color:{font_color}; text-align:center'>Welcome to Climate API</p><br/>"

        f"<p style='font-size:1.5em;'>Usage:</p>"

        f"<p style='color:{font_color}; background-color:{bkg_color}'>/api/v1.0/precipitation</p>"
        f"<p>Retrieve the last 12 months of precipitation data from the last date point.</p>"

        f"<p style='color:{font_color}; background-color:{bkg_color}'>/api/v1.0/stations</p>"
        f"<p>Retrieve a list of stations.</p>"

        f"<p style='color:{font_color}; background-color:{bkg_color}'>/api/v1.0/tobs</p>"
        f"<p>Query for the dates and temperature observations from a year from the last data point.</p>"

        f"<p><div style='color:{font_color}; background-color:{bkg_color}'>/api/v1.0/start/end</div></p>"
        f"<p>Date Format: <b>yyyy-mm-dd</b></p>"
        f"<p>Dataset first date: {begin_date}  Dataset last date: {last_date}</p>"
        f"<p>Return a list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.</p>"
        f"<p>When given the start only, calculate the above for all dates greater than and equal to the start date.</p>"
        f"<p>When given the start and the end date, calculate the above for dates between the start and end date inclusive.</p>"
        f"<p><u>Please make sure the start date is earlier than the end date</u></p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve the last 12 months of precipitation data from the last date point"""

    session = Session()

    # Query to retrieve the data and precipitation scores
    result = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= first_date).\
            filter(Measurement.date <= last_date).\
            order_by(Measurement.date.desc()).all()

    # Create a dictionary from the result data with date as key and precipitation as value
    all_precipitation = []
    for precipitation in result:
        precipitation_dict = {}
        precipitation_dict[precipitation.date] = precipitation.prcp
        all_precipitation.append(precipitation_dict)

    session.close()

    return jsonify(all_precipitation)
     
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""

    session = Session()
    
    # Query to retrieve all station id and names
    result = session.query(Station.id, Station.name).all()

    # Create a list of dictionaries to keep the result id and names
    all_stations = []
    for station in result:
        station_dict = {}
        station_dict['ID'] = station.id
        station_dict['Station Name'] = station.name
        all_stations.append(station_dict)

    session.close()       
    return jsonify(all_stations)
        
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature from previous year"""
    
    session = Session()

    # Query to retrieve temperature from 1 year 
    result = session.query(Measurement.tobs, Measurement.date).\
                filter(Measurement.date >= first_date).\
                filter(Measurement.date <= last_date).\
                order_by(Measurement.date.desc()).all()
                #filter(Measurement.station == most_active_stat).all()

    # Create a list of dictionaries to keep the result dates and temperatures
    all_tobs = []
    for tobs in result:
        tob_dict = {}
        tob_dict['Date'] = tobs.date
        tob_dict['Temperature'] = tobs.tobs   
        all_tobs.append(tob_dict)
    
    session.close()        
    return jsonify(all_tobs)
        
@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def timeperiod(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    
    session = Session()

    try:
        if (end != None):
            # If both start date and end date are given
            result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            # Only start date is given
            result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).all()

        # No result found. Something is wrong with the input date(s)
        if (result[0][0] == None):
            return f"No result. Please go to the home page to check the usage of this API"

        # Create a dictionary to keep the calculation result
        temp_dict = {}
        temp_dict['TMIN'] = result[0][0]
        temp_dict['TAVG'] = result[0][1]
        temp_dict['TMAX'] = result[0][2]
        
        return jsonify(temp_dict)
    except:
        # Depending on database behavior, program can reach here when date(s) format is wrong
        return f"Error! Please go to the home page to check the usage of this API"
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)
