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
from rasa_sdk.events import Restarted
from datetime import datetime
from rasa_sdk.events import SlotSet

class ActionWelcome(Action):
    def name(self) -> Text:
        return "action_welcome"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="ආයුබෝවන්! මම ඔබට උදව් කරන්නේ කෙසේ ද?")

        return []
class action_check_doctor_availability(Action):
    def name(self) -> Text:
        return "action_check_doctor_availability"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        doctor_name = tracker.get_slot("doctor_name").lower()
        day = tracker.get_slot("date")

        # Connect to the MySQL database
        conn = mysql.connector.connect(
             host='localhost',
             user='root',
             password='181522',
             database='medibot1.0'
         )
        cursor = conn.cursor()

        # Execute the SQL query to check doctor availability
        cursor.execute("SELECT available FROM medibot_doctor_availability WHERE doctor_id = (SELECT doctor_id FROM medibot_doctor WHERE doctor_name = %s) AND day = %s",(doctor_name, day))
        result = cursor.fetchone()

        # Close the database connection
        cursor.close()
        conn.close()

        if result and result[0] == 1:
            message = f"වෛද්‍ය {doctor_name}, {day} දින වෙන්කරවා ගත හැක. ඔබට වෙන් කිරීමක් කිරීමට අවශ්‍යද? ඔව් නම්, 'ඔව් මම වෙන්කරවා ගැනීම තහවුරු කරමි' ටයිප් කරන්න"
        else:
            message = f"වෛද්‍ය {doctor_name}, {day} දින වෙන්කරවා ගත නොහැක"

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
                database='medibot1.0'
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
                dispatcher.utter_message(f"{date_entity} දින ලබා ගත හැකි වෛද්‍යවරුන් : {', '.join(doctor_names)}")
            else:
                dispatcher.utter_message(f"{date_entity} දින වෙන්කරවා ගත හැකි වෛද්‍යවරුන් නොමැත")
        else:
            dispatcher.utter_message("මට දිනය තේරුම් ගත නොහැකි විය. කරුණාකර වලංගු දිනයක් ලබා දෙන්න")

        return []


class action_get_dates_available_given_Name(Action):
    def name(self) -> Text:
        return "action_get_dates_available_given_Name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the doctor's name entity from the user's message
        name_entity = next(tracker.get_latest_entity_values("doctor_name"), None)

        if name_entity:
            try:
                # Connect to the MySQL database
                with mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='181522',
                        database='medibot1.0'
                ) as conn:
                    with conn.cursor() as cursor:
                        # Execute the SQL query to get available dates for the given doctor
                        query = "SELECT DISTINCT d.day FROM medibot_doctor_availability d " \
                                "INNER JOIN medibot_doctor da ON d.doctor_id = da.doctor_id " \
                                "WHERE da.doctor_name = %s AND d.available = 1"

                        cursor.execute(query, (name_entity,))

                        # Fetch all the available dates
                        #dates = [row[0] for row in cursor.fetchall()]
                        dates = [row[0].strftime("%Y-%m-%d") for row in cursor.fetchall()]

                if dates:
                    dispatcher.utter_message(f"{name_entity} available on: {', '.join(dates)}")
                else:
                    dispatcher.utter_message(f"{name_entity} not available.")
            except mysql.connector.Error as err:
                print("Error:", err)
                dispatcher.utter_message("An error occurred while fetching data.")
        else:
            dispatcher.utter_message("කරුණාකර වලංගු නමක් සපයන්න.")

        return []

class action_check_available_doctors_given_speciality(Action):
        def name(self) -> Text:
            return "action_check_available_doctors_given_speciality"

        def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
            speciality = next(tracker.get_latest_entity_values("speciality"), None)
            try:
                # Connect to the MySQL database
                with mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='181522',
                        database='medibot1.0'
                ) as conn:
                    with conn.cursor() as cursor:
                        # Execute the SQL query to get available specialties
                        query = "SELECT DISTINCT doctor_name FROM medibot_doctor WHERE speciality=%s"
                        cursor.execute(query,(speciality,))

                        # Fetch all the available specialties
                        specialties = [row[0] for row in cursor.fetchall()]

                if specialties:
                    response = "සිටින විශේෂඥ වෛද්‍යවරුන්: {}".format(", ".join(specialties))
                else:
                    response = "සමාවන්න, රෝහලේ ඒ ක්ෂේත්‍රයට අදාල විශේෂඥ වෛද්‍යවරු නොමැත"

                dispatcher.utter_message(response)
            except mysql.connector.Error as err:
                print("Error:", err)
                dispatcher.utter_message("An error occurred while fetching data.")

            return []

