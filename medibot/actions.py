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
        doctor_name = "Dr. Johnson"
        day = "Monday"

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
        cursor.execute("SELECT available FROM doctor_availability WHERE doctor_name = %s AND day = %s",(doctor_name, day))
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
