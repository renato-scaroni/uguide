#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Place(ndb.Model):
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        query = Place.query()
        q = query.fetch(10)
        places = []
        s = ""
        for p in q:
            places.append(p.name)
            s += p.name + " , "
            s += str(p.latitude) + " , "
            s += str(p.longitude) + "<br>"

        template_values = {
            'places' : places,
            'placesString' : s
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class RegisterStuff(webapp2.RequestHandler):
    def get(self):
        lat = self.request.get("lat")
        lon = self.request.get("lon")
        name = self.request.get("name")
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        self.response.write("Regitered "+ name + " at longitude:"+lon+" and latitude:"+lat)

class ListStuff(webapp2.RequestHandler):
    def get(self):
        query = Place.query()
        s = "Name - Latitude - Longitude <br>"
        for p in query.fetch(10):
            s += p.name + " , "
            s += str(p.latitude) + " , "
            s += str(p.longitude) + "<br>"
        self.response.write(s)



class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'type' : str(self.request.get("type"))
        }
        template = JINJA_ENVIRONMENT.get_template('error.html')
        self.response.write(template.render(template_values))

class MapHandler(webapp2.RequestHandler):
    def getPlaces(self, l):
        places = []
        q = Place.query()
        for p in l:
            if not (p == ''):
                q2 = q.filter(Place.name == p)
                places.append((q2.fetch()[0].latitude, q2.fetch()[0].longitude, p))
        return places

    def post(self):
        req = str (self.request.get("locations"))
        places = self.getPlaces(req.split('\t'))
        waypts = []

        if(len(places) < 2):
            self.redirect("/error?type=400")
        else:
            for i in range(1, len(places)-1):
                waypts.append(places[i])

            template_values = {
                'orig' : places[0],
                'waypts' : waypts,
                'dest' : places[-1]
            }
            template = JINJA_ENVIRONMENT.get_template('map.html')
            self.response.write(template.render(template_values))

class Populate(webapp2.RequestHandler):
    def get(self):
        lat = -23.558745
        lon = -46.731859
        name = 'IMEUSP'
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        lat = -23.561518
        lon = -46.656009
        name = 'MASP'
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        lat = -23.572742
        lon = -46.696095
        name = 'ELDORADO'
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        self.response.write("Populated")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/map', MapHandler),
    ('/register', RegisterStuff),
    ('/list', ListStuff),
    ('/populate', Populate),
    ('/error', ErrorHandler)
], debug=True)