class action_book_doctor(Action):
    def name(self) -> Text:
        return "action_book_doctor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        doctor_name = next(tracker.get_latest_entity_values("doctor_name"), None)
        date = next(tracker.get_latest_entity_values("date"), None)
        patient_id = 1 # Change later
        doctor_name = tracker.get_slot("doctor_name").lower()
        date = tracker.get_slot("date")
        confirm = next(tracker.get_latest_entity_values("confirm"), None)

        if confirm == "confirm the booking":
            try:
                # Connect to the MySQL database
                with mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='181522',
                        database='medibot1.0'
                ) as conn:
                    cursor = conn.cursor()

                    # Execute the SQL query to get doctor's ID
                    query1 = "SELECT doctor_id FROM medibot_doctor WHERE doctor_name = %s"
                    cursor.execute(query1, (doctor_name,))
                    id_result = cursor.fetchone()

                    if id_result:
                        doctor_id = id_result[0]

                        # Execute the SQL query to book the doctor
                        query = "INSERT INTO medibot_booking (day, book, doctor_id, patient_id) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (date, 1, doctor_id, patient_id))

                        conn.commit()  # Commit the transaction

                        message = (f"{date} දින වෛද්‍ය {doctor_name} වෙන්කරවා ගැනීම සාර්ථකයි! \n ඔබට වෙනත් සේවාවක් අවශ්‍යද?"
                                   f"")
                        dispatcher.utter_message(message)
                    else:
                        response = f"සමාවන්න, වෛද්‍ය {doctor_name} {date} දින වෙන්කරවා ගත නොහැකියි"
                        dispatcher.utter_message(response)

            except mysql.connector.Error as err:
                print("Error:", err)
                dispatcher.utter_message("An error occurred while fetching data.")

        return []
class action_cancel_appointment(Action):
    def name(self) -> Text:
        return "action_cancel_appointment"

    def fetch_appointment_info(self, cursor, appointment_ID):
        query = """
            SELECT
                d.doctor_name,
                b.day
            FROM
                medibot_booking AS b
            JOIN
                medibot_doctor AS d ON b.doctor_id = d.doctor_id
            WHERE
                b.appointment_ID = %s
        """
        cursor.execute(query, (appointment_ID,))
        return cursor.fetchone()

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        confirm = next(tracker.get_latest_entity_values("confirm_cancellation"), None)

        if confirm == "cancellation":
            appointment_ID = tracker.get_slot("appointment_ID")
            try:
                with mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='181522',
                        database='medibot1.0'
                ) as conn:
                    cursor = conn.cursor()

                    appointment_info = self.fetch_appointment_info(cursor, appointment_ID)

                    if appointment_info:
                        doctor_name, date = appointment_info

                        query = "UPDATE medibot_booking SET book = 0 WHERE appointment_ID = %s"
                        cursor.execute(query, (appointment_ID,))
                        conn.commit()

                        message = f"{date} දින වෛද්‍ය {doctor_name} සමඟ හමුවීම අවලංගු කිරීම සාර්ථකයි!"
                        dispatcher.utter_message(message)
                    else:
                        response = "ලබා දී ඇති තොරතුරු සඳහා වෙන්කරවා ගැනීමක් නැත"
                        dispatcher.utter_message(response)

            except mysql.connector.Error as err:
                print("Error:", err)
                dispatcher.utter_message("An error occurred while fetching data.")

        return []
class  ActionRestart(Action):

  def name(self) -> Text:
      return "action_restart"

  async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
  ) -> List[Dict[Text, Any]]:

      # custom behavior
      response = "ආයුබෝවන්! මම ඔබට උදව් කරන්නේ කෙසේ ද?"
      dispatcher.utter_message(response)
      return [Restarted()]
  class ActionRestartWithoutMessage(Action):
      def name(self) -> Text:
          return "action_restart_without_message"

      async def run(
              self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
      ) -> List[Dict[Text, Any]]:
          # custom behavior

          return [Restarted()]

class ActionRestartWithThank(Action):
    def name(self) -> Text:
        return "action_restart_with_thank"

    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # custom behavior
        response = "සුභ දිනයක් වේවා!"
        dispatcher.utter_message(response)
        return [Restarted()]