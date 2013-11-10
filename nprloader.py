# This file is used to parse the JSON output
# that is returned from NPR requests. This file
# exists so that main.py doesn't have to deal at 
# with json

import json
import urllib2

def loadTopics():
	topics = {}

	# get all the current topics from NPR's API
	response = urllib2.urlopen('http://api.npr.org/list?id=3002&output=json')
	
	# load the json response
	js = json.load(response)

	# grab each topic from the resopnse and map its
	# name to its id in the topics dictionary
	for topic in js['item']:
		topics[topic['title']['$text']] = topic["id"]
	return topics


def loadStories(topic_id, URL):
	stories = {}

	# get the topic
	response = urllib2.urlopen(URL+'&id='+topic_id)
	js = json.load(response)

	# grab each story title from the given
	for story in js['list']['story']:
		stories[story['title']['$text']] = story['id']
	return stories

def loadStory(story_id, URL):
	paragraphs = []

	# get the story
	response = urllib2.urlopen(URL+'&id='+story_id)
	js = json.load(response)

	# make sure the story has text in it
	if 'text' in js['list']['story'][0]:

		# some stories just plain don't work, they don't recognize the ['$text'] key
		# (even though I've seen the dict and it's definitely there), so we need to
		# catch this exception
		try:

			# grab each paragraph in the returned story
			for p in js['list']['story'][0]['text']['paragraph']: #list, story, text, paragraph, $text
				paragraphs.append(p['$text'])
			return paragraphs

		except KeyError as e:
			return False

	elif 'teaser' in js['list']['story'][0]:
		paragraphs.append(js['list']['story'][0]['teaser']['$text'])
		return paragraphs
	else:
		return ['Story: '+js['list']['story']['title']['$text']+' has no text transcription.']

def loadStoryThings(story_id, URL):
	things = {}

	#get the story
	response = urllib2.urlopen(URL+'&id='+story_id)
	js = json.load(response)

	story_things = js['list']['story']

	#check for/grab url
	if 'link' in story_things:
		#check for html url
		for link in story_things['link']:
			if link['type'] == 'html':
				things['link'] = link['$text']

	if 'title' in story_things:
		things['title'] = story_things['title']['$text']

	if 'teaser' in story_things:
		things['teaser'] = story_things['teaser']['$text']

	if 'pubDate' in story_things:
		things['pubDate'] = story_things['pubDate']['$text']

	if 'thumbnail' in story_things:
		if 'large' in story_things['thumbnail']:
			things['image'] = story_things['thumbnail']['large']['$text']

	if 'byline' in story_things:
		if 'name' in story_things['byline']:
			things['author'] = story_things['byline']['name']['$text']

	return story_things



