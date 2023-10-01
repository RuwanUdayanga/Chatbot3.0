# custom actions
import mysql.connector
from typing import Text, List, Dict, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted
from datetime import datetime
from rasa_sdk.events import SlotSet
from datetime import date,timedelta
from googletrans import Translator
translator = Translator()

class ActionWelcome(Action):
    def name(self) -> Text:
        return "action_welcome"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="ආයුබෝවන්! ඔබට මගෙන් යම් සේවාවක් අවශ්‍යද?",
            buttons=[
                {"title": "අද දින හමුවිය හැකි වෛද්‍යවරුන් කවුදැයි දැන ගැනීමට",
                 "payload": '/check_doctors_available_today{{"day":"{}"}}'.format("today")},
                {"title": "හෙට දින හමුවිය හැකි වෛද්‍යවරුන් කවුදැයි දැන ගැනීමට",
                 "payload": '/check_doctors_available_today{{"day":"{}"}}'.format("tomorrow")},
                {"title": "වෙන්කරවා ගත හැකි විශේෂඥ වෛද්‍යවරුන් පිළිබඳ දැන ගැනීමට",
                 "payload": "/check_available_specialists"},
                {"title": "වෛද්‍යවරයකු වෙන්කරවා ගැනීමට",
                 "payload": "/add_booking_initial"},
                {"title": "වෛද්‍යවරයකු හමුවීමක් අවලංගු කිරීමට",
                 "payload": "/cancel_appointment"},
            ]
        )

        return []
class action_get_dates_available_given_Name(Action):
    def name(self) -> Text:
        return "action_get_dates_available_given_Name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the doctor's name entity from the user's message
        name_entity = next(tracker.get_latest_entity_values("doctor_name"),None)

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

                        dates = [row[0].strftime("%Y-%m-%d") for row in cursor.fetchall()]
                buttons = []
                for date in dates:
                    payload = '/provide_date{{"date":"{}"}}'.format(date)

                    buttons.append(
                        {"title": "{}".format(date),
                         "payload": payload})


                buttons.append(
                    {"title": "වෙනත් වෛද්‍යවරයකු සෙවීමට",
                     "payload": '/add_booking_initial'}
                )
                buttons.append(
                    {"title": "වෙනත් සේවාවක් ලබා ගැනීමට",
                     "payload": '/get_another_service'}
                )
                translated_name = translator.translate(name_entity, src="en", dest='si').text
                if len(dates)==1:
                    dispatcher.utter_message(f"වෛද්‍ය {translated_name} {', '.join(dates)} දින වෙන්කරවා ගත හැක.")
                    dispatcher.utter_button_template("utter_tell_select", buttons, tracker)

                elif len(dates)>1:
                    dispatcher.utter_message(f"වෛද්‍ය {translated_name} {', '.join(dates)} දිනවලදී වෙන්කරවා ගත හැක.")
                    dispatcher.utter_button_template("utter_tell_select", buttons, tracker)

                else:
                    dispatcher.utter_message(f"{translated_name} වෙන්කරවා ගත නොහැක.")
                    dispatcher.utter_button_template("", buttons, tracker)

            except mysql.connector.Error as err:

                dispatcher.utter_message("An error occurred while fetching data.")
        else:
            dispatcher.utter_message("කරුණාකර වලංගු නමක් සපයන්න.")

        return [SlotSet("doctor_name", name_entity)]
class action_get_channel_confirmation(Action):
    def name(self) -> Text:
        return "action_get_channel_confirmation"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        date = next(tracker.get_latest_entity_values("date"),None)
        name = tracker.get_slot("doctor_name")

        buttons=[
            {"payload":'/confirm_booking{{"confirm_booking":"{}"}}'.format("Confirm"),"title":"තහවුරු කරමි"},
            {"payload":'/deny_booking{{"confirm_booking":"{}"}}'.format("Deny"),"title":"ප්‍රතික්ෂේප කරමි"}
        ]
        dispatcher.utter_message(text="වෙන්කරවා ගැනීම තහවුරු කරන්න",buttons=buttons)

        return [SlotSet("date", date)]
