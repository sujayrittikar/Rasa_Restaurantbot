# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import ast
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction

#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

class BingLocation:

	def __init__(self):
		self.baseurl = "http://dev.virtualearth.net/REST/v1/Locations"
		self.bing_key = "Use your Bing API Key"

	def getLocationInfo(self, query, tracker):

		list_cities = []
		queryString = {
			"query": query,
			"key": self.bing_key
		}

		result = requests.get(self.baseurl, params= queryString)

		if result.ok is False:
			return None, None
		else:
			data = result.json()
			print(data)
			if "locality" in data["resourceSets"][0]["resources"][0]["address"]:
				return data["resourceSets"][0]["resources"][0]["address"]["locality"], data["resourceSets"][0]["resources"][0]["name"]
			else:
				return data["resourceSets"][0]["resources"][0]["name"]


class SetLocation(Action):

	def name(self):
		return "action_set_location"

	def run(self, dispatcher, tracker, domain):
		user_input = tracker.latest_message['text']

		r = BingLocation()
		locality, location_name = r.getLocationInfo(str(user_input), tracker)

		dispatcher.utter_message(template="I've got your location: " + locality.capitalize())
		return [SlotSet("location", location_name)]


class Zomato:

	def __init__(self):
		self.baseurl = "https://developers.zomato.com/api/v2.1/"
		self.key = "Use your Zomato API Key"

	def getId(self, location):
		location_info = []

		queryString = {"query": location}
		headers = {'Accept': 'application/json', 'user-key': self.key}
		result = requests.get(self.baseurl + "locations", params = queryString, headers=headers)

		if result.ok is False:
			raise Exception('Invalid_location')

		else:
			data = result.json()
			location_info.append(data["location_suggestions"][0]["latitude"])
			location_info.append(data["location_suggestions"][0]["longitude"])
			location_info.append(data["location_suggestions"][0]["entity_id"])
			location_info.append(data["location_suggestions"][0]["entity_type"])
			return location_info


	def cuisines(self, location):

		headers = {'Accept': 'application/json', 'user-key': self.key}

		queryString = {
			"lat": location[0],
			"lon": location[1]
		}

		result = requests.get(self.baseurl + "cuisines", params=queryString, headers=headers).content.decode("utf-8")

		a = ast.literal_eval(result)
		all_cuisines = a['cuisines']

		res = {}

		for x in all_cuisines:
			i = x['cuisine']
			res[i['cuisine_name'].lower()] = i['cuisine_id']

		return res

	def cuisineId(self, cuisine, location):
		cuisines = self.cuisines(location)
		return cuisines[cuisine.lower()]

	def getRestaurants(self, location, cuisine):

		location = self.getId(location)
		cuisine_id = self.cuisineId(cuisine, location)

		queryString = {
			"entity_type": location[3],
			"entity_id": location[2],
			"cuisines": cuisine_id,
			"sort": "rating",
			"count": 3
		}

		headers = {'Accept': 'application/json', 'user-key': self.key}
		result = requests.get(self.baseurl + "search", params=queryString, headers=headers)

		all_restaurants = result.json()["restaurants"]

		l = []

		for x in all_restaurants:
			name = x["restaurant"]["name"]
			url = x["restaurant"]["url"]
			l.append(name)
			l.append(url)

		return l

	def getDefaultRestaurants(self, location):
		
		loc = self.getId(location)
		queryString = {
			"entity_id": loc[2],
			"entity_type": loc[3],
			"sort": "rating",
			"count": 3
		}

		headers = {'Accept': 'application/json', 'user-key': self.key}
		response = requests.get(self.baseurl + "search", params=queryString, headers=headers)

		x = []
		if response.ok is True:
			l = response.json()["restaurants"]
			for i in l:
				name = i["restaurant"]["name"]
				url = i["restaurant"]["url"]
				x.append(name)
				x.append(url)
		return x

class ActionShowRestaurants(Action):

	def name(self):
		return "action_show_restaurants"

	def run(self, dispatcher, tracker, domain):

		user_input = tracker.latest_message['text']

		z = Zomato()
		loc = BingLocation()
		location = tracker.get_slot('location')

		if not location:
			locality, location_name = loc.getLocationInfo(str(user_input), tracker)

		if not location:
			dispatcher.utter_template(template='utter_ask_location', tracker=tracker)
		else:
			cuisine_type = tracker.get_slot('cuisine')
			restaurantlist = z.getRestaurants(location=location, cuisine=str(cuisine_type))

			response = ""
			if restaurantlist:
				print(restaurantlist)
				for i in range(0, len(restaurantlist), 2):
					if i==len(restaurantlist):
						break
					
					response += restaurantlist[i]
					response += "\n" + restaurantlist[i+1]
					response += "\n"				
				print(response)	
				dispatcher.utter_template('utter_restaurants', tracker= tracker, response=response)

			else:
				dispatcher.utter_message(template= "I'm sorry, couldn't find restaurants." )

			return []

class ActionDefaultRestaurants(Action):

	def name(self):
		return "action_default_restaurants"

	def run(self, dispatcher, tracker, domain):
		location = tracker.get_slot('location')

		z = Zomato()

		l = z.getDefaultRestaurants(str(location))

		if l:
			response = ""
			for i in range(0, len(l), 2):
				if i==len(l):
					break
				response += l[i]
				response += "\n" + l[i+1]
				response += "\n"
			print(response)
			dispatcher.utter_template('utter_restaurants_noCuisine', tracker=tracker, response=response)
		else:
			dispatcher.utter_message(template= "I'm sorry, couldn't find restaurants." )

		return []
