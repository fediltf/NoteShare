import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatModel

# Set up logging for the application
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """
    ChatConsumer handles WebSocket connections for the chat application.
    It manages user connections, message sending, and retrieving chat history.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is established.
        It adds the user to a chat group and sends the last messages to the client.
        """
        my_id = self.scope['user'].id  # Get the current user's ID
        other_user_id = self.scope['url_route']['kwargs']['id']  # Get the other user's ID from the URL

        # Create a unique room name based on user IDs to differentiate chat rooms
        if int(my_id) > int(other_user_id):
            self.room_name = f'{my_id}-{other_user_id}'
        else:
            self.room_name = f'{other_user_id}-{my_id}'

        self.roomGroupName = f'chat_{self.room_name}'  # Define the group name for the chat room

        # Join the chat group
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()  # Accept the WebSocket connection

        # Fetch last messages and send them to the client
        last_messages = await self.get_last_messages(self.roomGroupName)
        for message in last_messages:
            print(message.message)
            await self.send(text_data=json.dumps({
                "message": message.message,
                "username": message.sender.username,
                "user_id": message.sender.id,
                "time": message.timestamp.strftime("%H:%M:%S")  # Format the timestamp for display
            }))

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is closed.
        It removes the user from the chat group.
        """
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_name)

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        It processes the incoming message, saves it to the database,
        and sends it to all users in the chat group.
        """
        text_data_json = json.loads(text_data)  # Parse the incoming JSON data
        message = text_data_json["message"]  # Extract the message content
        user_id = self.scope['user'].id  # Get the current user's ID

        # Save the message to the database
        data_base = await self.save_message(user_id, self.roomGroupName, message)
        logger.info("Database output: %s", data_base)  # Log the result of the save operation

        # Send the message to the group
        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",  # Specify the type of message to handle
                "message": message,
                "username": text_data_json["username"],  # Include the username in the event
                "time": text_data_json["time"],  # Include the time in the event
                "user_id": user_id  # Include the user ID in the event
            }
        )

    async def sendMessage(self, event):
        """
        Called when a message is sent to the WebSocket.
        It sends the message data back to the WebSocket client.
        """
        message = event["message"]
        user_id = event["user_id"]
        time = event["time"]

        # Get user object asynchronously
        user_obj = await self.get_user(user_id)

        # Send the message back to the WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "username": user_obj.username,  # Send the username of the sender
            "user_id": user_id,
            "time": time  # Send the time of the message
        }))

    @database_sync_to_async
    def save_message(self, user_id, thread_name, message):
        """
        Saves a new chat message to the database.
        :param user_id: ID of the user sending the message.
        :param thread_name: Name of the chat thread.
        :param message: The message content to be saved.
        :return: Success message or error message.
        """
        try:
            sender = User.objects.get(id=user_id)  # Get user by ID
            new_message = ChatModel.objects.create(
                sender=sender, message=message, thread_name=thread_name
            )
            new_message.save()  # Save the new message to the database
            return "Success"
        except User.DoesNotExist:
            logger.error("User with ID %s does not exist.", user_id)  # Log error if user does not exist
            return "User does not exist"

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Retrieves a user object based on user ID.
        :param user_id: ID of the user to retrieve.
        :return: User object.
        """
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_last_messages(self, thread_name, limit=10):
        """
        Retrieves the last messages from the chat thread.
        :param thread_name: Name of the chat thread.
        :param limit: Maximum number of messages to retrieve.
        :return: List of chat messages.
        """
        return list(ChatModel.objects.filter(thread_name=thread_name).select_related('sender').order_by('timestamp')[:limit])