class action_book_doctor(Action):
    def name(self) -> Text:
        return "action_book_doctor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        doctor_name = tracker.get_slot("doctor_name").lower()
        date = tracker.get_slot("date")
        patient_id = 1 # Change later
        confirm = next(tracker.get_latest_entity_values("confirm_booking"), None)
        confirm=confirm.lower()
        if confirm == "confirm":
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
                    translated_name = translator.translate(doctor_name, src="en", dest='si').text
                    if id_result:
                        doctor_id = id_result[0]

                        # Execute the SQL query to book the doctor
                        query = "INSERT INTO medibot_booking (day, book, doctor_id, patient_id) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (date, 1, doctor_id, patient_id))

                        conn.commit()  # Commit the transaction

                        message = (f"{date} දින වෛද්‍ය {translated_name} වෙන්කරවා ගැනීම සාර්ථකයි!")
                        dispatcher.utter_message(message)
                    else:
                        response = f"සමාවන්න, වෛද්‍ය {translated_name} {date} දින වෙන්කරවා ගත නොහැකියි"
                        dispatcher.utter_message(response)

            except mysql.connector.Error as err:

                dispatcher.utter_message("An error occurred while fetching data.")

        return [SlotSet("confirm_booking", confirm)]

class Action_ask_other_services(Action):
    def name(self) -> Text:
        return "action_ask_other_services"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="ඔබට අපග‌ෙන් වෙනත් සේවාවක් අවශ්‍යද?",
            buttons=[
                {"title": "අද දින සිටින වෛද්‍යවරුන් කවුදැයි දැන ගැනීමට",
                 "payload": '/check_doctors_available_today{{"day":"{}"}}'.format("today")},
                {"title": "හෙට දින සිටින වෛද්‍යවරුන් කවුදැයි දැන ගැනීමට",
                 "payload": '/check_doctors_available_today{{"day":"{}"}}'.format("tomorrow")},
                {"title": "වෙන්කරවා ගත හැකි විශේෂඥ වෛද්‍යවරුන් පිළිබඳ දැන ගැනීමට",
                 "payload": "/check_available_specialists"},
                {"title": "වෛද්‍යවරයකු වෙන්කරවා ගැනීමට",
                 "payload": "/add_booking_initial"},
                {"title": "වෛද්‍යවරයෙකු හමුවීම අවලංගු කිරීමට",
                 "payload": "/cancel_appointment"},
            ]
        )
        return []
class Action_check_doctors_available_today_tomorrow(Action):
    def name(self) -> Text:
        return "action_check_doctors_available_today_tomorrow"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], date=date) -> List[Dict[Text, Any]]:
        # Get the current date
        selected_day = next(tracker.get_latest_entity_values("day"), None)

        if selected_day=="today":
            day_selected= date.today()
        else:
            day_selected= date.today() + timedelta(days=1)
        # Connect to the MySQL database
        try:
            conn = mysql.connector.connect(
                 host='localhost',
                 user='root',
                 password='181522',
                 database='medibot1.0'
             )
            cursor = conn.cursor()

            query = "SELECT DISTINCT d.doctor_name FROM medibot_doctor d " \
                    "INNER JOIN medibot_doctor_availability da ON d.doctor_id = da.doctor_id " \
                    "WHERE da.day = %s AND da.available = 1"
            # Execute the SQL query to check doctor availability
            cursor.execute(query,(day_selected,))
            names = [row[0] for row in cursor.fetchall()]

            # Close the database connection
            cursor.close()
            conn.close()

            buttons = []

            for name in names:
                translate_name = translator.translate(name, src="en", dest='si')
                payload = '/provide_doctor_name{{"doctor_name":"{}"}}'.format(name)

                buttons.append(
                    {"title": "{}".format('වෛද්‍ය '+ translate_name.text),
                     "payload": payload})

            buttons.append(
                {"title": "වෙනත් සේවාවක් ලබා ගැනීමට",
                 "payload": '/get_another_service'}
            )
        except mysql.connector.Error as err:

            dispatcher.utter_message("An error occurred while fetching data.")

        if len(names) >= 1:
            if selected_day=="today":
                dispatcher.utter_button_template("utter_available_doctors_today", buttons, tracker)
            else:
                dispatcher.utter_button_template("utter_available_doctors_tomorrow", buttons, tracker)
        else:
            if selected_day == "today":
                dispatcher.utter_message("අද දින වෙන්කරවා ගත හැකි වෛද්‍යවරැ කිසිවෙක් නැත.")
            else:
                dispatcher.utter_message("හෙට දින වෙන්කරවා ගත හැකි වෛද්‍යවරැ කිසිවෙක් නැත.")
            dispatcher.utter_button_template("", buttons, tracker)

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

                        translated_name = translator.translate(doctor_name, src="en", dest='si').text

                        message = f"{date} දින වෛද්‍ය {translated_name} සමඟ හමුවීම අවලංගු කිරීම සාර්ථකයි!"
                        dispatcher.utter_message(message)
                    else:
                        response = "ලබා දී ඇති තොරතුරු සඳහා වෙන්කරවා ගැනීමක් නැත"
                        dispatcher.utter_message(response)

            except mysql.connector.Error as err:

                dispatcher.utter_message("An error occurred while fetching data.")

        return []
