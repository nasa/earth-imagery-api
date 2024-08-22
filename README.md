# Earth-Imagery-API

## Description
This repository contains a flask API that provides satellite imagery. It is designed to be very simple and easy to use with minimal functionality and is provided to the public through api.nasa.gov. It focuses on one Earth imagery product, Landsat 8 collection 2.

#### Purpose
While there are many ways NASA and other government agencies provide satellite imagery to the public, these are often more fully featured and as a result more complex to use. This API is built to have a very basic intuitive interface and to be found easily on api.nasa.gov. It is designed for those just getting started with satellite imagery and APIs. It can server as a first step to using more complex imagery services.

#### History & Why Open Sourced
The earth imagery API has existed as an option on api.nasa.gov for several years. Many people have built demos using it or integrated it into their applications. We don't recommend using it in production. It is shared mostly as a very easy and feature sparse starting point for learning.

As such, we intend to keep the API endpoints as they are without changes that would disrupt previous work. 

We are open sourcing this repository in order to help others see how it works. We also expect others might detect problems and submit issues or pull requests of fixes in the same way users have done for <a href="https://github.com/nasa/apod-api">APOD-API</a>. 

## Where Data Comes From

Under the hood, this API leverages a moderately complex API, Google Earth Engine. Google Earth Engine in turn, leverages NASA APIs to get the satellite imagery it provides to endusers.

## Language(s) used by the software
Mostly Python with a little JavaScript and HTML.

## LICENSE
Apache 2.0


## Contributions

Because this API feeds off of the Google Earth Engine API (which in terms consumes NASA data) it can sometimes break when Google Earth Engine API makes breaking changes. We gladdly accept issue and code contributions! This also means you can deploy your own version of the API and are not dependent on calling the api.nasa.gov version. 

This API was originally developed by others. It is maintained when time allows, so there may not be a super fast response to your issue.

If you submit any pull requests, please remember that one of the main goals of this repository is to provide a very easy to use API interaface. Additionally, we don't want that API interface to change if at all possible as a lot of people have built things on top of it. 

## If You Need Additional Features
If you used this API a little and now need additional features, that's great! There's a variety of other APIs out there available for you with different strengths and weaknesses. What makes the most sense depends on the problem you're trying to solve, so we can't really advise you much here except to say that there are a variety of options built on top of google earth engine, other tools like leaflet or open layers, and also a variety of <a href="https://earthdata.nasa.gov/">NASA Earth Science data services</a>. Good Luck!

## Deployment 
We're currently deploying this on AWS, but it isn't specific to AWS. We're only noting it here as there are some slightly different ways to deploy a flask app work fine on a local server or ubuntu server that don't work as well on AWS EC2 or Elastic Beanstalk. If you submit a pull request that breaks AWS deployment, we'll have to decline the pull request or ask for an edit.

### Authentication
As mentioned above, this API calls another, Google Earth Engine (GEE). GEE requires authentication. There are two methods for google earth engine API requires authentication. The API that this repository builds does not contain any authentication method itself.

#### Google User Account Sign-in
The first authentication methodod is sign-in with a google account. This method requires a human to be in the loop as a pop-up screen appears and you have to enter your google email and password.

#### Service Account
You'll want to use this authentication method if setting up an API like we do as it doesn't require a human to be in the loop. You'll pass it service account details and a private key file. 

<i>Please find the instructions for either of these options on <a href="https://earthengine.google.com/">Google Earth Engine's site</a>.</i>

## Installation
The way this API is usually developed is to first get it working on your local machine and then deploy to a server. Installation on local machine is described first below and then described on a cloud server. 

<i>Before any of the installation instructions below, do the steps above under Authentication in order to get the information needed to populate your privatekey.json.</i>

