import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
session = Session(engine)

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
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["prcp"] = precipitation.prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


if __name__ == '__main__':
    app.run(debug=True)
