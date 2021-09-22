"""
Return a series of Landsat 7 or 8 image URLs for a specified location, along
with the acquisition date of the asset.
"""

import ee 
from datetime import datetime, timedelta
import requests


class NotFoundError(Exception):
    pass


def geocode(address):
    base = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    address = address.replace(' ', '+')
    address = address.replace('%20', '+')
    raw = requests.get(address).text
    # raw = urlfetch.fetch(base + address)
    res = json.loads(raw.content)
    coords = res['results'][0]['geometry']['location']
    return coords['lat'], coords['lng']


def verify_bbox(bbox):
    """Check that bbox is properly specified."""
    if type(bbox) != dict:
        raise Exception(
            'Malformed bounding box: must be "dict" type.\n%s' % str(bbox))

    for coord in ['xmax', 'xmin', 'ymax', 'ymin']:
        if coord not in bbox:
            raise Exception('Malformed bounding box: missing %s value' % coord)

    if bbox['xmin'] > bbox['xmax']:
        raise Exception('Malformed bounding box: xmin is greater than xmax')

    if bbox['ymin'] > bbox['ymax']:
        raise Exception('Malformed bounding box: ymin is greater than ymax')

    return True


def parse_bbox(bbox):
    """Convert a bbox dictionary to list a la [xmax, ymax, xmin, ymin]."""
    if verify_bbox(bbox):
        xmax = bbox['xmax']
        ymax = bbox['ymax']
        xmin = bbox['xmin']
        ymin = bbox['ymin']

    return [xmax, ymax, xmin, ymin]


def bbox_to_coords(bbox):
    """Convert a bbox dictionary to a list of coordinate lists, suitable for
    use as a counter-clockwise polygon geometry in Google Earth Engine."""
    xmax, ymax, xmin, ymin = parse_bbox(bbox)

    return [[xmax, ymax],
            [xmin, ymax],
            [xmin, ymin],
            [xmax, ymin],
            [xmax, ymax]]


def hsvpan(img):
    """Accepts a GEE image objects and returns a pan-sharpened GEE image."""
    #r, g, b, p = ['B6', 'B5', 'B4', 'B8']
    r, g, b, p = ['B3', 'B5', 'B4', 'B6']
    color = img.select(r, g, b).unitScale(0, 155)
    pan = img.select(p)
    huesat = color.rgbToHsv().select(['hue', 'saturation'])
    upres = ee.Image.cat(huesat, pan).hsvToRgb()
    return upres


def acqtime(feature):
    """A handler that returns the correctly formatted date, based on asset."""
    msec = feature['properties']['system:time_start']
    return datetime.fromtimestamp(msec / 1000).isoformat()


def cloudScore(landsat_img, coords, thresh=25):
    landsat_img = ee.Image(landsat_img).set('SENSOR_ID', 'OLI_TIRS')
    poly = ee.Feature(ee.Geometry.Polygon(coords))
    geom = ee.Geometry.Polygon(coords)
    scores = ee.Algorithms.Landsat.simpleCloudScore(landsat_img)
    binary = scores.select('cloud').clip(poly).gt(thresh)
    print("binary",binary,"type",type(binary))
    # res = binary.reduceRegion(ee.Reducer.mean(), geom, 25).getInfo()
    #res = binary.reduceRegion(ee.Reducer.mean(),30}).getInfo()
    res = binary.reduceRegion(ee.Reducer.mean(), geom, 25)

    # cloudy_scene = landsat_img
    # ## Load a cloudy Landsat scene and display it.
    # # var cloudy_scene = ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140926');
    # #### Add a cloud score band.  It is automatically called 'cloud'.
    # scored = ee.Algorithms.Landsat.simpleCloudScore(cloudy_scene)
    # #### Create a mask from the cloud score and combine it with the image mask.
    # mask = scored.select(['cloud']).lte(20)
    # #### Apply the mask to the image and display the result.
    # masked = cloudy_scene.updateMask(mask)
    # #### Load a Landsat 8 composite and set the SENSOR_ID property.
    # mosaic = ee.Image(ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').first()).set('SENSOR_ID', 'OLI_TIRS')
    # #### Cloud score the mosaic and display the result.
    # scored_mosaic = ee.Algorithms.Landsat.simpleCloudScore(mosaic)


    try:
        print("res: ",res)
        return float(res['cloud'])
    except TypeError:
        return None


