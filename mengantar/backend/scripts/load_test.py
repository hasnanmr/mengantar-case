import json
from locust import HttpUser, task, between
import uuid

class ChatbotUser(HttpUser):
    # Wait 1-3 seconds between tasks to simulate reading/typing time
    wait_time = between(1.0, 3.0)

    def on_start(self):
        """Called when a Locust user starts before any task"""
        # Give each simulated user a unique thread_id
        self.thread_id = str(uuid.uuid4())
        
    @task
    def chat_flow(self):
        """Simulate a user having a basic conversation with the chatbot."""
        
        # We must set stream=False for Locust to just measure the overall TTFB & Time To Complete
        # As SSE streaming can be complicated to measure natively in Locust without a custom client,
        # we will capture the full response time.
        
        payload = {
            "thread_id": self.thread_id,
            "message": "Hi, I have dry skin and acne. What do you recommend?"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        with self.client.post("/api/chat/", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")
