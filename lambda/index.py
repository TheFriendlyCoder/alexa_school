# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa
# Skills Kit SDK for Python. Please visit https://alexa.design/cookbook for
# additional examples on implementing slots, dialog management, session
# persistence, api calls, and more. This sample is built using the handler
# classes approach in skill builder.
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from school_scraper.fsdscraper import FSDScraper
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# TODO: populate these from user preferences
in_district = "Fredericton"
in_schools = [
    "École Sainte-Anne",
    "École des Bâtisseurs"
]
# ask local school if my school is closed today


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        try:
            sample = requests.get(FSDScraper.SCHEDULE_URL, timeout=45).text
            speak_output = ""
        except requests.exceptions.ReadTimeout:
            logging.error("Read timed out")
            raise

        src_data = FSDScraper(sample)
        district = src_data.get_district(in_district)

        if not district:
            speak_output += f"I'm sorry but district {in_district} not found in school database."
        else:
            open_schools = list()
            closed_schools = list()

            for cur_school in district.schools:
                # skip schools not selected by the user
                if cur_school.name not in in_schools:
                    continue

                if cur_school.is_open:
                    open_schools.append(cur_school.name)
                else:
                    closed_schools.append(cur_school.name)

            if closed_schools and not open_schools:
                speak_output += "All schools in the district are closed. "
            elif open_schools and not closed_schools:
                speak_output += "All schools in the district are open. "
            else:
                speak_output += " and ".join(closed_schools) + " are closed. "

            late_buses = list()
            for cur_school in in_schools:
                temp = district.get_school(cur_school)
                if not temp:
                    logging.error(f"Unable to get school info for {cur_school}")
                    continue
                if temp.has_late_busses:
                    late_buses.append(cur_school)

            if late_buses:
                speak_output += "Also, buses from " + \
                                " and ".join(late_buses) + " are running late."
            else:
                speak_output += "Also, all buses are running on time."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SchoolOpenIntentHandler(AbstractRequestHandler):
    """Handler for checking school closures."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SchoolOpenIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        try:
            sample = requests.get(FSDScraper.SCHEDULE_URL, timeout=45).text
            speak_output = ""
        except requests.exceptions.ReadTimeout:
            logging.error("Read timed out")
            raise

        src_data = FSDScraper(sample)
        district = src_data.get_district(in_district)

        if not district:
            speak_output += f"I'm sorry but district {in_district} not found in school database."
        else:
            open_schools = list()
            closed_schools = list()

            for cur_school in district.schools:
                # skip schools not selected by the user
                if cur_school.name not in in_schools:
                    continue

                if cur_school.is_open:
                    open_schools.append(cur_school.name)
                else:
                    closed_schools.append(cur_school.name)

            if closed_schools and not open_schools:
                speak_output += "All schools in the district are closed"
            elif open_schools and not closed_schools:
                speak_output += "All schools in the district are open"
            else:
                speak_output += " and ".join(closed_schools) + " are closed"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello Python World from Classes!"

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
        speak_output = "You can say hello to me! How can I help?"

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
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
                or
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
    It will simply repeat the intent the user said. You can create custom
    handlers for your intents by defining them above, then also adding them to
    the request handler chain below.
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
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you
    receive an error stating the request handler chain is not found, you have
    not implemented a handler for the intent being invoked or included it in
    the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = \
            "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all
# request and response payloads to the handlers above. Make sure any new
# handlers or interceptors you've defined are included below. The order
# matters - they're processed top to bottom.
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SchoolOpenIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your
# custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
