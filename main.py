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
import os, urllib, time, itertools, logging

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2

FILENAME = 'tweets.txt'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def isa_group_separator(line):
	return line=='\n'

DATA_PATH = 'data/'

def group_key(group_name):
	return ndb.Key('TweetKeywordGroup', group_name)

class Tweet(ndb.Model):
	username = ndb.StringProperty(indexed=False)
	screenname = ndb.StringProperty(indexed=False)
	text = ndb.StringProperty(indexed=False)
	longitude = ndb.FloatProperty()
	latitude = ndb.FloatProperty()

class MainHandler(webapp2.RequestHandler):

	def get(self):
		#query the keyword, resultant array is coordinates[]
		submitted_keyword = self.request.get('keyword')
		logging.debug('keyword: '+ submitted_keyword)

		coordinates = []
		if not (submitted_keyword == ""):
			coordinates = memcache.get(submitted_keyword)
			if coordinates is None:
				logging.debug('cache miss!')
				tweet_query = Tweet.query(ancestor=group_key(submitted_keyword))
				tweets = tweet_query.fetch()
				coordinates = []
				for item in tweets:
					coordinate = []
					coordinate.append(item.longitude)
					coordinate.append(item.latitude)
					coordinates.append(coordinate)
				memcache.add(submitted_keyword, coordinates)
			else:
				logging.debug('cache hit!')
			#logging.debug('first longitude: ' + str(coordinates[0][0]))
			logging.debug(coordinates)
			logging.debug( len(coordinates))

		template_values = {
				'coordinates': coordinates,
            	
        }

		template = JINJA_ENVIRONMENT.get_template('index2.html')
		self.response.write(template.render(template_values))


class TweetStore(webapp2.RequestHandler):

	def get(self):

		for data_file in os.listdir(DATA_PATH):
			keyword_group_name = data_file
			list_of_tweets = []
			with open(DATA_PATH+keyword_group_name, 'r') as fp:
				for key,group in itertools.groupby(fp, isa_group_separator):
					#print(key, list(group))
					if not key:
						tweet = Tweet(parent=group_key(keyword_group_name))
						for item in group:
							field,value = item.split('=:')
							value = value.strip()
							#print field + '!!!!!!' + value
							if field == 'username':
								tweet.username = value
							elif field == 'screenname':
								tweet.screenname = value
							elif field == 'text':
								tweet.text = value
							elif field == 'longitude':
								tweet.longitude = float(value)
							elif field == 'latitude':
								tweet.latitude = float(value)
							else:
								self.redirect('/?error=1')
						list_of_tweets.append(tweet)
			ndb.put_multi(list_of_tweets)

			#tweet.put() #comment this line and uncomment last 2 lines to upload the entire file
		self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/savedata',TweetStore),
], debug=True)
