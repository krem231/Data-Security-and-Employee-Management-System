
import asyncio
from nio import AsyncClient, RoomMessageText, MatrixRoom, LoginResponse

# Configuration details - replace these with your actual details
HOMESERVER_URL = "https://your-homeserver.com"
BRIDGE_USER_ID = "@example-bridge-bot:your-homeserver.com"
BRIDGE_AS_TOKEN = "YOUR_AS_TOKEN"

# Initialise the AsyncClient for the bridge
client = AsyncClient(HOMESERVER_URL, BRIDGE_USER_ID)
class MatrixBridge:
    def __init__(self, client):
        self.client = client

    async def start(self):
        # Use the AS token to log in to the homeserver
        response = await self.client.login(token=BRIDGE_AS_TOKEN)
        if isinstance(response, LoginResponse):
            print("Successfully logged into the homeserver!")
        else:
            print(f"Login failed: {response}")
            return
        
        # Register a callback for RoomMessageText events
        self.client.add_event_callback(self.on_message, RoomMessageText)
        
        # Keep the client syncing with the homeserver
        await self.client.sync_forever(timeout=30000)
    async def on_message(self, room: MatrixRoom, event: RoomMessageText):
        # Prevent the bridge from responding to its own messages
        if event.sender == BRIDGE_USER_ID:
            return
        
        print(f"Received message from {event.sender} in {room.room_id}: {event.body}")
        
        # Placeholder for relaying messages to the external service
        # For now, we'll send a confirmation message back to the Matrix room
        await self.send_message_to_matrix(room.room_id, "Message received and acknowledged!")
    async def send_message_to_matrix(self, room_id: str, message: str):
        # Send a text message to the specified Matrix room
        await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message,
            }
        )
async def main():
    bridge = MatrixBridge(client)
    await bridge.start()

if __name__ == "__main__":
    asyncio.run(main())