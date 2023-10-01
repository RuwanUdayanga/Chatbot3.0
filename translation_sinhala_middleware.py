# from typing import List
# from rasa.engine.graph import GraphComponent, ExecutionContext
# from rasa.engine.recipes.default_recipe import DefaultV1Recipe
# from rasa.shared.nlu.training_data.message import Message
# from googletrans import Translator
# translator = Translator()
#
# from rasa.core.channels import OutputChannel, UserMessage
# from rasa.core import utils
#
# @DefaultV1Recipe.register(
#     [DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER], is_trainable=False
# )
# class TranslateToSinhalaComponent(GraphComponent):
#     def __init__(self):
#         self.translator = Translator()
#
#     def process(self, messages: List[Message]) -> List[Message]:
#         translated_messages = []
#
#         for message in messages:
#             user_input = message.get("response")
#             message_dict = message.as_dict()
#             print(message_dict)
#             print(user_input)
#             translation=translator.translate(user_input, src="auto", dest='si')
#             print(translation)
#             message=translation.text
#             translated_message = Message(data={"text": message})
#             translated_messages.append(translated_message)
#         return translated_messages

# from googletrans import Translator
# translator = Translator()
# import sys
# import json
# import ast
#
# input = sys.argv[1]
# output = translator.translate(input, src="auto", dest='en')
# print(output)
#
# sys.stdout.flush()

from rasa.core.channels import OutputChannel
from googletrans import Translator

class TranslateResponseMiddleware(OutputChannel):
    def __init__(self, output_channel):
        self.translator = Translator()
        self.output_channel = output_channel

    async def send_response(self, recipient_id, message):
        # Translate the message using googletrans

        translated_message = self.translator.translate(message,src="auto", dest='si').text

        # Send the translated message to the user using the specified output channel
        await self.output_channel.send_response(recipient_id, translated_message)