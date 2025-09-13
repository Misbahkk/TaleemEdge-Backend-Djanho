# views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from .models import ChatSession, ChatMessage, UserChatPreferences
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer, 
    ChatMessageSerializer, SendMessageSerializer,
    UserChatPreferencesSerializer, CreateSessionSerializer
)
from .gemini_service import GeminiChatService

import logging

logger = logging.getLogger(__name__)

class ChatSessionListCreateView(generics.ListCreateAPIView):
    """
    GET: List all chat sessions for authenticated user
    POST: Create new chat session
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateSessionSerializer
        return ChatSessionListSerializer
    
    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user, 
            is_active=True
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        title = serializer.validated_data.get('title', '')
        first_message = serializer.validated_data.get('first_message', '')
        
        # Create new session
        session = ChatSession.objects.create(
            user=request.user,
            title=title or "New Chat"
        )
        
        # If first message is provided, generate title and process it
        if first_message:
            try:
                gemini_service = GeminiChatService()
                
                # Generate title if not provided
                if not title:
                    session.title = gemini_service.generate_chat_title(first_message)
                    session.save()
                
                # Process first message
                with transaction.atomic():
                    # Save user message
                    user_message = ChatMessage.objects.create(
                        session=session,
                        message_type='user',
                        content=first_message
                    )
                    
                    # Get user preferences
                    preferences, _ = UserChatPreferences.objects.get_or_create(
                        user=request.user
                    )
                    
                    # Generate AI response
                    ai_response = gemini_service.generate_response(
                        user_message=first_message,
                        system_prompt=preferences.bot_personality
                    )
                    
                    # Save AI response
                    ChatMessage.objects.create(
                        session=session,
                        message_type='bot',
                        content=ai_response
                    )
                    
                    session.updated_at = timezone.now()
                    session.save()
                    
            except Exception as e:
                logger.error(f"Error processing first message: {str(e)}")
        
        # Return session data
        session_serializer = ChatSessionSerializer(session)
        return Response(session_serializer.data, status=status.HTTP_201_CREATED)


class ChatSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Get specific chat session with all messages
    PUT/PATCH: Update session (title, etc.)
    DELETE: Delete session (soft delete)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user,
            is_active=True
        )
    
    def destroy(self, request, *args, **kwargs):
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'message': 'Chat session deleted successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    Send a message to the chatbot and get AI response
    """
    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id')
    
    try:
        with transaction.atomic():
            # Get or create session
            if session_id:
                session = get_object_or_404(
                    ChatSession, 
                    id=session_id, 
                    user=request.user, 
                    is_active=True
                )
            else:
                # Create new session
                gemini_service = GeminiChatService()
                title = gemini_service.generate_chat_title(user_message)
                session = ChatSession.objects.create(
                    user=request.user,
                    title=title
                )
            
            # Save user message
            user_msg = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message
            )
            
            # Get conversation history
            history = list(session.messages.values(
                'content', 'message_type'
            ).order_by('timestamp'))
            
            # Get user preferences
            preferences, _ = UserChatPreferences.objects.get_or_create(
                user=request.user
            )
            
            # Generate AI response
            gemini_service = GeminiChatService()
            ai_response = gemini_service.generate_response(
                user_message=user_message,
                conversation_history=history[:-1],  # Exclude the just-added user message
                system_prompt=preferences.bot_personality
            )
            
            # Save AI response
            ai_msg = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=ai_response
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            # Return both messages
            return Response({
                'session_id': str(session.id),
                'user_message': ChatMessageSerializer(user_msg).data,
                'bot_response': ChatMessageSerializer(ai_msg).data
            })
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return Response(
            {'error': 'Failed to process message'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserChatPreferencesView(generics.RetrieveUpdateAPIView):
    """
    GET: Get user's chat preferences
    PUT/PATCH: Update user's chat preferences
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserChatPreferencesSerializer
    
    def get_object(self):
        preferences, created = UserChatPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_session_messages(request, session_id):
    """
    Get paginated messages for a specific chat session
    """
    session = get_object_or_404(
        ChatSession, 
        id=session_id, 
        user=request.user, 
        is_active=True
    )
    
    messages = session.messages.all()
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 50))
    
    paginator = Paginator(messages, per_page)
    page_obj = paginator.get_page(page)
    
    serializer = ChatMessageSerializer(page_obj.object_list, many=True)
    
    return Response({
        'messages': serializer.data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_messages': paginator.count
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_sessions(request):
    """
    Delete all chat sessions for the user
    """
    ChatSession.objects.filter(user=request.user).update(is_active=False)
    return Response({'message': 'All chat sessions deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_summary(request, session_id):
    """
    Get AI-generated summary of a chat session
    """
    session = get_object_or_404(
        ChatSession, 
        id=session_id, 
        user=request.user, 
        is_active=True
    )
    
    messages = list(session.messages.values('content', 'message_type'))
    
    if not messages:
        return Response({'summary': 'No messages in this conversation yet.'})
    
    try:
        gemini_service = GeminiChatService()
        summary = gemini_service.get_conversation_summary(messages)
        
        return Response({'summary': summary})
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return Response(
            {'error': 'Failed to generate summary'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )