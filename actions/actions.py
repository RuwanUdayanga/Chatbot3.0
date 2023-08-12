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

class action_check_doctor_availability(Action):
    def name(self) -> Text:
        return "action_check_doctor_availability"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        doctor_name = tracker.get_slot("doctor_name")
        day = "2023-08-14"

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