def export_image(idx, coords, cloud_score):
    """Returns the thumbnail URL for a given Landsat image, bounded by the
    supplied coordinates.

    Arguments
        idx: A landsat image ID
        coords: A list of coordinate pairs, closed and counter-clockwise
        sharpen: Boolean indicating whether the image should be pan-sharpened

    Example:
        export_image(
            idx='LC8_L1T_TOA/LC81270592013320LGN00',
            coords=[[0,0], [1,0], [1,1], [0,1], [0,0]],
            sharpen=True
        )
    """
    #img = hsvpan(ee.Image(idx))
    #img = hsvpan(ee.Image('USGS/SRTMGL1_003'))
    # img = ee.Image('LANDSAT/LC08/C01/T1_SR')
    #img = ee.Image('USGS/SRTMGL1_003') ## THIS WORKS!
    print("idx is ",idx)
    print("type idx is ",type(idx))
    # img = ee.Image(idx)


    
    
    # thumb_params = {
    #     'crs': 'EPSG: 4326',
    #     'region': str(coords),
    #     # 'size': [512, 512],
    #     'dimensions': [512, 512],
    #     'format': 'png',
    #     'min': '0.01',
    #     'max': '0.5',
    #     'gamma': '1.7'
    # }
    # http://127.0.0.1:5000/v5000/earth/imagery/?lon=100.75&lat=40.5&date=2017-01-01
    # https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/thumbnails/583ba3a19b4fe932cedf847dad7cdf9a-ecb5736d2f3ed4461af711493dcca7ae:getPixels

    ## houston example http://127.0.0.1:5000/v5000/earth/imagery/?lon=-95&lat=29.7&date=2018-07-01&dim=0.3
    thumb_params = {
        'crs': 'EPSG: 4326',
        'region': str(coords),
        #'size': [512, 512],
        'dimensions': [2048, 2048],
        'format': 'png',
        'min': 0,
        'max': 3200,
    }
    
    # dataset = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterDate('2016-01-01', '2016-01-10')
    # print("dataset",dataset)
    # image_test = dataset.median()
    
    dataset = ee.Image(idx) #.filterDate('2016-01-01', '2016-01-10')
    #dataset = hsvpan(ee.Image(idx))
    print("dataset",dataset)
    image_test = dataset #.median()


    #final = dict(url=img.getThumbUrl(thumb_params))
    # final = dict(url = img.getThumbUrl({'min': 0, 'max': 4000, 'dimensions': 512,
    #             'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5']}))
    print("cloud score in export image function is: ",cloud_score)
    #final = dict(url = img.getThumbUrl(thumb_params ))
    final2 = dict(url = image_test.getThumbUrl(thumb_params ))

    if cloud_score:
        print("hit cloud_scoure exists:",cloud_score)
        print("type ee.Image(idx)",type(image_test))
        print("idx",idx)
        #final2["cloud_score"] = "test"
        final2["cloud_score"] = cloudScore(idx, coords)
    return final2


class GEEasset:
    """A GEE Asset for a bounding box, given the name of the image collection.
    The only GEE asset that is currently supported is 'LC8_L1T_TOA'.

    Example usage:
        bbox = {'xmin': -78, 'xmax': -77.9, 'ymax': 40, 'ymin': 39.9}
        asset = GEEasset(bbox)
        idx = asset.id_stack('2014-01-01', '2015-01-01')
        print "The dates of 'LC8_L1T_TOA' images are:\n"
        for k in idx.keys():
            print k
    """

    def __init__(self, bbox):
        """Authenticate to GEE and instantiate the class with the GEE Image
        collection defined by the asset and the geographic extent"""
        self.coords = bbox_to_coords(bbox)
        self.poly = ee.Geometry.Polygon(self.coords)
        # self.coll = ee.ImageCollection('LANDSAT/LC08').filterBounds(self.poly)
        self.coll = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterBounds(self.poly)

    def id_stack(self, begin, end):
        """Returns the a dictionary with the acquisition date as the key and
        the asset IDs as the value, all for the image collection between the
        two supplied dates in YYYY-MM-DD format."""
        stack = self.coll.filter(ee.Filter.date(begin, end)).getInfo()['features']
        return [dict(date=acqtime(x), id=x['id']) for x in stack]

    def image(self, date, cloud_score, offset=30):
        """Returns a dictionary with the acquisition date as the key and the
        export URL as the value.  Effectively replaces the value for each date
        key in `id_stack` with the export URL rather than the Image ID."""
        target_date = datetime.strptime(date, "%Y-%m-%d")
        delta = timedelta(days=offset)
        available = self.id_stack(target_date - delta, target_date + delta)
        # available = self.coll
        if len(available) == 0:
            raise NotFoundError('No imagery for specified date.')
        else:
            def _sorter(d):
                img_date = datetime.strptime(d['date'][0:19], "%Y-%m-%dT%H:%M:%S")
                return abs(img_date - target_date)

            closest = sorted(available, key=_sorter)[0]
            closest.update(
                export_image(
                    closest['id'],
                    self.coords,
                    cloud_score=cloud_score
                )
            )
            return closest
    def cloud_image_collection(self, date, cloud_score, offset=30):
        """Returns a dictionary with the acquisition date as the key and the
        export URL as the value.  Effectively replaces the value for each date
        key in `id_stack` with the export URL rather than the Image ID."""
        target_date = datetime.strptime(date, "%Y-%m-%d")
        delta = timedelta(days=offset)
        available = self.id_stack(target_date - delta, target_date + delta)
        # available = self.coll
        if len(available) == 0:
            raise NotFoundError('No imagery for specified date.')
        else:
            def _sorter(d):
                img_date = datetime.strptime(d['date'][0:19], "%Y-%m-%dT%H:%M:%S")
                return abs(img_date - target_date)

            closest = sorted(available, key=_sorter)[0]
            closest.update(
                export_image(
                    closest['id'],
                    self.coords,
                    cloud_score=cloud_score
                )
            )
            return closest


def asset_list(params):
    d = params['dim']
    lat = params['lat']
    lon = params['lon']
    begin = params['begin']
    end = params['end']
    bbox = {
        'xmin': lon - (d / 2),
        'xmax': lon + (d / 2),
        'ymin': lat - (d / 2),
        'ymax': lat + (d / 2)
    }
    asset = GEEasset(bbox)
    res = asset.id_stack(begin, end)
    return dict(resource=params['resource'], results=res, count=len(res))


def image_handler(params):
    """Handles the API request and properly returns the requested information,
    specifically a stack of JSON formatted dates and image URLs"""
    d = params['dim']
    lat = params['lat']
    lon = params['lon']
    bbox = {
        'xmin': lon - (d / 2),
        'xmax': lon + (d / 2),
        'ymin': lat - (d / 2),
        'ymax': lat + (d / 2)
    }
    asset = GEEasset(bbox)
    res = asset.image(date=params['date'], cloud_score=params['cloud_score'])
    res.update(dict(resource=params['resource']))
    print("image_handler function ran this is bottom")
    return res

