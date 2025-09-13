# services/gemini_service.py
import google.generativeai as genai
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GeminiChatService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None,
        system_prompt: str = "You are a helpful AI assistant."
    ) -> str:
        """
        Generate AI response using Gemini API
        """
        try:
            # Build conversation context
            context_messages = []
            
            # Add system prompt
            context_messages.append(f"System: {system_prompt}")
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = "Human" if msg['message_type'] == 'user' else "Assistant"
                    context_messages.append(f"{role}: {msg['content']}")
            
            # Add current user message
            context_messages.append(f"Human: {user_message}")
            context_messages.append("Assistant:")
            
            # Join all messages
            prompt = "\n".join(context_messages)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "I'm experiencing some technical difficulties. Please try again later."

    def generate_chat_title(self, first_message: str) -> str:
        """
        Generate a title for the chat session based on first message
        """
        try:
            prompt = f"""
            Generate a short, descriptive title (maximum 5 words) for a chat conversation that starts with this message:
            
            "{first_message}"
            
            Just return the title, nothing else.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                title = response.text.strip()
                # Limit title length
                if len(title) > 50:
                    title = title[:47] + "..."
                return title
            else:
                return "New Chat"
                
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return "New Chat"

    def get_conversation_summary(self, messages: List[Dict]) -> str:
        """
        Generate a summary of the conversation
        """
        try:
            # Take first and last few messages
            context_msgs = messages[:3] + messages[-3:] if len(messages) > 6 else messages
            
            conversation_text = "\n".join([
                f"{'User' if msg['message_type'] == 'user' else 'Bot'}: {msg['content']}"
                for msg in context_msgs
            ])
            
            prompt = f"""
            Provide a brief summary (2-3 sentences) of this conversation:
            
            {conversation_text}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "No summary available"
                
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "No summary available"
        

    