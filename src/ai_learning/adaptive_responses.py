"""
Adaptive Response System
Provides personalized and context-aware responses based on learned user patterns
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.models.ai_core import ConversationHistory, UserProfile, db
from src.ai_learning.pattern_recognition import PatternRecognitionEngine

class AdaptiveResponseSystem:
    """Generates personalized responses based on user patterns and preferences"""
    
    def __init__(self):
        self.pattern_engine = PatternRecognitionEngine()
        self.response_templates = self._load_response_templates()
        self.personality_traits = {
            'formal': 0.5,
            'friendly': 0.8,
            'concise': 0.6,
            'detailed': 0.4,
            'proactive': 0.7
        }
        
    def generate_adaptive_response(self, user_id: str, user_input: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a personalized response based on user patterns and context"""
        try:
            if context is None:
                context = {}
            
            # Get user patterns and preferences
            user_patterns = self.pattern_engine.analyze_user_patterns(user_id, days_back=7)
            user_profile = self._get_user_profile(user_id)
            
            # Predict user intent
            intent_prediction = self.pattern_engine.predict_user_intent(user_input, context)
            
            # Generate base response
            base_response = self._generate_base_response(intent_prediction, user_input, context)
            
            # Adapt response based on user patterns
            adapted_response = self._adapt_response_to_user(
                base_response, user_patterns, user_profile, context
            )
            
            # Add proactive suggestions if appropriate
            if self._should_add_suggestions(user_patterns, context):
                suggestions = self._generate_proactive_suggestions(user_id, user_patterns, context)
                adapted_response['suggestions'] = suggestions
            
            # Store interaction for future learning
            self._store_interaction(user_id, user_input, adapted_response, context)
            
            return {
                'status': 'success',
                'response': adapted_response,
                'intent': intent_prediction.get('predicted_intent'),
                'confidence': intent_prediction.get('confidence'),
                'personalization_applied': True
            }
            
        except Exception as e:
            # Fallback to basic response
            return {
                'status': 'success',
                'response': {
                    'text': "I understand you need help. Let me assist you with that.",
                    'type': 'fallback'
                },
                'personalization_applied': False,
                'error': str(e)
            }
    
    def _generate_base_response(self, intent_prediction: Dict[str, Any], 
                              user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate base response based on intent prediction"""
        intent = intent_prediction.get('predicted_intent', 'general_conversation')
        confidence = intent_prediction.get('confidence', 0.5)
        
        response_templates = self.response_templates.get(intent, {})
        
        if confidence > 0.7 and response_templates:
            # High confidence - use specific template
            template_type = 'high_confidence'
            templates = response_templates.get(template_type, response_templates.get('default', []))
        elif confidence > 0.4 and response_templates:
            # Medium confidence - use cautious template
            template_type = 'medium_confidence'
            templates = response_templates.get(template_type, response_templates.get('default', []))
        else:
            # Low confidence - ask for clarification
            template_type = 'low_confidence'
            templates = response_templates.get(template_type, [
                "I'm not entirely sure what you'd like me to do. Could you provide more details?",
                "Let me make sure I understand correctly. What specifically would you like me to help with?"
            ])
        
        # Select appropriate template
        if templates:
            base_text = random.choice(templates)
        else:
            base_text = "I'm here to help! What would you like me to do?"
        
        return {
            'text': base_text,
            'intent': intent,
            'confidence': confidence,
            'template_type': template_type,
            'requires_action': intent in ['device_control', 'climate_control', 'security_control', 'routine_activation']
        }
    
    def _adapt_response_to_user(self, base_response: Dict[str, Any], 
                              user_patterns: Dict[str, Any], user_profile: Dict[str, Any],
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt the response based on user patterns and preferences"""
        adapted_response = base_response.copy()
        
        if user_patterns.get('status') != 'success':
            return adapted_response
        
        patterns = user_patterns.get('patterns', {})
        
        # Adapt based on communication style
        comm_patterns = patterns.get('preference_patterns', {}).get('communication_style', [])
        if comm_patterns:
            dominant_style = comm_patterns[0][0] if comm_patterns[0] else 'casual'
            adapted_response['text'] = self._adjust_communication_style(
                adapted_response['text'], dominant_style
            )
        
        # Adapt based on time of day
        current_hour = datetime.utcnow().hour
        time_context = self._get_time_context(current_hour)
        adapted_response['text'] = self._add_time_awareness(
            adapted_response['text'], time_context, patterns
        )
        
        # Add personalization based on routine patterns
        routine_patterns = patterns.get('routine_patterns', {})
        if routine_patterns and self._is_routine_time(current_hour, routine_patterns):
            adapted_response['text'] = self._add_routine_awareness(
                adapted_response['text'], current_hour, routine_patterns
            )
        
        # Adapt based on device usage patterns
        device_patterns = patterns.get('device_usage_patterns', {})
        if device_patterns and adapted_response.get('requires_action'):
            adapted_response = self._add_device_context(adapted_response, device_patterns)
        
        # Add emotional intelligence
        mood_patterns = patterns.get('context_patterns', {}).get('mood_patterns', {})
        if mood_patterns:
            adapted_response['text'] = self._add_emotional_awareness(
                adapted_response['text'], mood_patterns
            )
        
        return adapted_response
    
    def _adjust_communication_style(self, text: str, style: str) -> str:
        """Adjust response text based on user's communication style"""
        if style == 'concise':
            # Make response more concise
            if len(text.split()) > 10:
                # Simplify long responses
                if 'I\'ll' in text:
                    return text.split('.')[0] + '.'
                return text[:50] + '...' if len(text) > 50 else text
        
        elif style == 'polite':
            # Add polite language
            if not any(word in text.lower() for word in ['please', 'thank', 'certainly']):
                text = text.replace('I\'ll', 'I\'ll be happy to')
                text = text.replace('I can', 'I\'d be glad to')
        
        elif style == 'urgent':
            # Make response more direct and immediate
            text = text.replace('I\'ll', 'I\'m')
            text = text.replace('Let me', 'I\'m immediately')
        
        return text
    
    def _add_time_awareness(self, text: str, time_context: str, patterns: Dict[str, Any]) -> str:
        """Add time-aware elements to the response"""
        temporal_patterns = patterns.get('temporal_patterns', {})
        
        if time_context == 'morning' and temporal_patterns.get('most_active_period') == 'morning':
            if 'good morning' not in text.lower():
                text = f"Good morning! {text}"
        
        elif time_context == 'evening' and temporal_patterns.get('most_active_period') == 'evening':
            if 'good evening' not in text.lower():
                text = f"Good evening! {text}"
        
        elif time_context == 'night':
            text = text.replace('I\'ll', 'I\'ll quietly')
            
        return text
    
    def _add_routine_awareness(self, text: str, current_hour: int, 
                             routine_patterns: Dict[str, Any]) -> str:
        """Add routine awareness to responses"""
        morning_routine = routine_patterns.get('morning_routine', {})
        evening_routine = routine_patterns.get('evening_routine', {})
        
        if 6 <= current_hour <= 10 and morning_routine:
            # Morning routine time
            top_morning_activity = list(morning_routine.keys())[0] if morning_routine else None
            if top_morning_activity and 'lighting' in top_morning_activity:
                text += " I notice you usually adjust lighting in the morning. Would you like me to optimize the lighting as well?"
        
        elif 18 <= current_hour <= 22 and evening_routine:
            # Evening routine time
            top_evening_activity = list(evening_routine.keys())[0] if evening_routine else None
            if top_evening_activity and 'security' in top_evening_activity:
                text += " Since it's evening, would you also like me to check your security settings?"
        
        return text
    
    def _add_device_context(self, response: Dict[str, Any], 
                          device_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Add device-specific context to responses"""
        most_used_category = device_patterns.get('most_used_category')
        
        if most_used_category:
            category_name = most_used_category[0] if isinstance(most_used_category, tuple) else most_used_category
            
            if category_name == 'light' and response['intent'] == 'device_control':
                response['text'] += f" I see you frequently use lighting controls. I can also adjust brightness and color if needed."
            
            elif category_name == 'thermostat' and response['intent'] == 'climate_control':
                response['text'] += f" Based on your usage patterns, I'll optimize the temperature for your comfort."
        
        return response
    
    def _add_emotional_awareness(self, text: str, mood_patterns: Dict[str, Any]) -> str:
        """Add emotional intelligence to responses"""
        if not mood_patterns:
            return text
        
        dominant_mood = max(mood_patterns.items(), key=lambda x: x[1])[0]
        
        if dominant_mood == 'positive':
            text = text.replace('I\'ll', 'I\'ll happily')
        elif dominant_mood == 'urgent':
            text = text.replace('I\'ll', 'I\'ll immediately')
        elif dominant_mood == 'negative':
            text = f"I understand this might be frustrating. {text}"
        
        return text
    
    def _generate_proactive_suggestions(self, user_id: str, user_patterns: Dict[str, Any], 
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate proactive suggestions based on patterns"""
        suggestions = []
        
        if user_patterns.get('status') != 'success':
            return suggestions
        
        patterns = user_patterns.get('patterns', {})
        current_hour = datetime.utcnow().hour
        
        # Routine-based suggestions
        routine_patterns = patterns.get('routine_patterns', {})
        if self._is_routine_time(current_hour, routine_patterns):
            suggestions.extend(self._get_routine_suggestions(current_hour, routine_patterns))
        
        # Energy optimization suggestions
        device_patterns = patterns.get('device_usage_patterns', {})
        if device_patterns.get('automation_potential', 0) > 0.7:
            suggestions.append({
                'type': 'automation',
                'title': 'Automation Opportunity',
                'description': 'I noticed patterns in your device usage. Would you like me to create an automation?',
                'action': 'create_automation'
            })
        
        # Weather-based suggestions (if weather context available)
        if context.get('weather'):
            weather_suggestions = self._get_weather_suggestions(context['weather'], patterns)
            suggestions.extend(weather_suggestions)
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _should_add_suggestions(self, user_patterns: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Determine if proactive suggestions should be added"""
        if user_patterns.get('status') != 'success':
            return False
        
        patterns = user_patterns.get('patterns', {})
        
        # Add suggestions if user has established patterns
        temporal_patterns = patterns.get('temporal_patterns', {})
        return temporal_patterns.get('activity_score', 0) > 15
    
    def _get_time_context(self, hour: int) -> str:
        """Get time context for the current hour"""
        if 6 <= hour <= 11:
            return 'morning'
        elif 12 <= hour <= 17:
            return 'afternoon'
        elif 18 <= hour <= 22:
            return 'evening'
        else:
            return 'night'
    
    def _is_routine_time(self, current_hour: int, routine_patterns: Dict[str, Any]) -> bool:
        """Check if current time matches user's routine patterns"""
        morning_routine = routine_patterns.get('morning_routine', {})
        evening_routine = routine_patterns.get('evening_routine', {})
        
        return (6 <= current_hour <= 10 and morning_routine) or \
               (18 <= current_hour <= 22 and evening_routine)
    
    def _get_routine_suggestions(self, current_hour: int, 
                               routine_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get routine-based suggestions"""
        suggestions = []
        
        if 6 <= current_hour <= 10:
            morning_routine = routine_patterns.get('morning_routine', {})
            if morning_routine:
                top_activity = list(morning_routine.keys())[0]
                suggestions.append({
                    'type': 'routine',
                    'title': 'Morning Routine',
                    'description': f'Would you like me to start your usual morning routine ({top_activity})?',
                    'action': 'activate_morning_routine'
                })
        
        elif 18 <= current_hour <= 22:
            evening_routine = routine_patterns.get('evening_routine', {})
            if evening_routine:
                top_activity = list(evening_routine.keys())[0]
                suggestions.append({
                    'type': 'routine',
                    'title': 'Evening Routine',
                    'description': f'Time for your evening routine ({top_activity})?',
                    'action': 'activate_evening_routine'
                })
        
        return suggestions
    
    def _get_weather_suggestions(self, weather: Dict[str, Any], 
                               patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get weather-based suggestions"""
        suggestions = []
        
        temperature = weather.get('temperature', 70)
        condition = weather.get('condition', 'clear')
        
        # Temperature-based suggestions
        temp_preferences = patterns.get('preference_patterns', {}).get('temperature_preferences', [])
        if temp_preferences:
            preferred_temp = temp_preferences[0][0] if temp_preferences[0] else 72
            
            if abs(temperature - preferred_temp) > 5:
                suggestions.append({
                    'type': 'climate',
                    'title': 'Climate Adjustment',
                    'description': f'It\'s {temperature}°F outside. Adjust indoor temperature to {preferred_temp}°F?',
                    'action': 'adjust_climate'
                })
        
        # Weather condition suggestions
        if condition in ['rain', 'storm']:
            suggestions.append({
                'type': 'security',
                'title': 'Weather Alert',
                'description': 'Storm detected. Would you like me to secure outdoor devices?',
                'action': 'weather_security'
            })
        
        return suggestions
    
    def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            if profile:
                return {
                    'preferences': profile.get_preferences(),
                    'settings': profile.get_settings()
                }
            return {}
        except:
            return {}
    
    def _store_interaction(self, user_id: str, user_input: str, 
                         response: Dict[str, Any], context: Dict[str, Any]):
        """Store interaction for future learning"""
        try:
            conversation = ConversationHistory(
                user_id=user_id,
                session_id=f"adaptive_{datetime.utcnow().timestamp()}",
                user_input=user_input,
                ai_response=response.get('text', ''),
                intent=response.get('intent'),
                confidence_score=response.get('confidence')
            )
            conversation.set_context_data(context)
            db.session.add(conversation)
            db.session.commit()
        except Exception as e:
            # Log error but don't fail the response
            print(f"Error storing interaction: {e}")
    
    def _load_response_templates(self) -> Dict[str, Any]:
        """Load response templates for different intents and confidence levels"""
        return {
            'device_control': {
                'high_confidence': [
                    "I'll take care of that right away.",
                    "Consider it done!",
                    "I'm adjusting that for you now.",
                    "Perfect, I'll handle that immediately."
                ],
                'medium_confidence': [
                    "I believe you want me to control a device. Let me do that for you.",
                    "I think I understand. I'll make that adjustment.",
                    "I'll try to help with that device control."
                ],
                'low_confidence': [
                    "I want to help with device control, but could you be more specific about which device?",
                    "Which device would you like me to control?"
                ]
            },
            'climate_control': {
                'high_confidence': [
                    "I'll adjust the temperature for you.",
                    "Setting the climate to your preference now.",
                    "I'm optimizing the temperature for your comfort."
                ],
                'medium_confidence': [
                    "I'll help with the climate control.",
                    "Let me adjust the temperature settings."
                ],
                'low_confidence': [
                    "I can help with climate control. What temperature would you prefer?"
                ]
            },
            'information_request': {
                'high_confidence': [
                    "Let me get that information for you.",
                    "I'll look that up right away.",
                    "Here's what I found about that."
                ],
                'medium_confidence': [
                    "I'll try to find that information.",
                    "Let me see what I can tell you about that."
                ],
                'low_confidence': [
                    "I'd be happy to help with information. Could you be more specific about what you need?"
                ]
            },
            'media_control': {
                'high_confidence': [
                    "I'll start playing that for you.",
                    "Setting up your media now.",
                    "I'll get your entertainment ready."
                ],
                'medium_confidence': [
                    "I'll help with media control.",
                    "Let me set up your entertainment."
                ],
                'low_confidence': [
                    "I can help with media. What would you like to play?"
                ]
            },
            'security_control': {
                'high_confidence': [
                    "I'll secure that for you immediately.",
                    "Updating security settings now.",
                    "I'm taking care of your security request."
                ],
                'medium_confidence': [
                    "I'll help with security settings.",
                    "Let me update your security configuration."
                ],
                'low_confidence': [
                    "I can help with security. Which specific setting would you like to change?"
                ]
            },
            'routine_activation': {
                'high_confidence': [
                    "Activating your routine now.",
                    "I'll start that routine for you.",
                    "Setting up your personalized routine."
                ],
                'medium_confidence': [
                    "I'll help activate that routine.",
                    "Let me set up that routine for you."
                ],
                'low_confidence': [
                    "Which routine would you like me to activate?"
                ]
            },
            'general_conversation': {
                'default': [
                    "I'm here to help! What would you like me to do?",
                    "How can I assist you today?",
                    "What can I help you with?",
                    "I'm ready to help. What do you need?"
                ]
            }
        }

