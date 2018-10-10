import google_maps_service

#TODO - Load the user-data from dynamoDB just when a session starts and not each time (maybe on launch) + greet the user
#TODO - Keep the welcome message short and use the help intent to introduce/present the intents
#TODO - Add more intents(currently it's fixed to "TRANSIT") and matching utterances:
# 1) Request: When is my next train (to work) - Response: Your next transit(Train?/generic term) to Destination is at 9:40pm
# 2) Request: How do I get from X to Y (optional at time Z) (optional mode - by default it's transit) - Response: similar response to 2)
#TODO - support (much) more utterances
#TODO - clean up
#TODO - some more utterances

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response(session_attributes):
    # """ If we wanted to initialize the session to have some attributes we could
    # add those here
    # """
    card_title = "Welcome"
    speech_output = "You could ask me questions like:" \
    "How do I get from address to address at time?" \
    "You can also set a default source or destination address by saying: " \
    "Set default source address to: address" \
    "If you have set your default source and destination addresses then you can ask:" \
    "When is my next train?" \
    "You could also ask: what are my directions?" \
    "The response would be directions for your default route and with the requested depart-time of now"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you would like to do?" \
                    "You can ask me to:" \
                    "Set default source or destination address to address" \
                    "When is my next train?" \
                    "What are my directions?" \
                    "How do I get from address to address at time?" \
                    "for example: how do I get from Crystal Palace to London Bridge at 7 p.m. (or now)"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Direct me. " \
                    "Have a nice day! "
    session_attributes = {} # we can bin the existing attributes
    should_end_session = True # Setting this to true ends the session and exits the skill.
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_fallback_response(session_attributes):
    reprompt_text = None
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        "oh no :(", "I didn't understand what you mean, please try again", reprompt_text, should_end_session))

#TODO - consider setting the source and target destination in the same intent (if not in the same intent - then probably I should common out the logic ( it's t-o-o similar))
def set_default_source_address(intent, session_attributes):
    card_title = intent['name']
    should_end_session = False

    if 'address' in intent['slots'] and 'value' in intent['slots']['address']:
        source_address = intent['slots']['address']['value']
        set_source_address(source_address, session_attributes)
        speech_output = "I now know your default source address is " + source_address
        reprompt_text = None #TODO - maybe we should add here some message
    else:
        speech_output = "I'm not sure what your default source address is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your default source address is. " \
                        "You can tell me your default source address by saying, " \
                        "Set default source address to address."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#TODO - consider setting the source and target destination in the same intent (if not in the same intent - then probably I should common out the logic ( it's t-o-o similar))
def set_default_destination_address(intent, session_attributes):
    card_title = intent['name']
    should_end_session = False

    if 'address' in intent['slots'] and 'value' in intent['slots']['address']:
        destination_address = intent['slots']['address']['value']
        set_destination_address(destination_address, session_attributes)
        speech_output = "I now know your default destination address is " + destination_address
        reprompt_text = None #TODO - maybe we should add some message
    else:
        speech_output = "I'm not sure what your default destination address is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your default destination address is. " \
                        "You can tell me your default destination address by saying, " \
                        "Set default destination address to address."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#TODO - store it in dynamoDB
def set_source_address(source_address, session_attributes):
    session_attributes["source_address"] = source_address

#TODO - store it in dynamoDB
def set_destination_address(destination_address, session_attributes):
    session_attributes["destination_address"] = destination_address

def fetch_or_create_attributes(session):
    return session.get("attributes", {})

def get_default_source_address(session_attributes):
    #TODO - revise it, since I'm likely to load the DB on startup regardless of that call, meaning the data should already be on the session if the user set it before. need to make sure that the user enters it before
    if "source_address" in session_attributes:
        return session_attributes["source_address"]

    return None

def get_default_destination_address(session_attributes):
    #TODO - revise it, since I'm likely to load the DB on startup regardless of that call, meaning the data should already be on the session if the user set it before. need to make sure that the user enters it before
    if "destination_address" in session_attributes:
        return session_attributes["destination_address"]

    return None

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    session_attributes = {}; #TODO - should load the details from dynamoDB to the session
    return get_welcome_response(session_attributes)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent['name']
    session_attributes = fetch_or_create_attributes(session)
    # Dispatch to your skill's intent handlers
    if intent_name == "SetSourceAddressIntent":
        return set_default_source_address(intent, session_attributes)
    elif intent_name == "SetDestinationAddressIntent":
        return set_default_destination_address(intent, session_attributes)
    elif intent_name == "DefaultRouteDirectionsIntent":
        #TODO - some validation on the inputs is needed + make sure it's in a legal state for exectuion (if user hasn't set the src/dest before - we should say that he didn't set it, if he did we would fetch it and it would already be loaded to the session
        src_address = get_default_source_address(session_attributes)
        dst_address = get_default_destination_address(session_attributes)
        card_title = "Default Itinerary"
        reprompt_text = None
        if (src_address == None or dst_address == None):
            should_finish = False
            return build_response(session_attributes, build_speechlet_response(card_title, "Default source or destination address isn't set. Please set both addresses before asking directions to your defult route", reprompt_text, should_finish))
        else:
            should_finish = True
            return build_response(session_attributes, build_speechlet_response(card_title, google_maps_service.get_directions(src_address, dst_address), reprompt_text, should_finish))
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(session_attributes)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "AMAZON.FallbackIntent":
        return get_fallback_response(session_attributes)

    # TODO - should complete it: NavigateHomeIntent
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
