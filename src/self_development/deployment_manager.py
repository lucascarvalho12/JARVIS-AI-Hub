"""
Deployment Manager (DM) for JARVIS AI Hub Self-Development Module

This module provides safe deployment strategies for autonomously generated
or modified code, including version control, rollback capabilities, and
gradual deployment mechanisms.
"""

import os
import json
import logging
import shutil
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile
import git

logger = logging.getLogger(__name__)

class DeploymentManager:
    """
    The Deployment Manager ensures safe deployment of self-modified code
    with proper version control, testing, and rollback capabilities.
    """

    def __init__(self, knowledge_repository=None, validation_framework=None):
        self.knowledge_repository = knowledge_repository
        self.validation_framework = validation_framework
        self.deployment_history = []
        self.backup_directory = os.path.join(os.getcwd(), "backups")
        self.staging_directory = os.path.join(os.getcwd(), "staging")
        self.deployment_strategies = {
            'safe': self._safe_deployment,
            'gradual': self._gradual_deployment,
            'canary': self._canary_deployment,
            'blue_green': self._blue_green_deployment
        }
        self._ensure_directories()
        logger.info("Deployment Manager initialized")

    def _ensure_directories(self):
        """Ensures that necessary directories exist."""
        for directory in [self.backup_directory, self.staging_directory]:
            os.makedirs(directory, exist_ok=True)

    def deploy_code(self, code: str, target_file: str, strategy: str = "safe", 
                   validation_required: bool = True) -> Dict[str, Any]:
        """
        Deploys code using the specified strategy.
        
        Args:
            code: The code to deploy
            target_file: Target file path for deployment
            strategy: Deployment strategy ('safe', 'gradual', 'canary', 'blue_green')
            validation_required: Whether to validate code before deployment
            
        Returns:
            Dictionary containing deployment results
        """
        logger.info(f"Initiating {strategy} deployment to {target_file}")
        
        deployment_record = {
            'deployment_id': f"deploy_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'target_file': target_file,
            'strategy': strategy,
            'validation_required': validation_required,
            'status': 'initiated',
            'code_hash': hash(code),
            'backup_created': False,
            'validation_passed': False,
            'deployment_successful': False,
            'rollback_available': False
        }

        try:
            # Step 1: Validation (if required)
            if validation_required and self.validation_framework:
                logger.info("Validating code before deployment")
                validation_result = self.validation_framework.validate_code(
                    code, language="python", validation_level="comprehensive"
                )
                deployment_record['validation_result'] = validation_result
                deployment_record['validation_passed'] = validation_result['passed']
                
                if not validation_result['passed']:
                    deployment_record['status'] = 'failed_validation'
                    deployment_record['error'] = 'Code failed validation checks'
                    return deployment_record
            else:
                deployment_record['validation_passed'] = True
            
            # Step 2: Create backup
            backup_result = self._create_backup(target_file, deployment_record['deployment_id'])
            deployment_record['backup_created'] = backup_result['success']
            deployment_record['backup_path'] = backup_result.get('backup_path')
            
            if not backup_result['success']:
                deployment_record['status'] = 'failed_backup'
                deployment_record['error'] = backup_result.get('error', 'Backup creation failed')
                return deployment_record
            
            # Step 3: Execute deployment strategy
            if strategy in self.deployment_strategies:
                strategy_result = self.deployment_strategies[strategy](
                    code, target_file, deployment_record
                )
                deployment_record.update(strategy_result)
            else:
                deployment_record['status'] = 'failed'
                deployment_record['error'] = f'Unknown deployment strategy: {strategy}'
                return deployment_record
            
            # Step 4: Post-deployment verification
            if deployment_record.get('deployment_successful', False):
                verification_result = self._verify_deployment(target_file, code)
                deployment_record['verification_result'] = verification_result
                
                if not verification_result['success']:
                    # Rollback if verification fails
                    logger.warning("Deployment verification failed, initiating rollback")
                    rollback_result = self.rollback_deployment(deployment_record['deployment_id'])
                    deployment_record['rollback_result'] = rollback_result
                    deployment_record['status'] = 'failed_verification'
                else:
                    deployment_record['status'] = 'completed'
                    deployment_record['rollback_available'] = True
            
        except Exception as e:
            logger.error(f"Deployment process failed: {str(e)}")
            deployment_record['status'] = 'error'
            deployment_record['error'] = str(e)
            
            # Attempt rollback if backup was created
            if deployment_record.get('backup_created', False):
                try:
                    rollback_result = self.rollback_deployment(deployment_record['deployment_id'])
                    deployment_record['emergency_rollback'] = rollback_result
                except Exception as rollback_error:
                    logger.error(f"Emergency rollback failed: {str(rollback_error)}")
        
        # Store deployment record
        self._store_deployment_record(deployment_record)
        
        return deployment_record

    def _safe_deployment(self, code: str, target_file: str, 
                        deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements safe deployment strategy with immediate replacement.
        
        Args:
            code: Code to deploy
            target_file: Target file path
            deployment_record: Deployment record dictionary
            
        Returns:
            Dictionary with deployment results
        """
        result = {
            'deployment_successful': False,
            'deployment_details': 'Safe deployment strategy'
        }

        try:
            # Write code to staging area first
            staging_file = os.path.join(self.staging_directory, os.path.basename(target_file))
            with open(staging_file, 'w') as f:
                f.write(code)
            
            # Test the staged code
            test_result = self._test_staged_code(staging_file)
            if not test_result['success']:
                result['error'] = f"Staged code testing failed: {test_result.get('error', 'Unknown error')}"
                return result
            
            # Deploy to target location
            shutil.copy2(staging_file, target_file)
            result['deployment_successful'] = True
            
            logger.info(f"Safe deployment completed successfully to {target_file}")
            
        except Exception as e:
            logger.error(f"Safe deployment failed: {str(e)}")
            result['error'] = str(e)
        
        return result

    def _gradual_deployment(self, code: str, target_file: str, 
                           deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements gradual deployment strategy with phased rollout.
        
        Args:
            code: Code to deploy
            target_file: Target file path
            deployment_record: Deployment record dictionary
            
        Returns:
            Dictionary with deployment results
        """
        result = {
            'deployment_successful': False,
            'deployment_details': 'Gradual deployment strategy',
            'phases': []
        }

        try:
            # Phase 1: Deploy to staging
            phase1_result = self._deploy_to_staging(code, target_file)
            result['phases'].append(phase1_result)
            
            if not phase1_result['success']:
                result['error'] = 'Phase 1 (staging) failed'
                return result
            
            # Phase 2: Limited testing
            phase2_result = self._limited_testing(target_file)
            result['phases'].append(phase2_result)
            
            if not phase2_result['success']:
                result['error'] = 'Phase 2 (limited testing) failed'
                return result
            
            # Phase 3: Full deployment
            phase3_result = self._full_deployment(code, target_file)
            result['phases'].append(phase3_result)
            
            if phase3_result['success']:
                result['deployment_successful'] = True
                logger.info(f"Gradual deployment completed successfully to {target_file}")
            else:
                result['error'] = 'Phase 3 (full deployment) failed'
            
        except Exception as e:
            logger.error(f"Gradual deployment failed: {str(e)}")
            result['error'] = str(e)
        
        return result

    def _canary_deployment(self, code: str, target_file: str, 
                          deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements canary deployment strategy with monitoring.
        
        Args:
            code: Code to deploy
            target_file: Target file path
            deployment_record: Deployment record dictionary
            
        Returns:
            Dictionary with deployment results
        """
        result = {
            'deployment_successful': False,
            'deployment_details': 'Canary deployment strategy',
            'canary_metrics': {}
        }

        try:
            # Create canary version
            canary_file = f"{target_file}.canary"
            with open(canary_file, 'w') as f:
                f.write(code)
            
            # Monitor canary performance
            monitoring_result = self._monitor_canary(canary_file, duration_seconds=30)
            result['canary_metrics'] = monitoring_result
            
            if monitoring_result['success'] and monitoring_result['performance_acceptable']:
                # Promote canary to production
                shutil.copy2(canary_file, target_file)
                os.remove(canary_file)  # Clean up canary
                result['deployment_successful'] = True
                logger.info(f"Canary deployment promoted to production: {target_file}")
            else:
                # Remove failed canary
                if os.path.exists(canary_file):
                    os.remove(canary_file)
                result['error'] = 'Canary performance was not acceptable'
            
        except Exception as e:
            logger.error(f"Canary deployment failed: {str(e)}")
            result['error'] = str(e)
        
        return result

    def _blue_green_deployment(self, code: str, target_file: str, 
                              deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements blue-green deployment strategy with environment switching.
        
        Args:
            code: Code to deploy
            target_file: Target file path
            deployment_record: Deployment record dictionary
            
        Returns:
            Dictionary with deployment results
        """
        result = {
            'deployment_successful': False,
            'deployment_details': 'Blue-green deployment strategy',
            'environments': {}
        }

        try:
            # Create green environment (new version)
            green_file = f"{target_file}.green"
            with open(green_file, 'w') as f:
                f.write(code)
            
            # Test green environment
            green_test_result = self._test_environment(green_file)
            result['environments']['green'] = green_test_result
            
            if green_test_result['success']:
                # Switch from blue to green (atomic operation)
                blue_file = f"{target_file}.blue"
                
                # Move current production to blue
                if os.path.exists(target_file):
                    shutil.copy2(target_file, blue_file)
                
                # Switch green to production
                shutil.copy2(green_file, target_file)
                
                # Verify switch
                switch_verification = self._verify_deployment(target_file, code)
                if switch_verification['success']:
                    result['deployment_successful'] = True
                    result['environments']['switch_successful'] = True
                    logger.info(f"Blue-green deployment completed: {target_file}")
                    
                    # Clean up green file (production is now the target)
                    os.remove(green_file)
                else:
                    # Rollback to blue
                    if os.path.exists(blue_file):
                        shutil.copy2(blue_file, target_file)
                    result['error'] = 'Switch verification failed, rolled back to blue'
            else:
                result['error'] = 'Green environment testing failed'
                if os.path.exists(green_file):
                    os.remove(green_file)
            
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {str(e)}")
            result['error'] = str(e)
        
        return result

    def _create_backup(self, target_file: str, deployment_id: str) -> Dict[str, Any]:
        """
        Creates a backup of the target file before deployment.
        
        Args:
            target_file: File to backup
            deployment_id: Unique deployment identifier
            
        Returns:
            Dictionary with backup results
        """
        backup_result = {
            'success': False,
            'backup_path': None
        }

        try:
            if os.path.exists(target_file):
                backup_filename = f"{os.path.basename(target_file)}.{deployment_id}.backup"
                backup_path = os.path.join(self.backup_directory, backup_filename)
                
                shutil.copy2(target_file, backup_path)
                backup_result['success'] = True
                backup_result['backup_path'] = backup_path
                
                logger.info(f"Backup created: {backup_path}")
            else:
                # File doesn't exist, no backup needed (new file deployment)
                backup_result['success'] = True
                backup_result['backup_path'] = None
                logger.info(f"No backup needed for new file: {target_file}")
        
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            backup_result['error'] = str(e)
        
        return backup_result

    def _test_staged_code(self, staged_file: str) -> Dict[str, Any]:
        """
        Tests code in the staging area.
        
        Args:
            staged_file: Path to staged code file
            
        Returns:
            Dictionary with test results
        """
        test_result = {
            'success': False,
            'tests_run': 0,
            'tests_passed': 0
        }

        try:
            # Basic syntax check
            with open(staged_file, 'r') as f:
                code = f.read()
            
            # Try to compile the code
            compile(code, staged_file, 'exec')
            
            # If we get here, syntax is valid
            test_result['success'] = True
            test_result['tests_run'] = 1
            test_result['tests_passed'] = 1
            
        except SyntaxError as e:
            test_result['error'] = f"Syntax error: {str(e)}"
        except Exception as e:
            test_result['error'] = f"Testing error: {str(e)}"
        
        return test_result

    def _deploy_to_staging(self, code: str, target_file: str) -> Dict[str, Any]:
        """
        Deploys code to staging environment.
        
        Args:
            code: Code to deploy
            target_file: Target file path
            
        Returns:
            Dictionary with deployment results
        """
        result = {
            'success': False,
            'phase': 'staging_deployment'
        }

        try:
            staging_file = os.path.join(self.staging_directory, os.path.basename(target_file))
            with open(staging_file, 'w') as f:
                f.write(code)
            
            result['success'] = True
            result['staging_file'] = staging_file
            
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def _limited_testing(self, target_file: str) -> Dict[str, Any]:
        """
        Performs limited testing on the staged code.
        
        Args:
            target_file: Target file path
            
        Returns:
            Dictionary with testing results
        """
        result = {
            'success': False,
            'phase': 'limited_testing'
        }

        try:
            staging_file = os.path.join(self.staging_directory, os.path.basename(target_file))
            
            # Perform basic tests
            test_result = self._test_staged_code(staging_file)
            result.update(test_result)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def _full_deployment(self, code: str, target_file: str) -> Dict[str, Any]:
        """
        Performs full deployment to production.
        
        Args:
            code: Code to deploy
            target_file: Target file path
            
        Returns:
            Dictionary with deployment results
        """
        result = {
            'success': False,
            'phase': 'full_deployment'
        }

        try:
            with open(target_file, 'w') as f:
                f.write(code)
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def _monitor_canary(self, canary_file: str, duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Monitors canary deployment performance.
        
        Args:
            canary_file: Path to canary file
            duration_seconds: How long to monitor
            
        Returns:
            Dictionary with monitoring results
        """
        monitoring_result = {
            'success': False,
            'performance_acceptable': False,
            'duration_seconds': duration_seconds,
            'metrics': {}
        }

        try:
            # Simulate monitoring (in a real implementation, this would monitor actual metrics)
            import time
            
            start_time = time.time()
            
            # Basic checks
            if os.path.exists(canary_file):
                with open(canary_file, 'r') as f:
                    code = f.read()
                
                # Try to compile/validate the canary
                compile(code, canary_file, 'exec')
                
                # Simulate monitoring period
                time.sleep(min(duration_seconds, 5))  # Cap at 5 seconds for testing
                
                end_time = time.time()
                
                monitoring_result['success'] = True
                monitoring_result['performance_acceptable'] = True  # Simplified check
                monitoring_result['metrics'] = {
                    'monitoring_duration': end_time - start_time,
                    'syntax_valid': True,
                    'no_errors_detected': True
                }
            
        except Exception as e:
            monitoring_result['error'] = str(e)
        
        return monitoring_result

    def _test_environment(self, environment_file: str) -> Dict[str, Any]:
        """
        Tests a deployment environment.
        
        Args:
            environment_file: Path to environment file
            
        Returns:
            Dictionary with test results
        """
        test_result = {
            'success': False,
            'environment': environment_file
        }

        try:
            # Basic environment testing
            test_result.update(self._test_staged_code(environment_file))
            
        except Exception as e:
            test_result['error'] = str(e)
        
        return test_result

    def _verify_deployment(self, target_file: str, expected_code: str) -> Dict[str, Any]:
        """
        Verifies that deployment was successful.
        
        Args:
            target_file: Path to deployed file
            expected_code: Expected code content
            
        Returns:
            Dictionary with verification results
        """
        verification_result = {
            'success': False,
            'file_exists': False,
            'content_matches': False
        }

        try:
            if os.path.exists(target_file):
                verification_result['file_exists'] = True
                
                with open(target_file, 'r') as f:
                    actual_code = f.read()
                
                # Check if content matches
                if actual_code.strip() == expected_code.strip():
                    verification_result['content_matches'] = True
                    verification_result['success'] = True
                else:
                    verification_result['error'] = 'Deployed content does not match expected code'
            else:
                verification_result['error'] = 'Target file does not exist after deployment'
        
        except Exception as e:
            verification_result['error'] = str(e)
        
        return verification_result

    def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Rolls back a deployment using its backup.
        
        Args:
            deployment_id: ID of the deployment to rollback
            
        Returns:
            Dictionary with rollback results
        """
        logger.info(f"Initiating rollback for deployment: {deployment_id}")
        
        rollback_result = {
            'success': False,
            'deployment_id': deployment_id,
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Find the deployment record
            deployment_record = None
            for record in self.deployment_history:
                if record.get('deployment_id') == deployment_id:
                    deployment_record = record
                    break
            
            if not deployment_record:
                rollback_result['error'] = f'Deployment record not found: {deployment_id}'
                return rollback_result
            
            backup_path = deployment_record.get('backup_path')
            target_file = deployment_record.get('target_file')
            
            if not backup_path or not os.path.exists(backup_path):
                rollback_result['error'] = 'Backup file not found or not available'
                return rollback_result
            
            # Restore from backup
            shutil.copy2(backup_path, target_file)
            
            # Verify rollback
            verification_result = self._verify_rollback(target_file, backup_path)
            rollback_result['verification'] = verification_result
            
            if verification_result['success']:
                rollback_result['success'] = True
                logger.info(f"Rollback completed successfully for {deployment_id}")
            else:
                rollback_result['error'] = 'Rollback verification failed'
        
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            rollback_result['error'] = str(e)
        
        return rollback_result

    def _verify_rollback(self, target_file: str, backup_path: str) -> Dict[str, Any]:
        """
        Verifies that rollback was successful.
        
        Args:
            target_file: Path to target file
            backup_path: Path to backup file
            
        Returns:
            Dictionary with verification results
        """
        verification_result = {
            'success': False
        }

        try:
            if os.path.exists(target_file) and os.path.exists(backup_path):
                with open(target_file, 'r') as f:
                    target_content = f.read()
                
                with open(backup_path, 'r') as f:
                    backup_content = f.read()
                
                if target_content == backup_content:
                    verification_result['success'] = True
                else:
                    verification_result['error'] = 'Content mismatch after rollback'
            else:
                verification_result['error'] = 'Files missing for rollback verification'
        
        except Exception as e:
            verification_result['error'] = str(e)
        
        return verification_result

    def _store_deployment_record(self, deployment_record: Dict[str, Any]):
        """
        Stores deployment record in history and knowledge repository.
        
        Args:
            deployment_record: The deployment record to store
        """
        # Add to deployment history
        self.deployment_history.append(deployment_record)
        
        # Keep only last 50 deployment records
        if len(self.deployment_history) > 50:
            self.deployment_history = self.deployment_history[-50:]
        
        # Store in knowledge repository if available
        if self.knowledge_repository:
            self.knowledge_repository.add_self_development_history({
                'type': 'code_deployment',
                'deployment_data': deployment_record,
                'timestamp': deployment_record['timestamp']
            })

    def get_deployment_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Gets the deployment history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of deployment records
        """
        return self.deployment_history[-limit:] if limit else self.deployment_history.copy()

    def get_deployment_statistics(self) -> Dict[str, Any]:
        """
        Gets statistics about deployment activities.
        
        Returns:
            Dictionary containing deployment statistics
        """
        total_deployments = len(self.deployment_history)
        successful_deployments = sum(1 for d in self.deployment_history if d.get('status') == 'completed')
        
        # Strategy distribution
        strategy_counts = {}
        for deployment in self.deployment_history:
            strategy = deployment.get('strategy', 'unknown')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # Recent activity
        from datetime import timedelta
        recent_deployments = [
            d for d in self.deployment_history
            if datetime.now() - datetime.fromisoformat(d['timestamp']) < timedelta(days=7)
        ]
        
        return {
            'total_deployments': total_deployments,
            'successful_deployments': successful_deployments,
            'success_rate': successful_deployments / max(total_deployments, 1),
            'recent_deployments_7_days': len(recent_deployments),
            'strategy_distribution': strategy_counts,
            'available_strategies': list(self.deployment_strategies.keys())
        }

    def cleanup_old_backups(self, days_old: int = 30):
        """
        Cleans up old backup files.
        
        Args:
            days_old: Remove backups older than this many days
        """
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=days_old)
            
            removed_count = 0
            for filename in os.listdir(self.backup_directory):
                if filename.endswith('.backup'):
                    file_path = os.path.join(self.backup_directory, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old backup files")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")

    def get_available_strategies(self) -> List[str]:
        """
        Gets the list of available deployment strategies.
        
        Returns:
            List of strategy names
        """
        return list(self.deployment_strategies.keys())

