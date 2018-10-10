import os
import googlemaps
from datetime import datetime

MAPS_CLIENT = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_KEY"))

def get_directions(from_address, to_address, mode = "transit", departure_time = datetime.now()):
    directions_response = MAPS_CLIENT.directions(from_address, to_address, mode = mode, departure_time = departure_time)
    #by defult returns a single route - probably I would like to use alternatives=true and pick the one which would arrive first
    return create_textual_directions_response(directions_response)

#TODO - extract string literls to constants
def create_textual_directions_response(directions_response):
    if (len(directions_response) == 0):
        return "I'm sorry but I didn't find a route between the requested source and destination."

    route = directions_response[0] # TODO - not convinced that the single returned route is the "first arrival", usually it would just be the shortest time but could still arrive later
    leg = route["legs"][0] # currently decided to allow only one leg - "from A to B"

    response_text_arr = []
    for step in leg["steps"]:
        if step["travel_mode"] == "TRANSIT":
            transit_details = step["transit_details"]
            departure_stop = transit_details["departure_stop"]["name"]
            departure_time = transit_details["departure_time"]["text"]
            arrival_stop = transit_details["arrival_stop"]["name"]
            line = transit_details["line"]
            if "short_name" in line: # unfortunately it's not always there (e.g. for Subway/Tube)
                line_name = line["short_name"]
            else:
                #TODO - double check that line data isn't available at all, we aren't showing which line it is - some Tube stations has 6 lines :/
                line_name = line["vehicle"]["name"]

            response_text_arr.append(line_name + " from " + departure_stop + " at " + departure_time + " to " + arrival_stop + ",\n")
        else:
            response_text_arr.append(step["html_instructions"] + ",\n")

    return ''.join(response_text_arr)
