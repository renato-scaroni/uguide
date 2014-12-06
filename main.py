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

import math

import urllib2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Place(ndb.Model):
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    name = ndb.StringProperty()
    city = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class IndexHandler(webapp2.RequestHandler):
    def get(self):
        myLocations = Location()
        cities = myLocations.cities
        template_values = {
            "l" : cities,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Location:
    cities = [("Sao Paulo","sampa"), ("Rio de Janeiro","rio")]

class PlaceSelectionHandler(webapp2.RequestHandler):
    def get(self):
        query = Place.query()
        c = self.request.get("city")
        citiesList = []
        myLocations = Location()
        cities = myLocations.cities
        for city in cities:
            citiesList.append(city[1])
        if c == "":
            c = citiesList[0]

        if c in citiesList:        
            q = query.filter(Place.city == c)
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
            template = JINJA_ENVIRONMENT.get_template('mainPage.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect("/error?type=400")

class RegisterStuff(webapp2.RequestHandler):
    def get(self):
        lat = self.request.get("lat")
        lon = self.request.get("lon")
        name = self.request.get("name")
        city = self.request.get("city")
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.city = city
        place.put()
        self.response.write("Regitered: "+ name + " City: "+ city +" at longitude:"+lon+" and latitude:"+lat)

class ListStuff(webapp2.RequestHandler):
    def get(self):
        query = Place.query()
        s = "Name - Latitude - Longitude <br>"
        for p in query.fetch():
            s += p.name + " , "
            s += str(p.latitude) + " , "
            s += str(p.longitude) + " , "
            s += str(p.city) + "</br>"
        self.response.write(s)



class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'type' : str(self.request.get("type"))
        }
        template = JINJA_ENVIRONMENT.get_template('error.html')
        self.response.write(template.render(template_values))

class MapHandler(webapp2.RequestHandler):

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

    def ordenaWaypoints(self, listaPontos, origem):
        #size = len(self.waypoints)
        size = len(listaPontos)
        print('size = ' + str(size))
        
        distMin = float('Inf')
        index = -1
        for k in range(0,size):
            
            #dist = self.distancia(origem,self.waypoints[k])

            dist = self.distancia(origem,listaPontos[k])

            #print('K = '+str(k))
            #print('nome = '+self.waypoints[k][2])
            #print('distMin = '+str(distMin))
            #print('dist k = '+str(dist))
            
            if (dist < distMin):
                
                print(str(listaPontos[k]))
                index = k
                distMin = dist

        listaPontos[0], listaPontos[index] = listaPontos[index], listaPontos[0]


        #print("depois do primeiro ficou assim:")
        #for w in self.waypoints:
        #    print(str(w[2]))
        #print('-------------------------------')


        for i in range (0,size-1):
            #print("i = "+str(i))
            distMin = float('Inf')
            index = -1
            for j in range (i+1, size):

                dist = self.distancia(listaPontos[i], listaPontos[j])

                if (dist < distMin):
                    index = j
                    distMin = dist

            listaPontos[i+1], listaPontos[index] = listaPontos[index], listaPontos[i+1]

        #print('Depois de tudo ficou assim:')
        #for w in self.waypoints:
            #print(w[2])

        #self.waypoints = listaPontos
        return listaPontos

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

            if len(waypts) > 0:
                waypts = self.ordenaWaypoints(waypts,places[0])
            template_values = {
                'orig' : places[0],
                'waypts' : waypts,
                'dest' : places[-1]
            }
            template = JINJA_ENVIRONMENT.get_template('map.html')
            self.response.write(template.render(template_values))


class Populate(webapp2.RequestHandler):
    def putPlace(self,lat,lon,name,city):
        place = Place()
        place.latitude = lat
        place.longitude = lon
        place.name = name
        place.city = city
        place.put()
    def get(self):
        ###############################################################
        # SP #
        ###############################################################
        #IMEUSP
        self.putPlace(-23.558745,-46.731859,'IMEUSP','sampa')
        #MASP
        self.putPlace(-23.561518,-46.656009,'MASP','sampa' )
        #Shopping Eldorado
        self.putPlace(-23.572742,-46.696095,'Shopping Eldorado','sampa')
        #HU
        self.putPlace(-23.564588,-46.739655,'HU','sampa')
        #Teatro Municipal SP
        self.putPlace(-23.545166, -46.638218,'Teatro Municipal de Sao Paulo','sampa')
        #Pinacoteca
        self.putPlace(-23.534208, -46.633228,'Pinacoteca de Sao Paulo','sampa')
        #Ibirapuera
        self.putPlace(-23.587426, -46.657205,'Parque do Ibirapuera','sampa')
        #Museu L.P.
        self.putPlace(-23.535016, -46.634672,'Museu da Lingua Portuguesa','sampa')
        #Jd Botanico SP
        self.putPlace(-23.641802, -46.620280,'Jardim Botanico de Sao Paulo','sampa')
        #Parque Villa Lobos
        self.putPlace(-23.547737, -46.723836,'Parque Villa Lobos','sampa')
        #Museu Paulista
        self.putPlace(-23.585440, -46.608956,'Museu Paulista','sampa')
        #Catedral da Se
        self.putPlace(-23.551339, -46.633914,'Catedral da Se','sampa')
        ###############################################################
        # RIO #
        ###############################################################
        #Pao de acucar
        self.putPlace(-22.948721, -43.155117,'Pao de Acucar','rio')
        #Teatro Municipal Rio
        self.putPlace(-22.908979, -43.175882,'Teatro Municipal do Rio','rio')
        #Cristo
        self.putPlace(-22.951304, -43.210759,'Cristo Redentor','rio')
        #Maracana
        self.putPlace(-22.912168, -43.229856,'Maracana','rio')
        #Ipanema
        self.putPlace(-22.986575, -43.202208,'Praia de Ipanema','rio')
        self.response.write("Ok")

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

class Test(Singleton):
    getDomainForm = "<!DOCTYPE html> <html> <body> <form action='/test' method='post'> Domain:<br> <input type='text' name='domain'> <br><br> <input type='submit' value='Submit'></form></body> </html>"
    domain = ""
    def SetDomain(self, dom):
        self.domain = dom
    def GetDomain(self):
        return self.domain
    def GetDomainForm(self):
        return self.getDomainForm

class TestMainHandler(webapp2.RequestHandler):
    def get(self):
        if Test().GetDomain() == "":
            self.response.write(Test().GetDomainForm())
        else:
            tests = UnitTests()

            s = "Should break /map : " + tests.ShouldReturnError_MAP() + "<br>"
            s += "Should access main page : " + tests.ShouldAccessMainPage()
            self.response.write(s)

    def post(self):
        domain = self.request.get("domain")
        Test().SetDomain(domain)
        self.redirect("/test")

class UnitTests():
    def ShouldReturnError_MAP(self):
        try:
            r = urllib2.urlopen(Test().GetDomain()+"/map")
            return "Not OK";
        except urllib2.HTTPError as e:
            return "OK"

    def ShouldAccessMainPage(self):
        try:
            r = urllib2.urlopen(Test().GetDomain())
            return "OK";
        except urllib2.HTTPError as e:
            return "Not OK - error " + str(e.code)

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/place', PlaceSelectionHandler),
    ('/map', MapHandler),
    ('/register', RegisterStuff),
    ('/list', ListStuff),
    ('/populate', Populate),
    ('/error', ErrorHandler),
    ('/test', TestMainHandler)
], debug=True)
