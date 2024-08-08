#
#""" A micro-service for the EARTH-based api (formerly part of planetary-api)
#    
#    Adapted from code in https://github.com/nasa/planetary-api
#    Dec 20, 2015 (original code written by Dan Hammer) 
#   
#    @author=JustinGOSSES @email=justin.c.gosses@nasa.gov
#
#    It basically is a simplified wrapper for google earth engine and only gets images from landsat 8
#"""

#### THIS IS THE ORIGINAL DEMO FLASK APP THAT IS KEPT HERE FOR TESTING PURPOSES
#### IF YOU NEED TO TEST IF EVERYTHING ELSE IS SET UP WELL LIKE APACHE USE THIS!
# from flask import Flask
#app = Flask(__name__)
#
#@app.route('/')
#def hello_world():
#	return 'Hello, World! darn it'
#
#if __name__ == "__main__":
#    app.run()
#### END OF :::::ORIGINAL DEMO FLASK APP THAT IS KEPT HERE FOR TESTING PURPOSES

import os
import sys

### justin edit
#sys.path.insert(0, "../lib")
sys.path.insert(0, ".")
sys.path.insert(1, "/var/www/html/flaskproject")
sys.path.insert(2,'..')

from flask import request, jsonify, render_template, Response, Flask, send_file, url_for
from flask_cors import CORS
from datetime import datetime

#### THIS IS AN ALTERNATIVE WAY TO BRING IN UTIL.py that doesn't work WHEN STARTED VIA APACHE SERVER
# import util
#from util import *
import util
import json
import requests
import ee
import logging
from PIL import Image
import urllib

app = Flask(__name__)
CORS(app)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__).setLevel(logging.DEBUG)


#### Google earth engine has some weird path issues such that what is treated as the base path changes if Apache server starts app.py
#### To get around these issues, we'll use one path if var is detected in the base folder and enough if it is not detected. 
#### When an apache server starts app.py, the CWD or current working directory is very high and includes things like var, etc, and others.
cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))

#### THIS IS THE PATH WHEN RUN LOCALLY
json_url = 'privatekey.json'
pic_url = 'static/temp.png'
#### THIS IS THE PATH IF RUN BY APACHE SERVER
#### NOTE: The privatekey.json never actually moves!
if('var' in files):
    json_url = cwd+'var/www/html/flaskproject'+'/privatekey.json'
    pic_url = cwd+'var/www/html/flaskproject'+'/static/temp.png'
    print("using the long url of:",json_url )

#### If you don't want to use the service account to start the API, we can initiate with a normal google account of any kind. 
#### ee.Authenticate will start up a browses page that asks you to log in with your google account 
#### and then gives you a code that you bring back here and put into a form in your console. 
#### After that, the ee.Initialize can run

#ee.Authenticate()
#ee.Initialize()

#### Alternatively, you can start with the service account
#### The service account is tied to a google app engine project that justin.c.gosses@nasa.gov started. 
##### Anyone in the OCIO data analytics project on GCP should have access to it.
service_account = 'idas-google-earth-admin@dotted-furnace-431819-e9.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, json_url)
ee.Initialize(credentials)


# this should reflect both this service and the backing 
# assorted libraries
SERVICE_VERSION = 'v5000'
DEFAULT_ADDRESS = '1800 F street, Washington, DC, NW'
EARTH_IMAGE_METHOD_NAME = 'earth/imagery'
ALLOWED_EARTH_IMAGE_FIELDS = ['lat', 'lon', 'address', 'dataset', 'date', 'cloud_score', 'dim']

def _abort(code, msg, usage=True):
    if (usage):
        msg += " " + _usage() + "'"
    response = jsonify(service_version=SERVICE_VERSION, msg=msg)
    response.status_code = code
    print (str(response))
    return response


# def _earth_image_handler(lat=None, lon=None, dataset='LC8_L1T_TOA', date='2014-01-01', cloud=False, dim=0.025):
def _earth_image_handler(lat=None, lon=None, dataset='LANDSAT/LC08/C01/T1_SR', date='2014-01-01', cloud=False, dim=0.025):

    LOG.info("Earth Image Handler called")

    '''
    params = {
        'cloud_score': cloud,
        'lon': float(lon),
        'lat': float(lat),
        'date': date,
        'dim': float(dim)
    }
    '''

    resource = {'planet': 'earth', 'dataset': dataset}
    bbox = {
        'xmin': lon - (dim / 2),
        'xmax': lon + (dim / 2),
        'ymin': lat - (dim / 2),
        'ymax': lat + (dim / 2)
    }

    # Make the call to Google Earth Engine
    LOG.debug("make call to google earth engine to get asset")
    asset = util.GEEasset(bbox)

    LOG.debug("get the resource")
    if(cloud==False):
        res = asset.image(date=date, cloud_score=cloud)
    else:
        res = asset.cloud_image_collection(date=date, cloud_score=cloud)
        
    
    LOG.debug("update resource dictionary")
    res.update(dict(resource=resource))
    
    LOG.debug("return result") 
    return res


