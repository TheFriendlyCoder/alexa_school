# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

import os
from ask_sdk_s3.adapter import S3Adapter

s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from schedule_parser import ScheduleParser, SCHEDULE_URL
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # logging.info("Kevin Was Here")

        attr = handler_input.attributes_manager.persistent_attributes
        if "district" in attr:
            speak_output = f"I see you are from school district {attr['district']}"
        else:
            speak_output = "Welcome to the local schools app. How can I help you today?"
        # district_name = "FREDERICTON"
        # school_name = "École des Bâtisseurs"
        # text = requests.get(SCHEDULE_URL).text
        # obj = ScheduleParser(text)
        # d = obj.get_district(district_name)
        # s = d.get_school(school_name)
        # if s.is_open:
        #     speak_output = f"School {s.name} is open"
        # else:
        #     speak_output = f"School {s.name} is closed"
        # speak_output = "I hear you Kevin"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CaptureDistrictIntentHandler(AbstractRequestHandler):
    """Handler for getting the school district."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureDistrictIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        in_district = slots["district"].value

        # TODO: when loading URL data, cache it in the app and put a timeout on the requests call
        #       if the request times out, fall back to the cached copy
        # TODO: put an expriation on the cached data, and warn the user the data may be out of date
        src_data = ScheduleParser(requests.get(SCHEDULE_URL).text)
        district = None
        for cur_dist in src_data.districts:
            if cur_dist.name.lower() == in_district.lower():
                district = cur_dist
                break

        if not district:
            speak_output = f"I'm sorry but district {in_district} is not currently supported."
        else:
            speak_output = f"Thanks. I see you are in district {district.name} which has {len(district.schools)} "
            if len(district.schools) == 1:
                speak_output += "school in it."
            else:
                speak_output += "schools in it."

            attributes_manager = handler_input.attributes_manager
            attributes_manager.persistent_attributes = {"district": district.name}
            attributes_manager.save_persistent_attributes()

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class SchoolsOpenIntentHandler(AbstractRequestHandler):
    """Handler for checking school closures."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SchoolsOpenIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        in_district = attr["district"]
        # TODO: prompt the user for district if it isn't set

        src_data = ScheduleParser(requests.get(SCHEDULE_URL).text)
        district = src_data.get_district(in_district)

        if not district:
            speak_output = f"I'm sorry but district {in_district} not found in school database."
        else:
            open_schools = list()
            closed_schools = list()

            for cur_school in district.schools:
                if cur_school.is_open:
                    open_schools.append(cur_school.name)
                else:
                    closed_schools.append(cur_school.name)

            if closed_schools and not open_schools:
                speak_output = "All schools in the district are closed"
            elif open_schools and not closed_schools:
                speak_output = "All schools in the district are open"
            else:
                speak_output = ",".join(closed_schools) + " are closed"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "This is the help for my school app."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter=s3_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureDistrictIntentHandler())
sb.add_request_handler(SchoolsOpenIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()