### Installation on Local Machine
1. Clone this repository
2. cd into repository
3. Start a new virtual environment `python3 -m venv venv`
4. Activate the virtual environment `source venv/bin/activate`
5. Install requirements `pip install -r requirements.txt`
5.b. `pip install earthengine-api --upgrade`
6. cd into flaskproject folder `cd flaskproject`
7. export the flask app like so `export FLASK_APP=app.py` the name of both FLASK_APP and app.py is important. 
8. To run a local flask server run `flask run`.
9. Go to browser url: `http://127.0.0.1:5000/v5000/earth/imagery/?lon=-95.21&lat=29.67&date=2018-01-01&dim=0.32` which calls the imagery endpoint. You should see a view with downtown Houston in upper left and Johnson Space Center in lower right. An example of the exact same view but on a day with more clouds and part of the view outside the satellite track is: `http://127.0.0.1:5000/v5000/earth/imagery/?lon=-95.21&lat=29.67&date=2018-07-01&dim=0.32`


### Installation on AWS EC2
1. Setup your EC2. Your use case might require different number of EC2s of different sizes. We've used an t3-large here. Make sure to set up your security settings such that inbound traffic on https & http is allowed from all IPs! Once you've started your EC2 and logged into it via ssh (AWS has instructions for how to do this), do the following.
2. apt-get update
3. apt-get upgrade
4. sudo apt-get install python3-pip
5. sudo apt-get install python3-venv
6. pip3 install virtualenv
7. sudo apt install apache2
8. sudo apt-get install libapache2-mod-wsgi
9. Establish a ssh key on the EC2 and add it to your settings, you can follow <a href="https://help.github.jp/enterprise/2.11/user/articles/adding-a-new-ssh-key-to-your-github-account/">these</a> instructions.
10. Clone this repository `git clone git@github.com:nasa/earth-imagery-api.git` and then `cd earth-imagery-api/` to go into the top folder. You'll want to start this from the `home/ubuntu/` folder for all the paths to work without changing them!
11. chmod on the entire flaskproject and all contents!! `chmod -R 777 flaskproject/`
12. change into the flaskproject folder `cd flaskproject`
13. set up the virtual environment `. venv/bin/activate` make sure to do this from inside the flaskproject folder!
14. Install all the requirements once inside of the virtual environment: `pip install -r requirements.txt`
15. Double check these are installed `sudo apt-get install apache2 libapache2-mod-wsgi-py3`
16. Double check all the paths in `app.wsgi` and `app.py` are correct!
17. Change directory up one level to `earth-imagery-api` and then run `sudo ln -sT ~/flaskproject /var/www/html/flaskproject`. This will create a symlink from the flaskproject folder to where the website will run from. THIS STEP HAS BEEN PROBLEMATIC BEFORE!!! Another way to do it is to navigate to the `var/www/html/` folder and `run sudo ln -sT /home/ubuntu/earth-imagery-api/flaskproject flaskproject`. If it seems everything should work but the page won't appear when you get down to step 22, come back up here and run the second way. 
18. Enable WSGI by running `sudo a2enmod wsgi`
19. Configure apache (you will need to sudo to edit the file) `sudo vi /etc/apache2/sites-enabled/000-default.conf` Paste this in right after the line with DocumentRoot /var/www/html
```
WSGIDaemonProcess flaskproject threads=5
WSGIScriptAlias / /var/www/html/flaskproject/app.wsgi

<Directory flaskproject>
	WSGIProcessGroup flaskproject
	WSGIApplicationGroup %{GLOBAL}
	Order deny,allow
	Allow from all
</Directory>

```
20. restart apache server `sudo apachectl restart`
21. Check the URL for the page as given by AWS. Make sure you check both the "http" and "https" version as the default .conf page you just edited is probably port 80 for http only!
22. After any change, rerun `sudo apachectl restart`.

