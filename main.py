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
import os
import webapp2
import jinja2
import urllib2
import nprloader
from google.appengine.ext import db

API_KEY = 'MDExOTMyODk5MDEzNzU5MzYzODhkNTkzOQ001'
JINJA_ENV = jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
URL = 'http://api.npr.org/query?apikey=' + API_KEY
URL += '&format=json&reuquiredAssets=text'
TOPICS = nprloader.loadTopics()



class Visitor(db.Model):
	name = db.StringProperty(required = True)
	topic = db.StringProperty(required = True)
	visited = db.DateTimeProperty(auto_now_add = True)

template_values = {
	'user' : 'Visitor',
	"options" : TOPICS,
	'visitors' : db.GqlQuery("SELECT * FROM Visitor ORDER BY visited DESC"),
	'last_user' : ""
}

class MainHandler(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENV.get_template('index.html')
		self.response.out.write(template.render(template_values))

	def post(self):
		topic_name = self.request.get('topic_name')
		user = self.request.get('user')
		if(user):
			# add a new visitor to the DB
			v = Visitor(name = user, topic= topic_name)
			v.put()
			template_values['last_user'] = user
		topic_name = topic_name.replace('&', '%26')
		self.redirect('/stories?topic=' + topic_name + '&user=' + template_values['user'])

class StoryPickHandler(webapp2.RequestHandler):
	def get(self):
		topic = self.request.get('topic')
		self.response.out.write(topic)
		stories = nprloader.loadStories(TOPICS[topic], URL)

		template_vals = {
			"user" : template_values['last_user'],
			"topic" : topic,
			'stories' : stories
		}
		if template_vals['user'] == '':
			template_vals['user'] = template_values['user']
		template = JINJA_ENV.get_template('stories.html')
		self.response.out.write(template.render(template_vals))

	def post(self):
		topic = self.request.get('topic')
		stories = nprloader.loadStories(TOPICS[topic], URL)
		story = self.request.get('story')
		try:
			story_id = stories[story]
			self.redirect('/story?id='+story_id)
		except KeyError as e:
			self.response.out.write("<p>Sorry, NPR is telling me that story doesn't exist anymore! (according to its response)</p>"+
									"<p>However, if you wanted to check that for yourself, I would start <a href='http://www.google.com/?q=NPR%20"+story+"'>here</a>")

class StoryHandler(webapp2.RequestHandler):
	def get(self):
		story_id = self.request.get('id')
		story_text = nprloader.loadStory(story_id, URL)
		story_things = nprloader.loadStoryThings(story_id, URL)
		template_vals = {
			'story_cont' : story_text,
			'story' : story_id,
			'things' : story_things
		}
		template = JINJA_ENV.get_template('story.html')
		if (not story_text):
			if 'fullText' in story_things[0]:
				self.response.out.write(story_things[0]['fullText']['$text'])
			else: 
				for p in story_things[0]['text']['paragraph']:
					if ('$text' in p):
						self.response.out.write("<p>"+p['$text']+"</p>")
		try:
			self.response.out.write(template.render(template_vals))
		except TypeError as e:
			if(story_text):
				self.response.out.write(story_things[0]['fullText']['$text'])


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/stories', StoryPickHandler),
    ('/story', StoryHandler)
], debug=True)