'''
class EarthListHandler(webapp2.RequestHandler):
    """Class to construct the input for grabbing earth imagery.  Returns a
    JSON object with the URLs of the returned image thumbnails."""
    
    def get(self):
        lat = self.request.get('lat', None)
        lon = self.request.get('lon', None)
        if (lat is None and lon is None):
            default_address = '1800 F street, Washington, DC, NW'
            address = self.request.get('address', default_address)
            lat, lon = util.geocode(address)
        dataset = self.request.get('dataset', 'LC8_L1T_TOA')
        begin = self.request.get('begin')
        end = self.request.get('end', datetime.today().strftime("%Y-%m-%d"))
        dim = self.request.get('dim', 0.025)
        params = {
            'resource': {
                'planet': 'earth',
                'dataset': dataset
            },
            'lon': float(lon),
            'lat': float(lat),
            'begin': begin,
            'end': end,
            'dim': float(dim)
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(util.asset_list(params)))
    '''


def _usage(joinstr="', '", prestr="'"):
    return "Allowed request fields for " + EARTH_IMAGE_METHOD_NAME + " method are " + prestr + joinstr.join(
        ALLOWED_EARTH_IMAGE_FIELDS)


def _validate(data):
    for key in data:
        if key not in ALLOWED_EARTH_IMAGE_FIELDS:
            return False
    return True


#### Endpoints
#### There are 3 main endpoints: home or / (returns html page with info), assets (json returned), imagery (returns PNG image file)


@app.route('/')
def home():
    return render_template('home.html', version=SERVICE_VERSION, \
                           service_url=request.host, \
                           methodname=EARTH_IMAGE_METHOD_NAME, \
                           usage=_usage(joinstr='", "', prestr='"') + '"')

### THIS GETS THE JSON WITH INFORMATION AND THE URL FOR THE IMAGE - ADDED BY JUSTIN
@app.route('/' + SERVICE_VERSION + '/' + "earth/assets" + '/', methods=['GET'])
def get_earth_assets():
    try:

        # application/json GET method 
        args = request.args

        if not _validate(args):
            return _abort(400, "Bad Request incorrect field passed.")

        date = args.get('date', datetime.strftime(datetime.today(), '%Y-%m-%d'))

        lat = args.get('lat', None)
        lon = args.get('lon', None)
        
        if (lat is None and lon is None):
            address = args.get('address', DEFAULT_ADDRESS)
            lat, lon = util.geocode(address)
        else:
            lat = float(lat)
            lon = float(lon)
        
        #dataset = args.get('dataset', 'LC8_L1T_TOA')
        dataset = args.get('dataset', 'LANDSAT/LC08/C01/T1_SR')
        
        # date = '2014-01-01'
        cloud = bool(args.get('cloud_score', False))
        dim = float(args.get('dim', 0.025))

        # get data
        data = _earth_image_handler(lat, lon, dataset, date, cloud, dim)
        data['service_version'] = SERVICE_VERSION

        # return info as JSON
        return jsonify(data)

    except Exception as ex:

        etype = type(ex)
        # print (str(etype)+"\n "+str(ex))
        if etype == ValueError or "BadRequest" in str(etype):
            LOG.error("Bad request. Msg: " + str(ex))
            return _abort(400, str(ex) + ".")

        elif etype == util.NotFoundError:
            return _abort(404, str(ex), usage=False)
        else:
            LOG.error("Service Exception. Msg: " + str(ex))
            return _abort(500, "Internal Service Error", usage=False)

#### EXAMPLE URL http://127.0.0.1:5000/v5000/earth/imagery/?lon=-95.21&lat=29.67&date=2018-01-01&dim=0.32
# @app.route('/' + SERVICE_VERSION + '/' + EARTH_IMAGE_METHOD_NAME + '/', methods=['GET'])
@app.route('/' + SERVICE_VERSION + '/' + "earth/imagery" + '/', methods=['GET'])
def get_earth_image():
    try:

        # application/json GET method 
        args = request.args

        if not _validate(args):
            return _abort(400, "Bad Request incorrect field passed.")

        date = args.get('date', datetime.strftime(datetime.today(), '%Y-%m-%d'))

        lat = args.get('lat', None)
        lon = args.get('lon', None)
        
        if (lat is None and lon is None):
            address = args.get('address', DEFAULT_ADDRESS)
            lat, lon = util.geocode(address)
        else:
            lat = float(lat)
            lon = float(lon)
        
        dataset = args.get('dataset', 'LANDSAT/LC08/C01/T1_SR')
        
        cloud = bool(args.get('cloud_score', False))
        dim = float(args.get('dim', 0.025))

        # get data
        data = _earth_image_handler(lat, lon, dataset, date, cloud, dim)
        data['service_version'] = SERVICE_VERSION

        image_url = data["url"]
        r = requests.get(image_url, allow_redirects=True)

        print("type r",type(r))
        print("r",r)

        #### NOTE: pic_url is defined up top!
        print("pic_url",pic_url)
        urllib.request.urlretrieve(image_url, pic_url)
        # # return info as PNG
        return send_file(pic_url, mimetype='image/png')

    except Exception as ex:

        etype = type(ex)
        if etype == ValueError or "BadRequest" in str(etype):
            LOG.error("Bad request. Msg: " + str(ex))
            return _abort(400, str(ex) + ".")

        elif etype == util.NotFoundError:
            return _abort(404, str(ex), usage=False)
        else:
            LOG.error("Service Exception. Msg: " + str(ex))
            return _abort(500, "Internal Service Error", usage=False)




@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return _abort(404, "Sorry, Nothing at this URL.", usage=True)


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    LOG.error("Service Internal Exception. Msg: " + str(e))
    return _abort(500, 'Sorry, unexpected error: {}'.format(e), usage=False)


if __name__ =='__main__':
    app.run()
