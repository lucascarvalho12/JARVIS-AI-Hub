"""
Pattern Recognition Module
Analyzes user behavior patterns and device usage to improve AI responses
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from src.models.ai_core import ConversationHistory, TaskExecution, DeviceRegistry, db

class PatternRecognitionEngine:
    """Analyzes patterns in user behavior and device usage"""
    
    def __init__(self):
        self.pattern_cache = {}
        self.learning_threshold = 5  # Minimum occurrences to establish a pattern
        self.confidence_threshold = 0.7  # Minimum confidence for pattern recognition
        
    def analyze_user_patterns(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze comprehensive user behavior patterns"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get conversation history
            conversations = ConversationHistory.query.filter(
                ConversationHistory.user_id == user_id,
                ConversationHistory.timestamp >= start_date
            ).all()
            
            # Get task execution history
            tasks = TaskExecution.query.filter(
                TaskExecution.user_id == user_id,
                TaskExecution.created_at >= start_date
            ).all()
            
            patterns = {
                'temporal_patterns': self._analyze_temporal_patterns(conversations, tasks),
                'command_patterns': self._analyze_command_patterns(conversations),
                'device_usage_patterns': self._analyze_device_usage_patterns(user_id, start_date),
                'routine_patterns': self._analyze_routine_patterns(conversations, tasks),
                'preference_patterns': self._analyze_preference_patterns(conversations),
                'context_patterns': self._analyze_context_patterns(conversations)
            }
            
            return {
                'status': 'success',
                'user_id': user_id,
                'analysis_period': f'{days_back} days',
                'patterns': patterns,
                'confidence_score': self._calculate_overall_confidence(patterns),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_temporal_patterns(self, conversations: List, tasks: List) -> Dict[str, Any]:
        """Analyze when user is most active and what they do at different times"""
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        weekly_activity = defaultdict(int)
        
        # Analyze conversation patterns
        for conv in conversations:
            hour = conv.timestamp.hour
            day = conv.timestamp.strftime('%A')
            week = conv.timestamp.isocalendar()[1]
            
            hourly_activity[hour] += 1
            daily_activity[day] += 1
            weekly_activity[week] += 1
        
        # Analyze task patterns
        for task in tasks:
            hour = task.created_at.hour
            day = task.created_at.strftime('%A')
            week = task.created_at.isocalendar()[1]
            
            hourly_activity[hour] += 1
            daily_activity[day] += 1
            weekly_activity[week] += 1
        
        # Find peak activity times
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1]) if hourly_activity else (12, 0)
        peak_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else ('Monday', 0)
        
        return {
            'peak_hour': peak_hour[0],
            'peak_day': peak_day[0],
            'hourly_distribution': dict(hourly_activity),
            'daily_distribution': dict(daily_activity),
            'activity_score': sum(hourly_activity.values()),
            'most_active_period': self._determine_active_period(hourly_activity)
        }
    
    def _analyze_command_patterns(self, conversations: List) -> Dict[str, Any]:
        """Analyze patterns in user commands and requests"""
        command_frequency = Counter()
        command_sequences = []
        intent_patterns = Counter()
        
        for conv in conversations:
            user_input = conv.user_input.lower()
            
            # Extract command types
            if any(word in user_input for word in ['turn on', 'switch on', 'activate']):
                command_frequency['turn_on'] += 1
                intent_patterns['device_control'] += 1
            elif any(word in user_input for word in ['turn off', 'switch off', 'deactivate']):
                command_frequency['turn_off'] += 1
                intent_patterns['device_control'] += 1
            elif any(word in user_input for word in ['set temperature', 'adjust temperature']):
                command_frequency['climate_control'] += 1
                intent_patterns['climate'] += 1
            elif any(word in user_input for word in ['play music', 'play song']):
                command_frequency['media_control'] += 1
                intent_patterns['entertainment'] += 1
            elif any(word in user_input for word in ['what is', 'tell me', 'how is']):
                command_frequency['information_request'] += 1
                intent_patterns['information'] += 1
            
            # Track command sequences (for learning automation opportunities)
            command_sequences.append(user_input)
        
        # Find most common commands
        top_commands = command_frequency.most_common(5)
        top_intents = intent_patterns.most_common(3)
        
        return {
            'most_common_commands': dict(top_commands),
            'most_common_intents': dict(top_intents),
            'total_commands': sum(command_frequency.values()),
            'command_diversity': len(command_frequency),
            'automation_opportunities': self._find_automation_opportunities(command_sequences)
        }
    
    def _analyze_device_usage_patterns(self, user_id: str, start_date: datetime) -> Dict[str, Any]:
        """Analyze patterns in device usage and control"""
        devices = DeviceRegistry.query.filter_by(user_id=user_id).all()
        
        device_usage = {}
        device_categories = Counter()
        
        for device in devices:
            device_categories[device.device_category] += 1
            
            # Simulate usage patterns (in production, get from device logs)
            usage_score = self._calculate_device_usage_score(device)
            device_usage[device.device_id] = {
                'device_name': device.device_name,
                'category': device.device_category,
                'usage_score': usage_score,
                'last_used': device.last_seen.isoformat() if device.last_seen else None
            }
        
        return {
            'total_devices': len(devices),
            'device_categories': dict(device_categories),
            'device_usage': device_usage,
            'most_used_category': device_categories.most_common(1)[0] if device_categories else None,
            'automation_potential': self._assess_automation_potential(device_usage)
        }
    
    def _analyze_routine_patterns(self, conversations: List, tasks: List) -> Dict[str, Any]:
        """Identify daily routines and recurring patterns"""
        morning_activities = []
        evening_activities = []
        routine_sequences = defaultdict(list)
        
        # Analyze conversations by time of day
        for conv in conversations:
            hour = conv.timestamp.hour
            activity = self._extract_activity_from_input(conv.user_input)
            
            if 6 <= hour <= 10:  # Morning
                morning_activities.append(activity)
            elif 18 <= hour <= 23:  # Evening
                evening_activities.append(activity)
            
            # Group activities by hour for routine detection
            routine_sequences[hour].append(activity)
        
        # Find common morning and evening routines
        morning_routine = Counter(morning_activities).most_common(3)
        evening_routine = Counter(evening_activities).most_common(3)
        
        return {
            'morning_routine': dict(morning_routine),
            'evening_routine': dict(evening_routine),
            'routine_consistency': self._calculate_routine_consistency(routine_sequences),
            'suggested_automations': self._suggest_routine_automations(morning_routine, evening_routine)
        }
    
    def _analyze_preference_patterns(self, conversations: List) -> Dict[str, Any]:
        """Analyze user preferences from conversation history"""
        preferences = {
            'temperature_preferences': [],
            'lighting_preferences': [],
            'music_preferences': [],
            'communication_style': [],
            'response_preferences': []
        }
        
        for conv in conversations:
            user_input = conv.user_input.lower()
            ai_response = conv.ai_response.lower()
            
            # Extract temperature preferences
            if 'temperature' in user_input:
                temp_match = self._extract_temperature_preference(user_input)
                if temp_match:
                    preferences['temperature_preferences'].append(temp_match)
            
            # Extract lighting preferences
            if 'light' in user_input or 'bright' in user_input or 'dim' in user_input:
                light_pref = self._extract_lighting_preference(user_input)
                if light_pref:
                    preferences['lighting_preferences'].append(light_pref)
            
            # Analyze communication style
            style = self._analyze_communication_style(user_input)
            preferences['communication_style'].append(style)
        
        # Process preferences to find patterns
        processed_preferences = {}
        for pref_type, pref_list in preferences.items():
            if pref_list:
                processed_preferences[pref_type] = Counter(pref_list).most_common(3)
            else:
                processed_preferences[pref_type] = []
        
        return processed_preferences
    
    def _analyze_context_patterns(self, conversations: List) -> Dict[str, Any]:
        """Analyze contextual patterns in user interactions"""
        location_contexts = Counter()
        time_contexts = Counter()
        device_contexts = Counter()
        mood_contexts = Counter()
        
        for conv in conversations:
            # Extract context from conversation data
            context_data = conv.get_context_data() if hasattr(conv, 'get_context_data') else {}
            
            if 'location' in context_data:
                location_contexts[context_data['location']] += 1
            
            if 'device_type' in context_data:
                device_contexts[context_data['device_type']] += 1
            
            # Analyze time context
            hour = conv.timestamp.hour
            if 6 <= hour <= 12:
                time_contexts['morning'] += 1
            elif 12 <= hour <= 18:
                time_contexts['afternoon'] += 1
            elif 18 <= hour <= 22:
                time_contexts['evening'] += 1
            else:
                time_contexts['night'] += 1
            
            # Simple mood analysis based on language patterns
            mood = self._analyze_mood_from_text(conv.user_input)
            mood_contexts[mood] += 1
        
        return {
            'location_patterns': dict(location_contexts.most_common(5)),
            'time_patterns': dict(time_contexts),
            'device_patterns': dict(device_contexts.most_common(5)),
            'mood_patterns': dict(mood_contexts.most_common(3)),
            'context_diversity': len(location_contexts) + len(device_contexts)
        }
    
    def predict_user_intent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict user intent based on learned patterns"""
        try:
            if context is None:
                context = {}
            
            # Simple intent prediction based on keywords and patterns
            user_input_lower = user_input.lower()
            
            # Intent scoring
            intent_scores = {
                'device_control': 0,
                'information_request': 0,
                'climate_control': 0,
                'media_control': 0,
                'security_control': 0,
                'routine_activation': 0
            }
            
            # Device control patterns
            if any(word in user_input_lower for word in ['turn', 'switch', 'activate', 'deactivate']):
                intent_scores['device_control'] += 0.8
            
            # Information request patterns
            if any(word in user_input_lower for word in ['what', 'how', 'when', 'where', 'tell me']):
                intent_scores['information_request'] += 0.7
            
            # Climate control patterns
            if any(word in user_input_lower for word in ['temperature', 'heat', 'cool', 'thermostat']):
                intent_scores['climate_control'] += 0.9
            
            # Media control patterns
            if any(word in user_input_lower for word in ['play', 'music', 'song', 'volume']):
                intent_scores['media_control'] += 0.8
            
            # Security patterns
            if any(word in user_input_lower for word in ['lock', 'unlock', 'security', 'alarm']):
                intent_scores['security_control'] += 0.9
            
            # Routine patterns
            if any(word in user_input_lower for word in ['good morning', 'good night', 'movie time']):
                intent_scores['routine_activation'] += 0.9
            
            # Find highest scoring intent
            predicted_intent = max(intent_scores.items(), key=lambda x: x[1])
            
            return {
                'status': 'success',
                'predicted_intent': predicted_intent[0],
                'confidence': predicted_intent[1],
                'all_scores': intent_scores,
                'context_used': context
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def suggest_automations(self, user_id: str) -> Dict[str, Any]:
        """Suggest automation opportunities based on learned patterns"""
        try:
            patterns = self.analyze_user_patterns(user_id)
            
            if patterns['status'] != 'success':
                return patterns
            
            suggestions = []
            
            # Routine-based automations
            morning_routine = patterns['patterns']['routine_patterns']['morning_routine']
            if morning_routine:
                suggestions.append({
                    'type': 'morning_automation',
                    'title': 'Morning Routine Automation',
                    'description': 'Automate your morning routine based on detected patterns',
                    'actions': list(morning_routine.keys())[:3],
                    'confidence': 0.8
                })
            
            evening_routine = patterns['patterns']['routine_patterns']['evening_routine']
            if evening_routine:
                suggestions.append({
                    'type': 'evening_automation',
                    'title': 'Evening Routine Automation',
                    'description': 'Automate your evening routine based on detected patterns',
                    'actions': list(evening_routine.keys())[:3],
                    'confidence': 0.8
                })
            
            # Device usage automations
            device_patterns = patterns['patterns']['device_usage_patterns']
            if device_patterns['automation_potential'] > 0.7:
                suggestions.append({
                    'type': 'device_automation',
                    'title': 'Smart Device Automation',
                    'description': 'Automate frequently used device combinations',
                    'confidence': device_patterns['automation_potential']
                })
            
            # Time-based automations
            temporal_patterns = patterns['patterns']['temporal_patterns']
            if temporal_patterns['activity_score'] > 10:
                suggestions.append({
                    'type': 'time_based_automation',
                    'title': 'Time-Based Automation',
                    'description': f'Automate actions during your peak activity time ({temporal_patterns["peak_hour"]}:00)',
                    'confidence': 0.7
                })
            
            return {
                'status': 'success',
                'user_id': user_id,
                'suggestions': suggestions,
                'total_suggestions': len(suggestions)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # Helper methods
    def _determine_active_period(self, hourly_activity: Dict[int, int]) -> str:
        """Determine the most active period of the day"""
        if not hourly_activity:
            return 'unknown'
        
        morning_activity = sum(hourly_activity.get(h, 0) for h in range(6, 12))
        afternoon_activity = sum(hourly_activity.get(h, 0) for h in range(12, 18))
        evening_activity = sum(hourly_activity.get(h, 0) for h in range(18, 23))
        
        max_activity = max(morning_activity, afternoon_activity, evening_activity)
        
        if max_activity == morning_activity:
            return 'morning'
        elif max_activity == afternoon_activity:
            return 'afternoon'
        else:
            return 'evening'
    
    def _find_automation_opportunities(self, command_sequences: List[str]) -> List[str]:
        """Find opportunities for automation based on command sequences"""
        # Simple pattern detection for consecutive commands
        opportunities = []
        
        # Look for repeated sequences
        sequence_patterns = Counter()
        for i in range(len(command_sequences) - 1):
            sequence = f"{command_sequences[i]} -> {command_sequences[i+1]}"
            sequence_patterns[sequence] += 1
        
        # Suggest automations for frequently occurring sequences
        for sequence, count in sequence_patterns.most_common(3):
            if count >= self.learning_threshold:
                opportunities.append(f"Automate: {sequence}")
        
        return opportunities
    
    def _calculate_device_usage_score(self, device: DeviceRegistry) -> float:
        """Calculate a usage score for a device based on various factors"""
        # Simple scoring based on last seen and device type
        if not device.last_seen:
            return 0.0
        
        days_since_use = (datetime.utcnow() - device.last_seen).days
        
        # Higher score for recently used devices
        if days_since_use == 0:
            return 1.0
        elif days_since_use <= 7:
            return 0.8
        elif days_since_use <= 30:
            return 0.5
        else:
            return 0.2
    
    def _assess_automation_potential(self, device_usage: Dict[str, Any]) -> float:
        """Assess the potential for device automation"""
        if not device_usage:
            return 0.0
        
        # Calculate based on number of devices and usage patterns
        total_devices = len(device_usage)
        active_devices = sum(1 for d in device_usage.values() if d['usage_score'] > 0.5)
        
        if total_devices == 0:
            return 0.0
        
        return min(active_devices / total_devices, 1.0)
    
    def _calculate_routine_consistency(self, routine_sequences: Dict[int, List[str]]) -> float:
        """Calculate how consistent user routines are"""
        if not routine_sequences:
            return 0.0
        
        consistency_scores = []
        for hour, activities in routine_sequences.items():
            if len(activities) > 1:
                # Calculate consistency as the frequency of the most common activity
                activity_counts = Counter(activities)
                most_common_count = activity_counts.most_common(1)[0][1]
                consistency = most_common_count / len(activities)
                consistency_scores.append(consistency)
        
        return np.mean(consistency_scores) if consistency_scores else 0.0
    
    def _suggest_routine_automations(self, morning_routine: List[Tuple], evening_routine: List[Tuple]) -> List[str]:
        """Suggest automations based on routine patterns"""
        suggestions = []
        
        if morning_routine:
            top_morning = morning_routine[0][0]
            suggestions.append(f"Morning automation: {top_morning}")
        
        if evening_routine:
            top_evening = evening_routine[0][0]
            suggestions.append(f"Evening automation: {top_evening}")
        
        return suggestions
    
    def _extract_activity_from_input(self, user_input: str) -> str:
        """Extract activity type from user input"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['light', 'lamp']):
            return 'lighting_control'
        elif any(word in user_input_lower for word in ['temperature', 'heat', 'cool']):
            return 'climate_control'
        elif any(word in user_input_lower for word in ['music', 'play', 'song']):
            return 'media_control'
        elif any(word in user_input_lower for word in ['lock', 'security']):
            return 'security_control'
        else:
            return 'general_command'
    
    def _extract_temperature_preference(self, user_input: str) -> Optional[int]:
        """Extract temperature preference from user input"""
        import re
        temp_match = re.search(r'(\d+)\s*(?:degrees?|°)', user_input)
        return int(temp_match.group(1)) if temp_match else None
    
    def _extract_lighting_preference(self, user_input: str) -> Optional[str]:
        """Extract lighting preference from user input"""
        if 'bright' in user_input or 'full' in user_input:
            return 'bright'
        elif 'dim' in user_input or 'low' in user_input:
            return 'dim'
        elif 'medium' in user_input:
            return 'medium'
        return None
    
    def _analyze_communication_style(self, user_input: str) -> str:
        """Analyze user's communication style"""
        if len(user_input.split()) <= 3:
            return 'concise'
        elif any(word in user_input.lower() for word in ['please', 'thank', 'could you']):
            return 'polite'
        elif '!' in user_input or user_input.isupper():
            return 'urgent'
        else:
            return 'casual'
    
    def _analyze_mood_from_text(self, text: str) -> str:
        """Simple mood analysis from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['happy', 'great', 'awesome', 'good']):
            return 'positive'
        elif any(word in text_lower for word in ['sad', 'bad', 'terrible', 'awful']):
            return 'negative'
        elif any(word in text_lower for word in ['urgent', 'emergency', 'help', 'quick']):
            return 'urgent'
        else:
            return 'neutral'
    
    def _calculate_overall_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall confidence score for pattern analysis"""
        # Simple confidence calculation based on data availability
        confidence_factors = []
        
        # Temporal patterns confidence
        temporal = patterns.get('temporal_patterns', {})
        if temporal.get('activity_score', 0) > 10:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)
        
        # Command patterns confidence
        command = patterns.get('command_patterns', {})
        if command.get('total_commands', 0) > 20:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)
        
        # Device usage confidence
        device = patterns.get('device_usage_patterns', {})
        if device.get('total_devices', 0) > 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        return np.mean(confidence_factors) if confidence_factors else 0.5

