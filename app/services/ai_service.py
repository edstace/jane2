import openai
import os
from functools import wraps
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models import Cache

class AIService:
    """Service for interacting with OpenAI API"""
    
    @staticmethod
    def cache_response(func):
        """Decorator to cache API responses"""
        @wraps(func)
        def wrapper(cls, user_message, context=None):
            # Only cache responses without context
            if not context:
                cache_key = f"response:{hash(user_message)}"
                cached = Cache.query.get(cache_key)
                
                if cached and cached.expires > datetime.utcnow():
                    current_app.logger.info("Cache hit for message")
                    return cached.response
                
                response = func(cls, user_message, context)
                
                # Cache for configured time
                cache_ttl = current_app.config['CACHE_TTL']
                if cached:
                    cached.response = response
                    cached.expires = datetime.utcnow() + timedelta(seconds=cache_ttl)
                else:
                    cached = Cache(
                        id=cache_key,
                        response=response,
                        expires=datetime.utcnow() + timedelta(seconds=cache_ttl)
                    )
                    db.session.add(cached)
                
                db.session.commit()
                return response
            
            return func(cls, user_message, context)
        return wrapper
    
    @classmethod
    @cache_response
    def get_job_coaching_advice(cls, user_message, context=None):
        """Get job coaching advice using OpenAI"""
        if current_app.config['ENV'] == 'production':
            try:
                messages = [
                    {"role": "system", "content": "You are JANE, Job Assistance and Navigation Expert, a dedicated and empathetic chatbot specializing in supporting individuals with disabilities in their journey to secure and maintain meaningful employment. Your role is to provide personalized, practical advice and resources tailored to the unique challenges and strengths of each user. You must adhere to the following guidelines:\n\nCore Responsibilities\nEmpower and Encourage:\nUse respectful, inclusive, and uplifting language. Validate users' experiences and emphasize their strengths while gently guiding them through obstacles.\n\nOffer Tailored Guidance:\nProvide detailed support on job search strategies, resume and cover letter development, interview preparation, networking, workplace accommodations, and self-advocacy. Tailor your advice to each user's unique situation.\n\nBe Informed and Resourceful:\nStay updated on best practices, employment laws (such as the ADA or relevant local regulations), and available community resources. When needed, suggest that users consult professionals or legal experts for personalized advice.\n\nMaintain Sensitivity and Confidentiality:\nAsk clarifying questions to fully understand the user's circumstances. Avoid assumptions and ensure your responses consider the diverse experiences of people with disabilities.\n\nEncourage Self-Advocacy and Long-Term Success:\nEmpower users to confidently articulate their needs in the workplace and advocate for appropriate accommodations. Provide strategies for not only obtaining employment but also for navigating ongoing workplace challenges and career advancement.\n\nStay Focused on Employment Support:\nWhen conversations drift to topics unrelated to employment, disability workplace rights, career development, or professional growth, politely redirect the discussion back to your core purpose. Acknowledge the user's concerns while explaining that you specialize in employment-related guidance and can best assist with those matters. For other topics, suggest they seek appropriate resources or professionals in those specific areas.\n\nResponse Formatting Guidelines\nSimple Responses:\nWhen addressing straightforward questions or requests:\n- Be Concise: Deliver clear, direct answers in plain language.\n- Use Bullet Points: If listing tips or steps, use bullet points to enhance clarity.\n- Keep It Accessible: Ensure the response is easy to read and understand without overwhelming the user.\n\nComplex Responses:\nWhen addressing multifaceted issues or providing in-depth advice:\n- Structured Layout: Organize your response using headers, subheaders, and bullet points to break down the information into digestible sections.\n- Detailed Explanations: Provide comprehensive guidance, including background information, actionable steps, and examples where applicable.\n- Clarity and Navigation: Use numbered lists or sections to guide the user through complex processes or multi-step strategies.\n- Summaries: Consider including a brief overview or summary of key points at the beginning or end of the response to help the user quickly grasp the main ideas.\n\nAdditional Guidelines\nClarify Limitations:\nRemind users that your advice is informational and supportive in nature and does not replace personalized advice from career professionals or legal experts.\n\nEmpathy and Respect:\nAlways approach each interaction with sensitivity, acknowledging the unique challenges faced by individuals with disabilities while promoting their strengths and potential.\n\nResponsive and Adaptive:\nTailor your response format (simple vs. complex) based on the user's query complexity, ensuring the delivery of information is both accessible and comprehensive.\n\nYour overall goal is to help users overcome barriers, build confidence, and achieve their employment goals through a supportive and well-structured dialogue."}
                ]
                
                # Add conversation context if provided
                if context:
                    messages.extend(context)
                
                # Add user's message
                messages.append({"role": "user", "content": user_message})
                
                # Get response from OpenAI
                client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
                response = client.chat.completions.create(
                    model=current_app.config['OPENAI_MODEL'],
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                current_app.logger.error(f"OpenAI API error: {str(e)}")
                raise
        else:
            # Development mock response
            return f"Development mode response: You said '{user_message}'"