##### AWS DEPLOYMENT NOTES
- This repo was originally made to work on AWS by following these instructions: https://vishnut.me/blog/ec2-flask-apache-setup.html . Note that this repository has the earth-imagery-folder on top with flaskproject folder inside it. The example only has a flaskproject folder! 
- Also the following gotches: When you start the API on the AWS EC2 you'll use an apache server instead of the `flask run` step above that was used locally.
- You'll need to modify the security policy to allow all or some IPs to reach it going inboard on http. 


## How to Call the API
You can call this API from <a href="https://api.nasa.gov/">https://api.nasa.gov/</a>. If you go to that site, you'll find a description of how to use the API. An example call is: https://api.nasa.gov/planetary/earth/imagery?lon=100.75&lat=1.5&date=2014-02-01&api_key=DEMO_KEY . Most of the information is also duplicated below:


### Endpoints

#### Api.nasa.gov vs. Native Endpoints in this API

<i>If you build the API yourself, you'll find the endpoint syntax is slightly different than those on api.nasa.gov.</i>

On api.nasa.gov, the endpoints users see are: `planetary/earth/imagery/` and `planetary/earth/assets/`. 

This API itself has endpoints with the syntax: `v5000/earth/imagery/` and `v5000/earth/assets/`


### Queries


#### `/earth`


**Query Fields**

- `date` A date in YYYY-MM-DD format indicating the beginning of the period of the image stack. It will look back 30 days and find the closest date.
- `lat` A float variable that indicates the latitude of the centroid of each image in the image stack.
- `lon` A float variable that indicates the longitude of the centroid of each image in the image stack.
- `dim` The dimension of the square image in degrees (float).
- `size` A string (small, medium, or large) indicating the size in pixels of the returned image.


#### `/assets`


**Query Fields**

- `date` A date in YYYY-MM-DD format indicating the beginning of the period of the image stack. It will look back 30 days and find the closest date.
- `lat` A float variable that indicates the latitude of the centroid of each image in the image stack.
- `lon` A float variable that indicates the longitude of the centroid of each image in the image stack.
- `dim` The dimension of the square image in degrees (float).

**Returned object**

The returned object is a stack of images with the specified location, dimension, and date range.  The keys are the date of acquisition that occurred in the date range and the values are the persistent URLs of the images.

```bash
http://localhost:5000/earth?lon=100.75&lat=1.5&size=large&begin=2014-07-01&end=2014-09-01
```
```jsoniq
{
    2014-08-30: "https://earthengine.googleapis.com//api/thumb?thumbid=e8a750b8ca7d6d2d76181762eb45da70&token=c2b33fc8ec54437cd2c2f33dd04ff1f8",
    2014-07-13: "https://earthengine.googleapis.com//api/thumb?thumbid=80488d566f2c0d75de6839a83a6cbb62&token=35ffce9a1bec82d8ca70a429380b8e4e",
    2014-08-14: "https://earthengine.googleapis.com//api/thumb?thumbid=76c94211a6426a8c00fa5a6a9ef377bc&token=c9f3b543d2fee3892e89fa482f9d8c7c",
    2014-07-29: "https://earthengine.googleapis.com//api/thumb?thumbid=3d301e4eddecd060a59c358371aab26d&token=a3b9105bc8315d1727b96e05d264b239"
}
```

Clicking on the image link for 2014-07-13 yields the following image, which is likely oil palm plantations in Indonesia:

![](http://i.imgur.com/pYVSmjH.png)



## Gotcha's, Pitfalls, and Notes
- Note that the paths in the AWS instructions will change if you use an OS that is not ubuntu!
- EXAMPLE URL DURING LOCAL DEVELOPMENT http://127.0.0.1:5000/v5000/earth/imagery/?lon=-95.21&lat=29.67&date=2018-01-01&dim=0.32
- ALWAYS DEPLOY 'master', if everyting still works, then change 'aws_prod" to "aws_prod_prev" and change "master" to "aws_prod"!s
- DO NOT CHECK YOUR `privatekey_example.json` in with your source code! `privatekey_example.json` is listed in the `.gitignore` file. Please take steps to prevent its accidental release.
