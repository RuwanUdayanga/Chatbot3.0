# Chatbot3.0
Medibot

Project group: 19 Project id: 09 Project title: Localised Chatbot for Hospital Customer Care
Instrctions

Enable a virtual environment and start it.
Install rasa frame:- pip install rasa 
Install mysql connector:- pip install mysql-connector-python 
Install django:- python -m pip install Django 
Install google translator:- pip install googletrans==4.0.0rc1

Run action server:- run action server: rasa run actions --cors "" --debug Run rasa server:- rasa run -m models --enable-api --cors "" --debug

To use bot with shell:- rasa shell To use bot with shell interactive mode:- rasa interactive

To open admin panel go to url:- http://127.0.0.1:8000/admin/
