### Overview

The application facilitates real-time chat functionality in a django based web application. It uses WebSockets to
establish a live connection between users, enabling them to send and receive messages instantly. The application includes
mechanisms for user status management, room connections, and real time message handling.

### Key Features

User Status Management: Users can toggle their online status with a button. This status is used to determine if they are
available for chatting.

Finding a Match: Users can initiate a search for a chat partner by clicking the 'Find Match' button. The application
communicates with the server to find another online user and establishes a chat room. First it finds users with
interests, if there is no person who matches with the user's interests, connects with anyone who is online and also connected to the server via WebSocket (used redis to store who is connected).
One user can only be connected to one person at a time. Both the users have to be online for a connection to be
established. They can voluntarily turn off their online status. Find connection logic and websocket code [/chat_app/consumer.py](https://github.com/RohanKaran/chat_app/blob/master/chat_app/consumer.py)

Chat Room Connection: Upon finding a match, the user is connected to a chat room. A new WebSocket connection is
established specifically for this room, allowing private communication between the matched users.

Message Handling: The application handles incoming messages and notifications. Messages from the user and the chat partner
are displayed in the chat log UI. Notifications about connection and disconnection events are also managed.

### How to Run
```python -m venv venv``` (Python 3.8+)

`source venv/bin/activate` (Linux) `venv\Scripts\activate` (Windows)

`pip install -r requirements.txt`

`python manage.py runserver`

 *Default redis host and port: `localhost:6379`*

Register endpoint: `/register/`
Login endpoint: `/login/`
DB is pre-populated with users, you may delete them and create new ones.
Admin username: `rohankaran` password: `123456`