class action_confirm_cancellation(Action):
    def name(self) -> Text:
        return "action_confirm_cancellation"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        appointment_ID = tracker.get_slot("appointment_ID")
        dispatcher.utter_message(
            text="ඔබට අංක {} දරණ හමුවීම් වෙන්කරවා ගැනීම අවලංගු කිරීමට අවශ්‍යද!".format(appointment_ID),
            buttons=[
                {"title": "හමුවීම අවලංගු කිරීම තහවුරු කරමි",
                 "payload": '/confirm_appointment_cancellation{{"confirm_cancellation":"{}"}}'.format("cancellation")},

                {"title": "නැත",
                 "payload": '/get_another_service'},
            ]
        )
        return []

class action_ask_speciality(Action):
    def name(self) -> str:
        return "action_ask_speciality"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the date entity from the user's message

        try:
            conn = mysql.connector.connect(
                 host='localhost',
                 user='root',
                 password='181522',
                 database='medibot1.0'
             )
            cursor = conn.cursor()

            query = "SELECT DISTINCT d.speciality FROM medibot_doctor d "
            # Execute the SQL query to check doctor availability
            cursor.execute(query,)
            specialities = [row[0] for row in cursor.fetchall()]

            # Close the database connection
            cursor.close()
            conn.close()

            buttons = []

            for speciality in specialities:
                translated_speciality = translator.translate(speciality, src="en", dest='si').text
                payload = '/give_speciality{{"speciality":"{}"}}'.format(speciality)

                buttons.append(
                    {"title": "{}".format(translated_speciality),
                     "payload": payload})

            buttons.append(
                {"title": "වෙනත් සේවාවක් ලබා ගැනීමට",
                 "payload": '/get_another_service'}
            )
            dispatcher.utter_button_template("utter_available_specialities", buttons, tracker)
        except mysql.connector.Error as err:
            print("Error:", err)
            dispatcher.utter_message("An error occurred while fetching data.")
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
                        cursor.execute(query, (speciality.lower(),))

                        # Fetch all the available specialties
                        doctor_names = [row[0] for row in cursor.fetchall()]

                buttons = []

                for doctor_name in doctor_names:
                    translate_name = translator.translate(doctor_name, src="en", dest='si').text
                    translate_speciality = translator.translate(speciality, src="en", dest='si').text
                    payload = '/provide_doctor_name{{"doctor_name":"{}"}}'.format(doctor_name)

                    buttons.append(
                        {"title": "{}".format('වෛද්‍ය ' + translate_name),
                         "payload": payload})

                buttons.append(
                    {"title": "වෙනත් සේවාවක් ලබා ගැනීමට",
                     "payload": '/get_another_service'}
                )

                if doctor_names:
                    dispatcher.utter_button_message("සිටින {} වෛද්‍යවරුන් වන්නේ,".format(translate_speciality), buttons)

                else:
                    dispatcher.utter_button_message("සමාවන්න, රෝහලේ ඒ ක්ෂේත්‍රයට අදාල විශේෂඥ වෛද්‍යවරු නොමැත,", buttons)

            except mysql.connector.Error as err:

                dispatcher.utter_message("An error occurred while fetching data.")

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