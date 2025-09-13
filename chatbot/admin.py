# admin.py
from django.contrib import admin
from .models import ChatSession, ChatMessage, UserChatPreferences

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'updated_at', 'is_active', 'message_count']
    list_filter = ['is_active', 'created_at', 'user__role']
    search_fields = ['user__full_name', 'user__email', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'timestamp', 'content_preview']
    list_filter = ['message_type', 'timestamp', 'session__user__role']
    search_fields = ['content', 'session__user__full_name']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    raw_id_fields = ['session']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(UserChatPreferences)
class UserChatPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'bot_name', 'language_preference', 'max_session_messages', 'created_at']
    search_fields = ['user__full_name', 'user__email', 'bot_name']
    list_filter = ['language_preference', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
