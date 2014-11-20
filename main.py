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
import cgi

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
        template_values = {
            'orig' : (-23.558745, -46.731859, 'IMEUSP') ,
            'waypts' : [(-23.572742, -46.696095, 'Shopping Eldorado'), (-23.564588, -46.739655, 'HU')],
            'dest' : (-23.561518, -46.656009, 'MASP')
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class RegisterStuff(webapp2.RequestHandler):
    def get(self):
        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))
        name = str(self.request.get("name"))
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        self.response.write("Regitered "+ name + " at longitude:"+str(lon)+" and latitude:"+str(lat))

class ListStuff(webapp2.RequestHandler):
    def get(self):
        query = Place.query()
        s = "Name - Latitude - Longitude <br>"
        for p in query.fetch(10):
            s += p.name + " , "
            s += str(p.latitude) + " , "
            s += str(p.longitude) + "<br>"
        self.response.write(s)

class MapHandler(webapp2.RequestHandler):
    def post(self):
        resp = cgi.escape(self.request.get('locations'))
        self.response.write(resp)

class RandomTest(webapp2.RequestHandler):
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
        name = 'Shopping Eldorado'
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        lat = -23.564588
        lon = -46.739655
        name = 'HU'
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()
        self.response.write("Ok")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/register', RegisterStuff),
    ('/list', ListStuff),
    ('/random', RandomTest),
    ('/map', MapHandler)
], debug=True)
