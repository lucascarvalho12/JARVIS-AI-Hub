"""
Research Agent (RA) for JARVIS AI Hub Self-Development Module

This module provides autonomous research capabilities, allowing JARVIS to
proactively search for and process new information relevant to its self-development goals.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    The Research Agent autonomously searches for and processes new information
    relevant to JARVIS's self-development goals, including algorithms, best practices,
    security vulnerabilities, and emerging technologies.
    """

    def __init__(self, knowledge_repository=None, omni_search_tool=None):
        self.knowledge_repository = knowledge_repository
        self.omni_search_tool = omni_search_tool
        self.client = OpenAI()  # Uses environment variables for API key
        self.research_history = []
        self.research_priorities = {
            'ai_development': 0.9,
            'code_optimization': 0.8,
            'security_vulnerabilities': 0.95,
            'new_algorithms': 0.7,
            'programming_best_practices': 0.6,
            'emerging_technologies': 0.5
        }
        self.last_research_time = {}
        logger.info("Research Agent initialized")

    def conduct_targeted_research(self, topic: str, depth: str = "medium", 
                                max_sources: int = 10) -> Dict[str, Any]:
        """
        Conducts targeted research on a specific topic.
        
        Args:
            topic: The research topic or question
            depth: Research depth ("shallow", "medium", "deep")
            max_sources: Maximum number of sources to analyze
            
        Returns:
            Dictionary containing research results and analysis
        """
        logger.info(f"Conducting targeted research on: {topic} (depth: {depth})")
        
        research_session = {
            'topic': topic,
            'depth': depth,
            'max_sources': max_sources,
            'timestamp': datetime.now().isoformat(),
            'status': 'initiated',
            'sources_found': [],
            'key_findings': [],
            'actionable_insights': [],
            'confidence_score': 0.0
        }

        try:
            # Step 1: Generate search queries
            search_queries = self._generate_search_queries(topic, depth)
            research_session['search_queries'] = search_queries
            
            # Step 2: Execute searches and collect sources
            all_sources = []
            for query in search_queries[:3]:  # Limit to 3 queries to avoid overwhelming
                sources = self._execute_search(query, max_results=max_sources//len(search_queries))
                all_sources.extend(sources)
            
            research_session['sources_found'] = all_sources[:max_sources]
            research_session['total_sources'] = len(all_sources)
            
            # Step 3: Analyze and synthesize findings
            if all_sources:
                analysis_result = self._analyze_sources(topic, all_sources[:max_sources])
                research_session.update(analysis_result)
                research_session['status'] = 'completed'
            else:
                research_session['status'] = 'no_sources_found'
                research_session['error'] = 'No relevant sources found for the topic'
            
            # Step 4: Store results
            self._store_research_results(research_session)
            
        except Exception as e:
            logger.error(f"Research failed for topic '{topic}': {str(e)}")
            research_session['status'] = 'failed'
            research_session['error'] = str(e)
        
        return research_session

    def conduct_autonomous_research(self, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Conducts autonomous research based on current system needs and priorities.
        
        Args:
            focus_areas: Optional list of specific areas to focus on
            
        Returns:
            Dictionary containing autonomous research results
        """
        logger.info("Conducting autonomous research session")
        
        autonomous_session = {
            'session_type': 'autonomous',
            'timestamp': datetime.now().isoformat(),
            'focus_areas': focus_areas or list(self.research_priorities.keys()),
            'research_topics': [],
            'total_findings': 0,
            'high_priority_findings': 0
        }

        try:
            # Determine research topics based on priorities and system needs
            research_topics = self._determine_research_topics(focus_areas)
            autonomous_session['research_topics'] = research_topics
            
            # Conduct research on each topic
            all_findings = []
            for topic_info in research_topics:
                topic_research = self.conduct_targeted_research(
                    topic_info['topic'], 
                    depth=topic_info.get('depth', 'medium'),
                    max_sources=topic_info.get('max_sources', 5)
                )
                
                if topic_research['status'] == 'completed':
                    all_findings.extend(topic_research.get('key_findings', []))
                    if topic_info.get('priority', 0) > 0.7:
                        autonomous_session['high_priority_findings'] += len(topic_research.get('key_findings', []))
            
            autonomous_session['total_findings'] = len(all_findings)
            autonomous_session['status'] = 'completed'
            
            # Generate summary insights
            if all_findings:
                summary_insights = self._generate_summary_insights(all_findings)
                autonomous_session['summary_insights'] = summary_insights
            
        except Exception as e:
            logger.error(f"Autonomous research session failed: {str(e)}")
            autonomous_session['status'] = 'failed'
            autonomous_session['error'] = str(e)
        
        return autonomous_session

    def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """
        Generates appropriate search queries for a given topic and depth.
        
        Args:
            topic: The research topic
            depth: Research depth level
            
        Returns:
            List of search query strings
        """
        # Use LLM to generate contextually appropriate search queries
        prompt = f"""
Generate {3 if depth == 'shallow' else 5 if depth == 'medium' else 8} search queries for researching the topic: "{topic}"

The queries should be:
- Specific enough to find relevant technical information
- Varied to cover different aspects of the topic
- Suitable for academic and technical sources
- Focused on recent developments and best practices

Research depth: {depth}

Return only the search queries, one per line, without numbering or additional text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research assistant specializing in generating effective search queries for technical topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            queries = [q.strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
            return queries
            
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            # Fallback to basic query generation
            return [
                f"{topic} best practices",
                f"{topic} recent developments",
                f"{topic} optimization techniques",
                f"{topic} security considerations",
                f"{topic} performance improvements"
            ]

    def _execute_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a search query and returns formatted results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        sources = []
        
        try:
            # This would integrate with the omni_search tool
            # For now, we'll simulate search results
            # In a real implementation, this would call the actual omni_search function
            
            # Simulated search results structure
            simulated_results = [
                {
                    'title': f"Research Result for: {query}",
                    'url': f"https://example.com/research/{hash(query) % 1000}",
                    'snippet': f"This is a simulated research result for the query '{query}'. It contains relevant information about the topic.",
                    'source_type': 'web',
                    'relevance_score': 0.8,
                    'date': datetime.now().isoformat()
                }
            ]
            
            # In real implementation, replace with:
            # if self.omni_search_tool:
            #     search_results = self.omni_search_tool(query, search_type="research")
            #     sources = self._format_search_results(search_results)
            
            sources = simulated_results[:max_results]
            
        except Exception as e:
            logger.error(f"Search execution failed for query '{query}': {str(e)}")
        
        return sources

    def _analyze_sources(self, topic: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes collected sources and extracts key findings.
        
        Args:
            topic: The research topic
            sources: List of source dictionaries
            
        Returns:
            Dictionary containing analysis results
        """
        analysis_prompt = f"""
Analyze the following research sources for the topic: "{topic}"

Sources:
{json.dumps(sources, indent=2)}

Provide a comprehensive analysis including:
1. Key findings (3-5 most important insights)
2. Actionable insights (specific recommendations for implementation)
3. Confidence score (0.0-1.0 based on source quality and consistency)
4. Potential risks or considerations
5. Recommended next steps

Format your response as a JSON object with the following structure:
{{
    "key_findings": ["finding1", "finding2", ...],
    "actionable_insights": ["insight1", "insight2", ...],
    "confidence_score": 0.0-1.0,
    "risks_considerations": ["risk1", "risk2", ...],
    "recommended_next_steps": ["step1", "step2", ...],
    "summary": "Brief summary of the research"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert research analyst specializing in technical and scientific literature analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle potential markdown formatting)
            if '```json' in analysis_text:
                json_start = analysis_text.find('```json') + 7
                json_end = analysis_text.find('```', json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            elif '```' in analysis_text:
                json_start = analysis_text.find('```') + 3
                json_end = analysis_text.find('```', json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            analysis_result = json.loads(analysis_text)
            
            # Validate and set defaults
            required_keys = ['key_findings', 'actionable_insights', 'confidence_score', 'summary']
            for key in required_keys:
                if key not in analysis_result:
                    analysis_result[key] = [] if key != 'confidence_score' and key != 'summary' else (0.5 if key == 'confidence_score' else "Analysis summary not available")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Source analysis failed: {str(e)}")
            return {
                'key_findings': [f"Analysis failed for topic: {topic}"],
                'actionable_insights': ["Manual review of sources recommended"],
                'confidence_score': 0.0,
                'summary': f"Automated analysis failed. {len(sources)} sources collected for manual review.",
                'error': str(e)
            }

    def _determine_research_topics(self, focus_areas: List[str] = None) -> List[Dict[str, Any]]:
        """
        Determines what topics to research based on current system needs and priorities.
        
        Args:
            focus_areas: Optional list of specific focus areas
            
        Returns:
            List of research topic dictionaries
        """
        topics = []
        
        # Use focus areas if provided, otherwise use all priority areas
        areas_to_research = focus_areas or list(self.research_priorities.keys())
        
        for area in areas_to_research:
            priority = self.research_priorities.get(area, 0.5)
            
            # Check if we've researched this area recently
            last_research = self.last_research_time.get(area)
            if last_research:
                time_since_last = datetime.now() - datetime.fromisoformat(last_research)
                if time_since_last < timedelta(hours=24) and priority < 0.8:
                    continue  # Skip if researched recently and not high priority
            
            # Generate specific topics for each area
            area_topics = self._generate_area_specific_topics(area)
            for topic_info in area_topics:
                topic_info['priority'] = priority
                topics.append(topic_info)
        
        # Sort by priority and return top topics
        topics.sort(key=lambda x: x.get('priority', 0), reverse=True)
        return topics[:5]  # Limit to top 5 topics to avoid overwhelming

    def _generate_area_specific_topics(self, area: str) -> List[Dict[str, Any]]:
        """
        Generates specific research topics for a given area.
        
        Args:
            area: The research area
            
        Returns:
            List of topic dictionaries
        """
        area_topics = {
            'ai_development': [
                {'topic': 'latest AI model architectures for code generation', 'depth': 'medium', 'max_sources': 5},
                {'topic': 'AI self-improvement techniques and frameworks', 'depth': 'deep', 'max_sources': 8}
            ],
            'code_optimization': [
                {'topic': 'Python performance optimization techniques 2024', 'depth': 'medium', 'max_sources': 6},
                {'topic': 'memory management best practices for long-running applications', 'depth': 'medium', 'max_sources': 5}
            ],
            'security_vulnerabilities': [
                {'topic': 'recent Python security vulnerabilities and patches', 'depth': 'deep', 'max_sources': 10},
                {'topic': 'AI system security best practices', 'depth': 'medium', 'max_sources': 6}
            ],
            'new_algorithms': [
                {'topic': 'efficient algorithms for natural language processing', 'depth': 'medium', 'max_sources': 5},
                {'topic': 'optimization algorithms for resource management', 'depth': 'shallow', 'max_sources': 4}
            ],
            'programming_best_practices': [
                {'topic': 'clean code principles for AI systems', 'depth': 'shallow', 'max_sources': 4},
                {'topic': 'testing strategies for machine learning applications', 'depth': 'medium', 'max_sources': 5}
            ],
            'emerging_technologies': [
                {'topic': 'emerging trends in AI and automation 2024', 'depth': 'shallow', 'max_sources': 4},
                {'topic': 'new programming languages and frameworks for AI', 'depth': 'shallow', 'max_sources': 3}
            ]
        }
        
        return area_topics.get(area, [{'topic': f'general research on {area}', 'depth': 'medium', 'max_sources': 5}])

    def _generate_summary_insights(self, all_findings: List[str]) -> Dict[str, Any]:
        """
        Generates summary insights from all research findings.
        
        Args:
            all_findings: List of all findings from research sessions
            
        Returns:
            Dictionary containing summary insights
        """
        summary_prompt = f"""
Analyze the following research findings and generate summary insights:

Findings:
{json.dumps(all_findings, indent=2)}

Provide:
1. Top 3 most important insights across all findings
2. Common themes or patterns
3. Immediate action items for system improvement
4. Long-term strategic recommendations

Format as JSON:
{{
    "top_insights": ["insight1", "insight2", "insight3"],
    "common_themes": ["theme1", "theme2", ...],
    "immediate_actions": ["action1", "action2", ...],
    "strategic_recommendations": ["rec1", "rec2", ...],
    "overall_assessment": "Brief overall assessment"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic analyst specializing in technology research synthesis."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if '```json' in summary_text:
                json_start = summary_text.find('```json') + 7
                json_end = summary_text.find('```', json_start)
                summary_text = summary_text[json_start:json_end].strip()
            
            return json.loads(summary_text)
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return {
                'top_insights': ["Summary generation failed"],
                'common_themes': [],
                'immediate_actions': ["Manual review of findings recommended"],
                'strategic_recommendations': [],
                'overall_assessment': f"Automated summary failed. {len(all_findings)} findings available for manual review."
            }

    def _store_research_results(self, research_session: Dict[str, Any]):
        """
        Stores research results in the knowledge repository and updates tracking.
        
        Args:
            research_session: The research session results to store
        """
        # Add to research history
        self.research_history.append(research_session)
        
        # Keep only last 50 research sessions
        if len(self.research_history) > 50:
            self.research_history = self.research_history[-50:]
        
        # Store in knowledge repository if available
        if self.knowledge_repository:
            self.knowledge_repository.add_research_finding({
                'type': 'research_session',
                'session_data': research_session,
                'timestamp': research_session['timestamp']
            })
            
            # Store individual findings
            for finding in research_session.get('key_findings', []):
                self.knowledge_repository.add_research_finding({
                    'type': 'key_finding',
                    'topic': research_session['topic'],
                    'finding': finding,
                    'confidence_score': research_session.get('confidence_score', 0.5),
                    'timestamp': research_session['timestamp']
                })
        
        # Update last research time for the topic area
        topic = research_session.get('topic', '')
        for area in self.research_priorities.keys():
            if area.replace('_', ' ') in topic.lower():
                self.last_research_time[area] = research_session['timestamp']
                break

    def get_research_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Gets the research history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of research session records
        """
        return self.research_history[-limit:] if limit else self.research_history.copy()

    def get_research_statistics(self) -> Dict[str, Any]:
        """
        Gets statistics about research activities.
        
        Returns:
            Dictionary containing research statistics
        """
        total_sessions = len(self.research_history)
        successful_sessions = sum(1 for session in self.research_history if session.get('status') == 'completed')
        
        # Topic distribution
        topic_counts = {}
        for session in self.research_history:
            topic = session.get('topic', 'unknown')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Recent activity
        recent_sessions = [
            session for session in self.research_history
            if datetime.now() - datetime.fromisoformat(session['timestamp']) < timedelta(days=7)
        ]
        
        return {
            'total_research_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'success_rate': successful_sessions / max(total_sessions, 1),
            'recent_sessions_7_days': len(recent_sessions),
            'topic_distribution': topic_counts,
            'research_priorities': self.research_priorities,
            'last_research_times': self.last_research_time
        }

    def update_research_priority(self, area: str, priority: float):
        """
        Updates the research priority for a specific area.
        
        Args:
            area: The research area
            priority: New priority value (0.0-1.0)
        """
        if 0.0 <= priority <= 1.0:
            self.research_priorities[area] = priority
            logger.info(f"Updated research priority for {area}: {priority}")
        else:
            logger.warning(f"Invalid priority value: {priority}. Must be between 0.0 and 1.0")

    def schedule_periodic_research(self, interval_hours: int = 24):
        """
        Schedules periodic autonomous research (placeholder for future implementation).
        
        Args:
            interval_hours: How often to conduct research (in hours)
        """
        logger.info(f"Periodic research scheduled every {interval_hours} hours")
        # This would integrate with a task scheduler in a full implementation
        # For now, it's a placeholder that logs the intent

