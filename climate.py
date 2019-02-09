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

# Create our session (link) from Python to the DB
#session = Session(engine)
Session = sessionmaker(bind=engine)

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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/passengers"
    )


@app.route("/api/v1.0/names")
#def names():
#    """Return a list of all passenger names"""
    # Query all passengers
#    results = session.query(Passenger.name).all()

    # Convert list of tuples into normal list
#    all_names = list(np.ravel(results))

#    return jsonify(all_names)


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of passenger data including the name, age, and sex of each passenger"""

    try:
        session = Session()

        # Find the last data point 
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

        # Convert last date to String
        last_date = "%s" %(last_date)

        # Calculate the date 1 year ago
        first_date = dparser.parse(last_date, fuzzy=True) - dt.timedelta(days=365)

        # Convert from datatime type to string in the format of yyyy-mm-dd
        first_date = first_date.strftime('%Y-%m-%d')
        
        # Perform a query to retrieve the data and precipitation scores
        result = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= first_date).\
                filter(Measurement.date <= last_date).\
                order_by(Measurement.date).all()

        # Create a dictionary from the row data and append to a list of all_passengers
        all_precipitation = []
        for precipitation in result:
            precipitation_dict = {}
            #precipitation_dict["date"] = precipitation.date
            precipitation_dict[precipitation.date] = precipitation.prcp
            all_precipitation.append(precipitation_dict)

        return jsonify(all_precipitation)
    finally:
        session.close()
        
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""

    try:
        session = Session()
        result1 = session.query(Station.id, Station.name).all()
        all_stations = []
        for station in result1:
            station_dict = {}
            station_dict['ID'] = station.id
            station_dict['Station Name'] = station.name
            all_stations.append(station_dict)
            
        return jsonify(all_stations)
    finally:
        session.close()

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature from previous year"""

    try:
        session = Session()

        # Find the last data point 
        last_date1 = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

        # Convert last date to String
        last_date1 = "%s" %(last_date1)

        # Calculate the date 1 year ago
        first_date1 = dparser.parse(last_date1, fuzzy=True) - dt.timedelta(days=365)

        # Convert from datatime type to string in the format of yyyy-mm-dd
        first_date1 = first_date1.strftime('%Y-%m-%d')

        result_tobs = session.query(Measurement.tobs).\
        filter(Measurement.date >= first_date1).\
        filter(Measurement.date <= last_date1).all()
        #filter(Measurement.station == most_active_stat).all()

        all_tobs = []
        for tobs in result_tobs:
            tob_dict = {}
            tob_dict['Temperature'] = tobs.tobs
            
            all_tobs.append(tob_dict)
            
        return jsonify(all_tobs)
    finally:
        session.close()

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def timeperiod(start, end):
    """Return a list of stations"""
    session = Session()

    try:
        
        if (end != None):
            result3 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            result3 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).all()

        print(result3)
        if (result3[0][0] == None):
            return f"wrong date range"

        all_prcp = []    
        for prcp in result3:
            prcp_dict = {}
            prcp_dict['TMIN'] = prcp[0]
            prcp_dict['TAVG'] = prcp[1]
            prcp_dict['TMAX'] = prcp[2]
            all_prcp.append(prcp_dict)
        
        return jsonify(all_prcp)
    except:
        return f"date wrong format"
    finally:
        session.close()

    

if __name__ == '__main__':
    app.run(debug=True)
