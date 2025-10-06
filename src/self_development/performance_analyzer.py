"""
Performance Analyzer for JARVIS AI Hub Self-Development Module

This module provides mechanisms for the AI to analyze its own performance
and identify areas for code improvement through comprehensive metrics collection
and intelligent analysis.
"""

import logging
import json
import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """
    The Performance Analyzer continuously monitors JARVIS's operational metrics,
    identifies performance bottlenecks, and suggests areas for improvement.
    """

    def __init__(self, knowledge_repository=None):
        self.knowledge_repository = knowledge_repository
        self.metrics_history = []
        self.performance_baselines = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_thresholds = {
            'cpu_usage': 80.0,  # Percentage
            'memory_usage': 85.0,  # Percentage
            'response_time': 5.0,  # Seconds
            'error_rate': 5.0,  # Percentage
            'disk_usage': 90.0  # Percentage
        }
        self.improvement_suggestions = []
        logger.info("Performance Analyzer initialized")

    def start_monitoring(self, interval_seconds: int = 30):
        """
        Starts continuous performance monitoring in a background thread.
        
        Args:
            interval_seconds: How often to collect metrics (default: 30 seconds)
        """
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interval_seconds,),
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info(f"Performance monitoring started with {interval_seconds}s interval")
        else:
            logger.warning("Performance monitoring is already active")

    def stop_monitoring(self):
        """Stops the performance monitoring thread."""
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            logger.info("Performance monitoring stopped")

    def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop that runs in a background thread."""
        while self.monitoring_active:
            try:
                metrics = self.collect_system_metrics()
                self.record_metrics(metrics)
                self._check_for_alerts(metrics)
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(interval_seconds)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collects comprehensive system performance metrics.
        
        Returns:
            Dictionary containing current system metrics
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process-specific metrics (for JARVIS process)
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'cpu_count': cpu_count,
                    'cpu_frequency': cpu_freq.current if cpu_freq else None,
                    'memory_total': memory.total,
                    'memory_available': memory.available,
                    'memory_percent': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent,
                    'disk_total': disk.total,
                    'disk_used': disk.used,
                    'disk_percent': (disk.used / disk.total) * 100,
                    'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
                    'disk_write_bytes': disk_io.write_bytes if disk_io else 0,
                    'network_bytes_sent': network_io.bytes_sent if network_io else 0,
                    'network_bytes_recv': network_io.bytes_recv if network_io else 0
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def record_metrics(self, metrics: Dict[str, Any]):
        """
        Records metrics in the history and updates baselines.
        
        Args:
            metrics: The metrics dictionary to record
        """
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 metric records to prevent memory bloat
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Update performance baselines
        self._update_baselines(metrics)
        
        # Store in knowledge repository if available
        if self.knowledge_repository:
            self.knowledge_repository.add_performance_data({
                'type': 'system_metrics',
                'metrics': metrics,
                'timestamp': metrics.get('timestamp')
            })

    def _update_baselines(self, metrics: Dict[str, Any]):
        """Updates performance baselines based on historical data."""
        if 'system' in metrics and 'process' in metrics:
            # Calculate rolling averages for key metrics
            recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
            
            if len(recent_metrics) >= 5:  # Need at least 5 data points
                self.performance_baselines = {
                    'avg_cpu_percent': sum(m.get('system', {}).get('cpu_percent', 0) for m in recent_metrics) / len(recent_metrics),
                    'avg_memory_percent': sum(m.get('system', {}).get('memory_percent', 0) for m in recent_metrics) / len(recent_metrics),
                    'avg_process_cpu': sum(m.get('process', {}).get('cpu_percent', 0) for m in recent_metrics) / len(recent_metrics),
                    'avg_process_memory': sum(m.get('process', {}).get('memory_percent', 0) for m in recent_metrics) / len(recent_metrics),
                    'last_updated': datetime.now().isoformat()
                }

    def _check_for_alerts(self, metrics: Dict[str, Any]):
        """
        Checks current metrics against alert thresholds and generates alerts.
        
        Args:
            metrics: Current metrics to check
        """
        alerts = []
        
        if 'system' in metrics:
            system = metrics['system']
            
            # CPU usage alert
            if system.get('cpu_percent', 0) > self.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'high_cpu_usage',
                    'severity': 'warning',
                    'message': f"High CPU usage: {system['cpu_percent']:.1f}%",
                    'value': system['cpu_percent'],
                    'threshold': self.alert_thresholds['cpu_usage']
                })
            
            # Memory usage alert
            if system.get('memory_percent', 0) > self.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'high_memory_usage',
                    'severity': 'warning',
                    'message': f"High memory usage: {system['memory_percent']:.1f}%",
                    'value': system['memory_percent'],
                    'threshold': self.alert_thresholds['memory_usage']
                })
            
            # Disk usage alert
            disk_percent = system.get('disk_percent', 0)
            if disk_percent > self.alert_thresholds['disk_usage']:
                alerts.append({
                    'type': 'high_disk_usage',
                    'severity': 'critical',
                    'message': f"High disk usage: {disk_percent:.1f}%",
                    'value': disk_percent,
                    'threshold': self.alert_thresholds['disk_usage']
                })
        
        # Log alerts and store them
        for alert in alerts:
            logger.warning(f"Performance Alert: {alert['message']}")
            if self.knowledge_repository:
                self.knowledge_repository.add_performance_data({
                    'type': 'performance_alert',
                    'alert': alert,
                    'timestamp': datetime.now().isoformat()
                })

    def analyze_performance_trends(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Analyzes performance trends over a specified time period.
        
        Args:
            hours_back: How many hours of history to analyze
            
        Returns:
            Dictionary containing trend analysis results
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter metrics within the time window
        relevant_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if len(relevant_metrics) < 2:
            return {
                'error': 'Insufficient data for trend analysis',
                'data_points': len(relevant_metrics),
                'required_minimum': 2
            }
        
        # Calculate trends
        trends = {
            'analysis_period_hours': hours_back,
            'data_points_analyzed': len(relevant_metrics),
            'trends': {},
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # CPU trend analysis
        cpu_values = [m.get('system', {}).get('cpu_percent', 0) for m in relevant_metrics]
        trends['trends']['cpu_usage'] = {
            'average': sum(cpu_values) / len(cpu_values),
            'min': min(cpu_values),
            'max': max(cpu_values),
            'trend_direction': self._calculate_trend_direction(cpu_values),
            'volatility': self._calculate_volatility(cpu_values)
        }
        
        # Memory trend analysis
        memory_values = [m.get('system', {}).get('memory_percent', 0) for m in relevant_metrics]
        trends['trends']['memory_usage'] = {
            'average': sum(memory_values) / len(memory_values),
            'min': min(memory_values),
            'max': max(memory_values),
            'trend_direction': self._calculate_trend_direction(memory_values),
            'volatility': self._calculate_volatility(memory_values)
        }
        
        # Process-specific trends
        process_cpu_values = [m.get('process', {}).get('cpu_percent', 0) for m in relevant_metrics]
        process_memory_values = [m.get('process', {}).get('memory_percent', 0) for m in relevant_metrics]
        
        trends['trends']['process_cpu'] = {
            'average': sum(process_cpu_values) / len(process_cpu_values),
            'trend_direction': self._calculate_trend_direction(process_cpu_values)
        }
        
        trends['trends']['process_memory'] = {
            'average': sum(process_memory_values) / len(process_memory_values),
            'trend_direction': self._calculate_trend_direction(process_memory_values)
        }
        
        # Generate recommendations based on trends
        trends['recommendations'] = self._generate_performance_recommendations(trends['trends'])
        
        return trends

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """
        Calculates the overall trend direction of a series of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            String indicating trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x_squared_sum = sum(i * i for i in range(n))
        
        # Calculate slope
        slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    def _calculate_volatility(self, values: List[float]) -> float:
        """
        Calculates the volatility (standard deviation) of a series of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Float representing the volatility
        """
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _generate_performance_recommendations(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates performance improvement recommendations based on trend analysis.
        
        Args:
            trends: Dictionary containing trend analysis results
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # CPU usage recommendations
        cpu_trend = trends.get('cpu_usage', {})
        if cpu_trend.get('average', 0) > 70:
            recommendations.append({
                'type': 'cpu_optimization',
                'priority': 'high',
                'title': 'High CPU Usage Detected',
                'description': f"Average CPU usage is {cpu_trend['average']:.1f}%. Consider optimizing CPU-intensive operations.",
                'suggested_actions': [
                    'Profile code to identify CPU hotspots',
                    'Implement caching for frequently computed results',
                    'Consider asynchronous processing for heavy tasks',
                    'Optimize database queries and reduce unnecessary computations'
                ]
            })
        
        if cpu_trend.get('trend_direction') == 'increasing':
            recommendations.append({
                'type': 'cpu_trend_warning',
                'priority': 'medium',
                'title': 'Increasing CPU Usage Trend',
                'description': 'CPU usage is trending upward over time.',
                'suggested_actions': [
                    'Monitor for memory leaks or resource accumulation',
                    'Review recent code changes for performance regressions',
                    'Consider implementing resource cleanup mechanisms'
                ]
            })
        
        # Memory usage recommendations
        memory_trend = trends.get('memory_usage', {})
        if memory_trend.get('average', 0) > 80:
            recommendations.append({
                'type': 'memory_optimization',
                'priority': 'high',
                'title': 'High Memory Usage Detected',
                'description': f"Average memory usage is {memory_trend['average']:.1f}%. Memory optimization needed.",
                'suggested_actions': [
                    'Implement garbage collection optimization',
                    'Review data structures for memory efficiency',
                    'Consider implementing data pagination or streaming',
                    'Check for memory leaks in long-running processes'
                ]
            })
        
        if memory_trend.get('trend_direction') == 'increasing':
            recommendations.append({
                'type': 'memory_leak_warning',
                'priority': 'critical',
                'title': 'Potential Memory Leak',
                'description': 'Memory usage is consistently increasing over time.',
                'suggested_actions': [
                    'Investigate for memory leaks in application code',
                    'Review object lifecycle management',
                    'Implement memory profiling and monitoring',
                    'Consider restarting services periodically as a temporary measure'
                ]
            })
        
        # Process-specific recommendations
        process_cpu = trends.get('process_cpu', {})
        if process_cpu.get('average', 0) > 50:
            recommendations.append({
                'type': 'process_optimization',
                'priority': 'medium',
                'title': 'High Process CPU Usage',
                'description': f"JARVIS process is using {process_cpu['average']:.1f}% CPU on average.",
                'suggested_actions': [
                    'Profile JARVIS-specific operations',
                    'Optimize AI model inference calls',
                    'Implement request queuing and rate limiting',
                    'Consider distributing workload across multiple processes'
                ]
            })
        
        return recommendations

    def identify_improvement_opportunities(self) -> Dict[str, Any]:
        """
        Identifies specific code improvement opportunities based on performance analysis.
        
        Returns:
            Dictionary containing improvement opportunities and suggestions
        """
        opportunities = {
            'timestamp': datetime.now().isoformat(),
            'code_improvements': [],
            'system_improvements': [],
            'architecture_improvements': []
        }
        
        # Analyze recent performance data
        if len(self.metrics_history) > 10:
            recent_trends = self.analyze_performance_trends(hours_back=6)
            
            # Code-level improvements
            if any(rec['type'] == 'cpu_optimization' for rec in recent_trends.get('recommendations', [])):
                opportunities['code_improvements'].append({
                    'area': 'CPU optimization',
                    'description': 'Implement more efficient algorithms and reduce computational complexity',
                    'specific_suggestions': [
                        'Cache frequently computed results',
                        'Use more efficient data structures',
                        'Implement lazy evaluation where possible',
                        'Optimize loops and recursive functions'
                    ],
                    'estimated_impact': 'high'
                })
            
            if any(rec['type'] == 'memory_optimization' for rec in recent_trends.get('recommendations', [])):
                opportunities['code_improvements'].append({
                    'area': 'Memory optimization',
                    'description': 'Reduce memory footprint and improve memory management',
                    'specific_suggestions': [
                        'Implement object pooling for frequently created objects',
                        'Use generators instead of lists where appropriate',
                        'Implement proper cleanup in finally blocks',
                        'Consider using memory-mapped files for large datasets'
                    ],
                    'estimated_impact': 'high'
                })
            
            # System-level improvements
            opportunities['system_improvements'].append({
                'area': 'Monitoring and alerting',
                'description': 'Enhance system monitoring capabilities',
                'specific_suggestions': [
                    'Implement real-time performance dashboards',
                    'Add more granular performance metrics',
                    'Implement predictive alerting based on trends',
                    'Add performance regression testing'
                ],
                'estimated_impact': 'medium'
            })
            
            # Architecture improvements
            opportunities['architecture_improvements'].append({
                'area': 'Scalability',
                'description': 'Improve system architecture for better scalability',
                'specific_suggestions': [
                    'Implement microservices architecture',
                    'Add horizontal scaling capabilities',
                    'Implement load balancing',
                    'Consider containerization for better resource isolation'
                ],
                'estimated_impact': 'high'
            })
        
        # Store opportunities in knowledge repository
        if self.knowledge_repository:
            self.knowledge_repository.add_performance_data({
                'type': 'improvement_opportunities',
                'opportunities': opportunities,
                'timestamp': opportunities['timestamp']
            })
        
        return opportunities

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Gets a comprehensive performance summary.
        
        Returns:
            Dictionary containing current performance status and recommendations
        """
        if not self.metrics_history:
            return {
                'status': 'no_data',
                'message': 'No performance data available. Start monitoring to collect metrics.'
            }
        
        latest_metrics = self.metrics_history[-1]
        trends = self.analyze_performance_trends(hours_back=24)
        opportunities = self.identify_improvement_opportunities()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_status': 'active' if self.monitoring_active else 'inactive',
            'data_points_collected': len(self.metrics_history),
            'current_metrics': {
                'cpu_percent': latest_metrics.get('system', {}).get('cpu_percent', 0),
                'memory_percent': latest_metrics.get('system', {}).get('memory_percent', 0),
                'disk_percent': latest_metrics.get('system', {}).get('disk_percent', 0),
                'process_cpu_percent': latest_metrics.get('process', {}).get('cpu_percent', 0),
                'process_memory_percent': latest_metrics.get('process', {}).get('memory_percent', 0)
            },
            'performance_baselines': self.performance_baselines,
            'trend_analysis': trends,
            'improvement_opportunities': opportunities,
            'health_score': self._calculate_health_score(latest_metrics, trends)
        }
        
        return summary

    def _calculate_health_score(self, latest_metrics: Dict[str, Any], trends: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates an overall system health score based on current metrics and trends.
        
        Args:
            latest_metrics: Most recent performance metrics
            trends: Trend analysis results
            
        Returns:
            Dictionary containing health score and breakdown
        """
        score_components = {}
        
        # CPU health (0-100, higher is better)
        cpu_percent = latest_metrics.get('system', {}).get('cpu_percent', 0)
        cpu_score = max(0, 100 - cpu_percent)
        score_components['cpu'] = cpu_score
        
        # Memory health (0-100, higher is better)
        memory_percent = latest_metrics.get('system', {}).get('memory_percent', 0)
        memory_score = max(0, 100 - memory_percent)
        score_components['memory'] = memory_score
        
        # Disk health (0-100, higher is better)
        disk_percent = latest_metrics.get('system', {}).get('disk_percent', 0)
        disk_score = max(0, 100 - disk_percent)
        score_components['disk'] = disk_score
        
        # Trend health (penalize increasing trends for resource usage)
        trend_score = 100
        if trends.get('trends', {}).get('cpu_usage', {}).get('trend_direction') == 'increasing':
            trend_score -= 20
        if trends.get('trends', {}).get('memory_usage', {}).get('trend_direction') == 'increasing':
            trend_score -= 20
        score_components['trends'] = max(0, trend_score)
        
        # Calculate overall score (weighted average)
        weights = {'cpu': 0.3, 'memory': 0.3, 'disk': 0.2, 'trends': 0.2}
        overall_score = sum(score_components[component] * weights[component] for component in weights)
        
        # Determine health status
        if overall_score >= 80:
            status = 'excellent'
        elif overall_score >= 60:
            status = 'good'
        elif overall_score >= 40:
            status = 'fair'
        elif overall_score >= 20:
            status = 'poor'
        else:
            status = 'critical'
        
        return {
            'overall_score': round(overall_score, 1),
            'status': status,
            'component_scores': score_components,
            'weights': weights
        }

    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Gets the performance metrics history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of performance metrics records
        """
        return self.metrics_history[-limit:] if limit else self.metrics_history.copy()

    def clear_metrics_history(self):
        """Clears the performance metrics history."""
        self.metrics_history.clear()
        logger.info("Performance metrics history cleared")

    def set_alert_threshold(self, metric: str, threshold: float):
        """
        Sets or updates an alert threshold for a specific metric.
        
        Args:
            metric: The metric name (e.g., 'cpu_usage', 'memory_usage')
            threshold: The threshold value
        """
        if metric in self.alert_thresholds:
            old_threshold = self.alert_thresholds[metric]
            self.alert_thresholds[metric] = threshold
            logger.info(f"Updated alert threshold for {metric}: {old_threshold} -> {threshold}")
        else:
            logger.warning(f"Unknown metric for alert threshold: {metric}")

    def get_alert_thresholds(self) -> Dict[str, float]:
        """Gets the current alert thresholds."""
        return self.alert_thresholds.copy()

