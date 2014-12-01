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

import math

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

    def defineWaypoints(self) :
        self.waypoints = [
            (-23.557265, -46.660883, 'Estacao Consolacao'),
            (-23.572742, -46.696095, 'Shopping Eldorado'), 
            (-23.564588, -46.739655, 'HU'), 
            (-23.567349, -46.692782, 'Estacao Faria Lima'), 
            (-23.571875, -46.707365, 'Estacao Butanta')
            ]


    def rad(self, x):
        return x*math.pi/(180)

    def distancia(self, p1, p2):
        R = 6378137
        dLat = self.rad(p2[0] - p1[0])
        dLong = self.rad(p2[1] - p1[1])
        a = math.sin(dLat/2)*math.sin(dLat/2) + math.cos(self.rad(p1[0])) * math.cos(self.rad(p2[0])) * math.sin(dLong / 2) * math.sin(dLong / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c;
        return d 
    
    def ordenaWaypoints(self, origem):
        size = len(self.waypoints)
        print('size = ' + str(size))
        
        distMin = float('Inf')
        index = -1
        for k in range(0,size):
            
            dist = self.distancia(origem,self.waypoints[k])

            #print('K = '+str(k))
            #print('nome = '+self.waypoints[k][2])
            #print('distMin = '+str(distMin))
            #print('dist k = '+str(dist))
            
            if (dist < distMin):
                
                print(str(self.waypoints[k]))
                index = k
                distMin = dist

        self.waypoints[0], self.waypoints[index] = self.waypoints[index], self.waypoints[0] 

        #print("depois do primeiro ficou assim:")
        #for w in self.waypoints:
        #    print(str(w[2]))
        #print('-------------------------------')


        for i in range (0,size-1):
            #print("i = "+str(i))
            distMin = float('Inf')
            index = -1
            for j in range (i+1, size):

                dist = self.distancia(self.waypoints[i], self.waypoints[j])

                if (dist < distMin):
                    index = j
                    distMin = dist

            self.waypoints[i+1], self.waypoints[index] = self.waypoints[index], self.waypoints[i+1]

        #print('Depois de tudo ficou assim:')
        #for w in self.waypoints:
            #print(w[2])


    def get(self):

        self.defineWaypoints()
        self.ordenaWaypoints((-23.558745, -46.731859, 'IMEUSP'))

        #for w in self.waypoints:
         #   print(w[2])

        template_values = {
            'orig' : (-23.558745, -46.731859, 'IMEUSP') ,
            'waypts' : self.waypoints,
            'dest' : (-23.561518, -46.656009, 'MASP')
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class RegisterStuff(webapp2.RequestHandler):
    def get(self):

        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))
        name = str(self.request.get("name"))

        lat = self.request.get("lat")
        lon = self.request.get("lon")
        name = self.request.get("name")

        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()

        self.response.write("Regitered "+ name + " at longitude:"+str(lon)+" and latitude:"+str(lat))

        self.response.write("Regitered "+ name + " at longitude:"+lon+" and latitude:"+lat)

class ListStuff(webapp2.RequestHandler):
    def get(self):
        query = Place.query()
        s = "Name - Latitude - Longitude <br>"
        for p in query.fetch(50):
            s += p.name + " , "
            s += str(p.latitude) + " , "
            s += str(p.longitude) + "<br>"
        self.response.write(s)

class MapHandler(webapp2.RequestHandler):
    def post(self):
        resp = cgi.escape(self.request.get('locations'))
        self.response.write(resp)

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
        resp = str (self.request.get("locations"))
        self.response.write(cgi.escape(resp))

class Populate(webapp2.RequestHandler):
    
    def putPlace(self,lat,lon,name):
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.put()

    def get(self):
        ###############################################################
        #                           SP                                # 
        ###############################################################

        #IMEUSP
        self.putPlace(-23.558745,-46.731859,'IMEUSP')
        #MASP
        self.putPlace(-23.561518,-46.656009,'MASP')
        #Shopping Eldorado
        self.putPlace(-23.572742,-46.696095,'Shopping Eldorado')
        #HU
        self.putPlace(-23.564588,-46.739655,'HU')
        #Teatro Municipal SP
        self.putPlace(-23.545166, -46.638218,'Teatro Municipal de Sao Paulo')
        #Pinacoteca
        self.putPlace(-23.534208, -46.633228,'Pinacoteca de Sao Paulo')
        #Ibirapuera
        self.putPlace(-23.587426, -46.657205,'Parque do Ibirapuera')
        #Museu L.P.
        self.putPlace(-23.535016, -46.634672,'Museu da Lingua Portuguesa')
        #Jd Botanico SP
        self.putPlace(-23.641802, -46.620280,'Jardim Botanico de Sao Paulo')
        #Parque Villa Lobos
        self.putPlace(-23.547737, -46.723836,'Parque Villa Lobos')
        #Museu Paulista
        self.putPlace(-23.585440, -46.608956,'Museu Paulista')
        #Catedral da Se
        self.putPlace(-23.551339, -46.633914,'Catedral da Se')

        ###############################################################
        #                           RIO                               # 
        ###############################################################
        #Pao de acucar
        self.putPlace(-22.948721, -43.155117,'Pao de Acucar')
        #Teatro Municipal Rio
        self.putPlace(-22.908979, -43.175882,'Teatro Municipal do Rio')
        #Cristo
        self.putPlace(-22.951304, -43.210759,'Cristo Redentor')
        #Maracana
        self.putPlace(-22.912168, -43.229856,'Maracana')
        #Ipanema
        self.putPlace(-22.986575, -43.202208,'Praia de Ipanema')
        self.response.write("Ok")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/map', MapHandler),
    ('/register', RegisterStuff),
    ('/list', ListStuff),
    ('/populate', Populate),
    ('/error', ErrorHandler)
], debug=True)
