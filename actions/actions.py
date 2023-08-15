# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
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
# import mysql.connector
#
# conn = mysql.connector.connect(
#              host='localhost',
#              user='root',
#              password='181522',
#              database='medibot'
#          )
# cursor = conn.cursor()
#
# from typing import Text, Dict, Any, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.events import SlotSet
# from rasa_sdk.executor import CollectingDispatcher
#
# class ActionCheckRestaurants(Action):
#    def name(self) -> Text:
#       return "action_check_restaurants"
#
#    def run(self,
#            dispatcher: CollectingDispatcher,
#            tracker: Tracker,
#            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#       cuisine = tracker.get_slot('cuisine')
#       q = "select * from restaurants where cuisine='{0}' limit 1".format(cuisine)
#       result = cursor.query(q)
#
#       cursor.close()
#       conn.close()
#       return [SlotSet("matches", result if result is not None else [])]

import mysql.connector
from typing import Text, List, Dict, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from datetime import datetime
from rasa_sdk.events import SlotSet

class action_check_doctor_availability(Action):
    def name(self) -> Text:
        return "action_check_doctor_availability"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        doctor_name = tracker.get_slot("doctor_name")
        day = tracker.get_slot("date")

        # Connect to the SQLite database
        #conn = sqlite3.connect('db.sqlite3')
        #cursor = conn.cursor()

        # Connect to the MySQL database
        conn = mysql.connector.connect(
             host='localhost',
             user='root',
             password='181522',
             database='medibot'
         )
        cursor = conn.cursor()

        # Execute the SQL query to check doctor availability
        cursor.execute("SELECT available FROM medibot_doctor_availability WHERE doctor_id = (SELECT doctor_id FROM medibot_doctor WHERE doctor_name = %s) AND day = %s",(doctor_name, day))
        result = cursor.fetchone()

        # Close the database connection
        cursor.close()
        conn.close()

        if result and result[0] == 1:
            message = f"{doctor_name} is available on {day}."
        else:
            message = f"{doctor_name} is not available on {day}."

        # Send the response back to the user
        dispatcher.utter_message(text=message)

        return []

class action_get_doctors_available_onDate(Action):
    def name(self) -> str:
        return "action_get_doctors_available_onDate"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the date entity from the user's message
        date_entity = next(tracker.get_latest_entity_values("date"), None)

        if date_entity:
            # Connect to the MySQL database
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='181522',
                database='medibot'
            )
            cursor = conn.cursor()

            # Execute the SQL query to get doctors available on the given date
            query = "SELECT DISTINCT d.doctor_name FROM medibot_doctor d " \
                    "INNER JOIN medibot_doctor_availability da ON d.doctor_id = da.doctor_id " \
                    "WHERE da.day = %s AND da.available = 1"
            cursor.execute(query, (date_entity,))

            # Fetch all the doctor names
            doctor_names = [row[0] for row in cursor.fetchall()]

            # Close the database connection
            cursor.close()
            conn.close()

            if doctor_names:
                dispatcher.utter_message(f"Doctors available on {date_entity}: {', '.join(doctor_names)}")
            else:
                dispatcher.utter_message(f"No doctors available on {date_entity}")
        else:
            dispatcher.utter_message("I couldn't understand the date. Please provide a valid date.")

        return []