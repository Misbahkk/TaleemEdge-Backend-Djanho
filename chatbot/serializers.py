# serializers.py
from rest_framework import serializers
from .models import ChatSession, ChatMessage, UserChatPreferences

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message_type', 'content', 'timestamp', 'metadata'
        ]

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    latest_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'created_at', 'updated_at', 'is_active',
            'messages', 'latest_message', 'message_count'
        ]

    def get_latest_message(self, obj):
        latest = obj.get_latest_message()
        if latest:
            return {
                'content': latest.content[:100] + '...' if len(latest.content) > 100 else latest.content,
                'timestamp': latest.timestamp,
                'message_type': latest.message_type
            }
        return None

    def get_message_count(self, obj):
        return obj.messages.count()

class ChatSessionListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing sessions"""
    latest_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'created_at', 'updated_at', 
            'latest_message', 'message_count'
        ]

    def get_latest_message(self, obj):
        latest = obj.get_latest_message()
        if latest:
            return {
                'content': latest.content[:50] + '...' if len(latest.content) > 50 else latest.content,
                'timestamp': latest.timestamp
            }
        return None

    def get_message_count(self, obj):
        return obj.messages.count()

class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=5000)
    session_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()

class UserChatPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChatPreferences
        fields = [
            'bot_name', 'bot_personality', 'language_preference', 
            'max_session_messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CreateSessionSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    first_message = serializers.CharField(max_length=5000, required=False, allow_blank=True)