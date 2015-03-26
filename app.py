from flask import Flask, request
import requests
import twilio.twiml

CLIENT_ID = ""
CLIENT_SECRET = ""

app = Flask(__name__)

def has_menu(venue):
	return 'hasMenu' in venue

def get_menu(restaurant_name):
	text_response = ''
	r = requests.get("https://api.foursquare.com/v2/venues/search?client_id={0}&client_secret={1}&v=20130815&near=Toronto, ON&query={2}".format(CLIENT_ID, CLIENT_SECRET, restaurant_name))
	venues = r.json()['response']['venues'][:]

	if len(venues) == 0:
		text_response += "No venues found. Please try another search!"

	elif len(venues) == 1:
		venue = venues[0]

		if has_menu(venue):
			venue_id = venue['id']
			full_venue_object = requests.get("https://api.foursquare.com/v2/venues/{0}?client_id={1}&client_secret={2}&v=20130815&near=Toronto, ON".format(venue_id, CLIENT_ID, CLIENT_SECRET)).json()['response']['venue']
			foursquare_url = full_venue_object['shortUrl']
			text_response = "{0} Menu: {1}, Foursquare Link: {2}".format(venue['name'], venue['menu']['mobileUrl'], foursquare_url)

		elif not has_menu(venue):
			text_response = "{0} doesn't have a menu on Foursquare. Sorry!".format(venue['name'])

	elif len(venues) > 1: #multiple options
		# show only restaurants with menus
		text_response += "Listed below are venues that matched your search query and their respective menus.\n"
		for venue in venues:
			venue_id = venue['id']

			if has_menu(venue):
				full_venue_object = requests.get("https://api.foursquare.com/v2/venues/{0}?client_id={1}&client_secret={2}&v=20130815&near=Toronto, ON".format(venue_id, CLIENT_ID, CLIENT_SECRET)).json()['response']['venue']
				foursquare_url = full_venue_object['shortUrl']
				text_response += "\n{0} Menu: {1}, Foursquare Link: {2}\n".format(venue['name'], venue['menu']['mobileUrl'], foursquare_url)

	return text_response

@app.route("/", methods=["GET", "POST"])
def root():
	venue_query = request.values.get('Body', None)
	resp = twilio.twiml.Response()
	resp.message(get_menu(venue_query))
	return str(resp)

if __name__ == '__main__':
	app.run(debug=True)