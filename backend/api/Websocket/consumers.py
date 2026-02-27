# from channels.generic.websocket import WebsocketConsumer
# import json
# from django.contrib.auth.models import User
# from asgiref.sync import async_to_sync
# from api.TestAPI.model import Test

# # for test
# class MyConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#     def disconnect(self, close_code):
#         pass
#     def receive(self, text_data):
#         self.send(text_data=text_data)


# # chat
# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.username = self.scope['url_route']['kwargs']['username']
#         self.room_group_name = f'chat_{self.room_name}'

#         # Check if the user exists
#         if not User.objects.filter(username=self.username).exists():
#             self.close()
#             return

#         # Add user to the users list (bypassing approval)
#         if not hasattr(self.channel_layer, 'users'):
#             self.channel_layer.users = {}
#         if self.room_group_name not in self.channel_layer.users:
#             self.channel_layer.users[self.room_group_name] = []
#         self.channel_layer.users[self.room_group_name].append(self.username)

#         # Add user to the group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()

#         # Notify the room that a user has joined
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'user_joined',
#                 'username': self.username,
#                 'message': f'{self.username} has joined the chat.'
#             }
#         )

#     def disconnect(self, close_code):
#         # Remove user from the room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Remove user from the users list
#         if self.username in self.channel_layer.users.get(self.room_group_name, []):
#             self.channel_layer.users[self.room_group_name].remove(self.username)

#         # Notify the room that the user has left
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'user_left',
#                 'username': self.username,
#                 'message': f'{self.username} has left the chat.'
#             }
#         )

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message', '')

#         # Broadcast the message to all users in the room
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': self.username
#             }
#         )

#     def chat_message(self, event):
#         message = event['message']
#         username = event['username']

#         # Send the message to WebSocket
#         self.send(text_data=json.dumps({
#             'username': username,
#             'message': message
#         }))

#     def user_joined(self, event):
#         message = event['message']
#         username = event['username']

#         # Send join message to WebSocket
#         self.send(text_data=json.dumps({
#             'username': username,
#             'message': message
#         }))

#     def user_left(self, event):
#         message = event['message']
#         username = event['username']

#         # Send leave message to WebSocket
#         self.send(text_data=json.dumps({
#             'username': username,
#             'message': message
#         }))


# # response from model by keyword(s)
# class modelChatConsumer(WebsocketConsumer):
#     def connect(self):
#         # Use a default room name, or you can generate one dynamically
#         self.room_name = "default_room"
#         self.username = self.scope['user'].username if self.scope['user'].is_authenticated else "guest"
#         self.room_group_name = f'chat_{self.room_name}'

#         # Add user to the users list (bypassing approval)
#         if not hasattr(self.channel_layer, 'users'):
#             self.channel_layer.users = {}
#         if self.room_group_name not in self.channel_layer.users:
#             self.channel_layer.users[self.room_group_name] = []
#         self.channel_layer.users[self.room_group_name].append(self.username)

#         # Add user to the group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()

#         # Notify the room that a user has joined
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'user_joined',
#                 'username': self.username,
#                 'message': f'{self.username} has joined the chat.'
#             }
#         )

#     def disconnect(self, close_code):
#         # Remove user from the room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Remove user from the users list
#         if self.username in self.channel_layer.users.get(self.room_group_name, []):
#             self.channel_layer.users[self.room_group_name].remove(self.username)

#         # Notify the room that the user has left
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'user_left',
#                 'username': self.username,
#                 'message': f'{self.username} has left the chat.'
#             }
#         )

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message', '')

#         # Process the message and get the response
#         response_message = self.process_message(message)

#         # Send the response message to the user
#         self.send(text_data=json.dumps({
#             # 'username': 'System',
#             'message': response_message
#         }))

#         # Broadcast the message to all users in the room
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': self.username
#             }
#         )

#     def process_message(self, message):
#         # Check if the message starts with 'info:'
#         if message.startswith("info:"):
#             name = message[5:].strip()  # Extract the name after 'info:'
            
#             # Query the TestAPI model based on the name
#             test_objects = Test.objects.filter(name__iexact=name)  # Case-insensitive lookup
            
#             count = test_objects.count()  # Count how many objects were found
            
#             if count > 0:
#                 response_list = [f"Found {count} object(s) with the name '{name}':\n"]
                
#                 # Iterate over all matching objects and format their details
#                 for test in test_objects:
#                     test_info = {
#                         "ID": str(test.id),
#                         "name": test.name,
#                         "description": test.description,
#                         "address": test.address,
#                     }
#                     # Convert the object details to a formatted string and append to the response list
#                     response_list.append("\n".join([f"{key}: {value}" for key, value in test_info.items()]))

#                 # Join all employee details into a single string
#                 return "\n\n".join(response_list)
#             else:
#                 return f'No object of TestAPI found with name: {name}'
#         else:
#             return 'Invalid command. Please use "info:<name>" to get test_object details.'

#     def chat_message(self, event):
#         message = event['message']
#         username = event['username']

#         # Send the message to WebSocket
#         self.send(text_data=json.dumps({
#             'username': username,
#             'message': message
#         }))

#     def user_joined(self, event):
#         message = event['message']
#         username = event['username']

#         # Send join message to WebSocket
#         self.send(text_data=json.dumps({
#             'username': username,
#             'message': message
#         }))

#     def user_left(self, event):
#         message = event['message']
#         username = event['username']

#         # Send leave message to WebSocket
#         self.send(text_data=json.dumps({
#             'username': username,
#             'message': message
#         }))
