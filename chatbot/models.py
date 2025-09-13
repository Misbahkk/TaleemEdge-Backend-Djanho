# models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class ChatSession(models.Model):
    """
    Each user can have multiple chat sessions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"

    def get_latest_message(self):
        return self.messages.last()


class ChatMessage(models.Model):
    """
    Individual messages in a chat session
    """
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # For storing additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.session.user.full_name} - {self.message_type} - {self.timestamp}"


class UserChatPreferences(models.Model):
    """
    Store user preferences for their chatbot
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_preferences')
    bot_name = models.CharField(max_length=100, default="AI Assistant")
    bot_personality = models.TextField(default="You are a helpful AI assistant.")
    language_preference = models.CharField(max_length=10, default='en')
    max_session_messages = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - Chat Preferences"