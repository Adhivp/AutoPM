"""
Risk Prediction Service - ML-based risk prediction for projects
Uses Random Forest Classifier for multi-class risk prediction
Features auto-training as new data arrives
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import numpy as np
import pickle
import os
from pathlib import Path
import json

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Warning: scikit-learn not installed. ML features will be limited.")
    SKLEARN_AVAILABLE = False

from models.database_models import (
    ProjectMetadata, JiraTask, GitHubActivity, ResourceAllocation,
    TaskDependency, HistoricalProjectPerformance, TeamCommunicationLog,
    EmployeeProfile
)
from services.sentiment_service import SentimentService


class RiskPredictionService:
    """
    ML-based Risk Prediction Service
    
    Models Used:
    1. Random Forest Classifier - Main model for risk classification
       - Ensemble of decision trees, robust to overfitting
       - Handles non-linear relationships well
       - Provides feature importance scores
    
    2. Gradient Boosting Classifier - Alternative/ensemble model
       - Sequential tree building for better accuracy
       - Good for imbalanced datasets
    
    Risk Categories:
    - LOW (0): < 20% risk score
    - MEDIUM (1): 20-50% risk score
    - HIGH (2): 50-80% risk score
    - CRITICAL (3): > 80% risk score
    """
    
    def __init__(self, model_dir: str = "ml_models"):
        """Initialize the risk prediction service"""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model_path = self.model_dir / "risk_model.pkl"
        self.scaler_path = self.model_dir / "scaler.pkl"
        self.metadata_path = self.model_dir / "model_metadata.json"
        
        self.model = None
        self.scaler = None
        self.metadata = {}
        self.sentiment_service = SentimentService()
        
        # Load existing model if available
        self.load_model()
    
    def extract_features(self, db: Session, project_id: str) -> Optional[Dict[str, float]]:
        """
        Extract features from database for a project
        
        Feature Engineering:
        1. Schedule Features: task completion rate, overdue ratio
        2. Quality Features: build failure rate, defect density
        3. Resource Features: overtime ratio, workload variance
        4. Dependency Features: blocked task ratio, external dependency count
        5. Team Features: sentiment scores, communication frequency
        6. Historical Features: similar project outcomes
        """
        try:
            project = db.query(ProjectMetadata).filter(
                ProjectMetadata.project_id == project_id
            ).first()
            
            if not project:
                return None
            
            # Initialize features
            features = {}
            
            # === SCHEDULE FEATURES ===
            total_tasks = db.query(JiraTask).filter(
                JiraTask.project_id == project_id
            ).count()
            
            if total_tasks > 0:
                completed_tasks = db.query(JiraTask).filter(
                    and_(JiraTask.project_id == project_id, JiraTask.status == 'Done')
                ).count()
                
                features['task_completion_rate'] = completed_tasks / total_tasks
                
                overdue_tasks = db.query(JiraTask).filter(
                    and_(
                        JiraTask.project_id == project_id,
                        JiraTask.status != 'Done',
                        JiraTask.created_date < datetime.now() - timedelta(days=14)
                    )
                ).count()
                features['overdue_task_ratio'] = overdue_tasks / total_tasks
                
                # Priority distribution
                critical_tasks = db.query(JiraTask).filter(
                    and_(
                        JiraTask.project_id == project_id,
                        JiraTask.priority == 'Critical',
                        JiraTask.status != 'Done'
                    )
                ).count()
                features['critical_task_ratio'] = critical_tasks / total_tasks
            else:
                features['task_completion_rate'] = 0.0
                features['overdue_task_ratio'] = 0.0
                features['critical_task_ratio'] = 0.0
            
            # === QUALITY FEATURES ===
            total_prs = db.query(GitHubActivity).filter(
                GitHubActivity.project_id == project_id
            ).count()
            
            if total_prs > 0:
                failed_builds = db.query(GitHubActivity).filter(
                    and_(
                        GitHubActivity.project_id == project_id,
                        GitHubActivity.build_status == 'Failed'
                    )
                ).count()
                features['build_failure_rate'] = failed_builds / total_prs
                
                # Average test coverage delta
                avg_coverage = db.query(func.avg(GitHubActivity.test_coverage_delta)).filter(
                    and_(
                        GitHubActivity.project_id == project_id,
                        GitHubActivity.test_coverage_delta.isnot(None)
                    )
                ).scalar()
                features['avg_test_coverage_delta'] = float(avg_coverage) if avg_coverage else 0.0
                
                # PR review time (open PRs aging)
                open_prs = db.query(GitHubActivity).filter(
                    and_(
                        GitHubActivity.project_id == project_id,
                        GitHubActivity.status == 'Open',
                        GitHubActivity.created_at.isnot(None)
                    )
                ).all()
                
                if open_prs:
                    avg_pr_age = sum([
                        (datetime.now() - pr.created_at).days 
                        for pr in open_prs if pr.created_at
                    ]) / len(open_prs)
                    features['avg_pr_age_days'] = avg_pr_age
                else:
                    features['avg_pr_age_days'] = 0.0
            else:
                features['build_failure_rate'] = 0.0
                features['avg_test_coverage_delta'] = 0.0
                features['avg_pr_age_days'] = 0.0
            
            # === RESOURCE FEATURES ===
            recent_allocations = db.query(ResourceAllocation).filter(
                and_(
                    ResourceAllocation.project_id == project_id,
                    ResourceAllocation.week_start_date >= datetime.now().date() - timedelta(days=30)
                )
            ).all()
            
            if recent_allocations:
                total_overtime = sum([a.overtime_hours for a in recent_allocations])
                total_logged = sum([a.logged_hours for a in recent_allocations])
                
                features['overtime_ratio'] = total_overtime / total_logged if total_logged > 0 else 0.0
                
                # Workload variance across team members
                employee_hours = {}
                for alloc in recent_allocations:
                    if alloc.employee_id not in employee_hours:
                        employee_hours[alloc.employee_id] = 0
                    employee_hours[alloc.employee_id] += alloc.logged_hours
                
                if len(employee_hours) > 1:
                    hours_list = list(employee_hours.values())
                    features['workload_variance'] = np.var(hours_list)
                else:
                    features['workload_variance'] = 0.0
            else:
                features['overtime_ratio'] = 0.0
                features['workload_variance'] = 0.0
            
            # === DEPENDENCY FEATURES ===
            all_dependencies = db.query(TaskDependency).join(
                JiraTask, TaskDependency.dependent_task_id == JiraTask.issue_id
            ).filter(JiraTask.project_id == project_id).all()
            
            if all_dependencies:
                at_risk_deps = [d for d in all_dependencies if d.status in ['At Risk', 'Delayed']]
                features['dependency_risk_ratio'] = len(at_risk_deps) / len(all_dependencies)
                
                external_deps = [d for d in all_dependencies if d.dependency_type == 'External']
                features['external_dependency_ratio'] = len(external_deps) / len(all_dependencies)
            else:
                features['dependency_risk_ratio'] = 0.0
                features['external_dependency_ratio'] = 0.0
            
            # Blocked tasks
            blocked_tasks = db.query(JiraTask).filter(
                and_(
                    JiraTask.project_id == project_id,
                    JiraTask.status == 'In Progress'
                )
            ).all()
            
            # Check if tasks have blocking dependencies
            blocked_count = 0
            for task in blocked_tasks:
                has_blocker = db.query(TaskDependency).filter(
                    and_(
                        TaskDependency.dependent_task_id == task.issue_id,
                        TaskDependency.status != 'On Track'
                    )
                ).first()
                if has_blocker:
                    blocked_count += 1
            
            features['blocked_task_ratio'] = blocked_count / len(blocked_tasks) if blocked_tasks else 0.0
            
            # === TEAM/SENTIMENT FEATURES ===
            try:
                sentiment_data = self.sentiment_service.analyze_project_sentiment(
                    db, project_id, days_back=30
                )
                features['overall_sentiment_score'] = sentiment_data.get('overall_sentiment_score', 0.5)
                features['negative_sentiment_ratio'] = sentiment_data.get('negative_ratio', 0.0)
            except Exception as e:
                print(f"Error getting sentiment: {e}")
                features['overall_sentiment_score'] = 0.5
                features['negative_sentiment_ratio'] = 0.0
            
            # Communication frequency
            recent_messages = db.query(TeamCommunicationLog).filter(
                and_(
                    TeamCommunicationLog.project_id == project_id,
                    TeamCommunicationLog.timestamp >= datetime.now() - timedelta(days=7)
                )
            ).count()
            features['weekly_message_count'] = recent_messages
            
            blocker_messages = db.query(TeamCommunicationLog).filter(
                and_(
                    TeamCommunicationLog.project_id == project_id,
                    TeamCommunicationLog.is_blocker_signal == True,
                    TeamCommunicationLog.timestamp >= datetime.now() - timedelta(days=7)
                )
            ).count()
            features['blocker_signal_count'] = blocker_messages
            
            # === TIMELINE FEATURES ===
            if project.start_date and project.target_end_date:
                total_duration = (project.target_end_date - project.start_date).days
                elapsed = (datetime.now().date() - project.start_date).days
                
                features['project_progress_ratio'] = elapsed / total_duration if total_duration > 0 else 0.0
                
                # Schedule pressure (tasks remaining vs time remaining)
                remaining_days = (project.target_end_date - datetime.now().date()).days
                remaining_tasks = db.query(JiraTask).filter(
                    and_(
                        JiraTask.project_id == project_id,
                        JiraTask.status != 'Done'
                    )
                ).count()
                
                features['tasks_per_remaining_day'] = remaining_tasks / max(remaining_days, 1)
            else:
                features['project_progress_ratio'] = 0.0
                features['tasks_per_remaining_day'] = 0.0
            
            # === TEAM SIZE & COMPOSITION ===
            team_members = db.query(EmployeeProfile).join(
                ResourceAllocation, EmployeeProfile.employee_id == ResourceAllocation.employee_id
            ).filter(
                ResourceAllocation.project_id == project_id
            ).distinct().count()
            features['team_size'] = team_members
            
            return features
        
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return None
    
    def prepare_training_data(self, db: Session) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare training data from historical projects
        
        Returns:
            X: Feature matrix
            y: Risk labels (0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL)
            feature_names: List of feature names
        """
        historical_projects = db.query(HistoricalProjectPerformance).all()
        
        X_list = []
        y_list = []
        feature_names = []
        
        for hist_project in historical_projects:
            # Calculate risk score based on historical data
            risk_score = self._calculate_historical_risk_score(hist_project)
            
            # Convert to risk category
            if risk_score < 20:
                risk_category = 0  # LOW
            elif risk_score < 50:
                risk_category = 1  # MEDIUM
            elif risk_score < 80:
                risk_category = 2  # HIGH
            else:
                risk_category = 3  # CRITICAL
            
            # Create synthetic features from historical data
            features = {
                'task_completion_rate': 0.7 + np.random.normal(0, 0.1),
                'overdue_task_ratio': hist_project.delay_days / 100.0 if hist_project.delay_days else 0.0,
                'critical_task_ratio': 0.1 + np.random.normal(0, 0.05),
                'build_failure_rate': hist_project.integration_issues_count / 50.0 if hist_project.integration_issues_count else 0.0,
                'avg_test_coverage_delta': -2.0 if hist_project.defect_density and hist_project.defect_density > 5 else 1.0,
                'avg_pr_age_days': 3 + np.random.normal(0, 1),
                'overtime_ratio': 0.15 + np.random.normal(0, 0.05) if hist_project.delay_days and hist_project.delay_days > 10 else 0.05,
                'workload_variance': 20 + np.random.normal(0, 5),
                'dependency_risk_ratio': 0.3 if 'late_dependency' in (hist_project.root_causes or []) else 0.1,
                'external_dependency_ratio': 0.2 + np.random.normal(0, 0.05),
                'blocked_task_ratio': 0.15 if 'late_dependency' in (hist_project.root_causes or []) else 0.05,
                'overall_sentiment_score': 0.4 if hist_project.delay_days and hist_project.delay_days > 15 else 0.6,
                'negative_sentiment_ratio': 0.3 if hist_project.delay_days else 0.1,
                'weekly_message_count': 15 + np.random.normal(0, 5),
                'blocker_signal_count': 3 if hist_project.delay_days else 1,
                'project_progress_ratio': 0.5 + np.random.normal(0, 0.2),
                'tasks_per_remaining_day': 2.0 if hist_project.delay_days else 0.8,
                'team_size': 8 + int(np.random.normal(0, 2))
            }
            
            X_list.append(list(features.values()))
            y_list.append(risk_category)
            
            if not feature_names:
                feature_names = list(features.keys())
        
        # Add some synthetic data if we don't have enough historical data
        if len(X_list) < 50:
            print("Insufficient historical data. Generating synthetic training data...")
            synthetic_data = self._generate_synthetic_training_data(50 - len(X_list), feature_names)
            X_list.extend(synthetic_data['X'])
            y_list.extend(synthetic_data['y'])
        
        return np.array(X_list), np.array(y_list), feature_names
    
    def _generate_synthetic_training_data(self, n_samples: int, feature_names: List[str]) -> Dict:
        """Generate synthetic training data for initial model training"""
        X_synthetic = []
        y_synthetic = []
        
        for _ in range(n_samples):
            # Generate features with correlations to risk
            risk_category = np.random.choice([0, 1, 2, 3], p=[0.3, 0.4, 0.2, 0.1])
            
            # Adjust features based on risk category
            if risk_category == 0:  # LOW
                features = [0.85, 0.05, 0.05, 0.02, 2.0, 2.0, 0.05, 15, 0.05, 0.1, 0.03, 0.7, 0.05, 20, 1, 0.4, 0.5, 8]
            elif risk_category == 1:  # MEDIUM
                features = [0.70, 0.15, 0.12, 0.08, 0.5, 3.5, 0.12, 25, 0.15, 0.15, 0.10, 0.55, 0.15, 18, 2, 0.6, 1.2, 7]
            elif risk_category == 2:  # HIGH
                features = [0.50, 0.30, 0.20, 0.15, -1.0, 5.0, 0.22, 40, 0.30, 0.25, 0.20, 0.35, 0.30, 12, 4, 0.75, 2.0, 6]
            else:  # CRITICAL
                features = [0.30, 0.50, 0.35, 0.25, -3.0, 7.0, 0.35, 60, 0.45, 0.35, 0.35, 0.25, 0.45, 8, 6, 0.85, 3.5, 5]
            
            # Add noise
            features = [f + np.random.normal(0, 0.1) for f in features]
            
            X_synthetic.append(features)
            y_synthetic.append(risk_category)
        
        return {'X': X_synthetic, 'y': y_synthetic}
    
    def _calculate_historical_risk_score(self, hist_project: HistoricalProjectPerformance) -> float:
        """Calculate risk score from historical project data"""
        score = 0.0
        
        # Delay factor (0-40 points)
        if hist_project.delay_days:
            score += min(hist_project.delay_days * 2, 40)
        
        # Defect density factor (0-30 points)
        if hist_project.defect_density:
            score += min(hist_project.defect_density * 5, 30)
        
        # Integration issues (0-20 points)
        if hist_project.integration_issues_count:
            score += min(hist_project.integration_issues_count * 2, 20)
        
        # Compliance audit (0-10 points)
        if hist_project.compliance_audit_result == 'Major NC':
            score += 10
        elif hist_project.compliance_audit_result == 'Minor NC':
            score += 5
        
        return min(score, 100)
    
    def train_model(self, db: Session, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train the risk prediction model
        
        Args:
            db: Database session
            force_retrain: Force retraining even if model exists
        
        Returns:
            Training results and metrics
        """
        if not SKLEARN_AVAILABLE:
            return {
                'status': 'error',
                'message': 'scikit-learn not installed. Please install: pip install scikit-learn'
            }
        
        try:
            print("Preparing training data...")
            X, y, feature_names = self.prepare_training_data(db)
            
            if len(X) < 10:
                return {
                    'status': 'error',
                    'message': 'Insufficient training data. Need at least 10 samples.'
                }
            
            print(f"Training with {len(X)} samples, {len(feature_names)} features")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            print("Training Random Forest model...")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=min(5, len(X_train)))
            
            # Feature importance
            feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            # Save model and metadata
            self.metadata = {
                'trained_at': datetime.now().isoformat(),
                'n_samples': len(X),
                'n_features': len(feature_names),
                'feature_names': feature_names,
                'accuracy': float(accuracy),
                'cv_mean_score': float(cv_scores.mean()),
                'cv_std_score': float(cv_scores.std()),
                'model_type': 'RandomForestClassifier',
                'top_features': sorted_features[:10]
            }
            
            self.save_model()
            
            print(f"Model trained successfully! Accuracy: {accuracy:.2%}")
            
            return {
                'status': 'success',
                'accuracy': accuracy,
                'cv_score': cv_scores.mean(),
                'n_samples': len(X),
                'feature_importance': sorted_features[:10],
                'metadata': self.metadata
            }
        
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def predict_risk(self, db: Session, project_id: str) -> Dict[str, Any]:
        """
        Predict risk for a project
        
        Returns:
            Risk prediction with scores, category, and contributing factors
        """
        try:
            # Check if model is trained
            if self.model is None or self.scaler is None:
                return {
                    'status': 'error',
                    'message': 'Model not trained. Please train the model first.'
                }
            
            # Extract features
            features = self.extract_features(db, project_id)
            if features is None:
                return {
                    'status': 'error',
                    'message': 'Could not extract features for project'
                }
            
            # Prepare feature vector
            feature_vector = np.array([list(features.values())])
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict
            risk_category = self.model.predict(feature_vector_scaled)[0]
            risk_probabilities = self.model.predict_proba(feature_vector_scaled)[0]
            
            # Map category to label
            risk_labels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            risk_label = risk_labels[risk_category]
            
            # Calculate overall risk score (0-100)
            risk_score = (risk_probabilities[1] * 35 + 
                         risk_probabilities[2] * 65 + 
                         risk_probabilities[3] * 100)
            
            # Identify top risk factors
            feature_names = self.metadata.get('feature_names', list(features.keys()))
            feature_importance = self.model.feature_importances_
            
            # Get high-risk features (above threshold)
            risk_factors = []
            for fname, fvalue, importance in zip(feature_names, features.values(), feature_importance):
                if self._is_high_risk_value(fname, fvalue):
                    risk_factors.append({
                        'feature': fname,
                        'value': fvalue,
                        'importance': float(importance)
                    })
            
            risk_factors.sort(key=lambda x: x['importance'], reverse=True)
            
            # Calculate dimension scores
            dimension_scores = self._calculate_dimension_scores(features)
            
            return {
                'status': 'success',
                'project_id': project_id,
                'risk_category': risk_label,
                'risk_score': float(risk_score),
                'confidence': float(max(risk_probabilities)),
                'probabilities': {
                    'LOW': float(risk_probabilities[0]),
                    'MEDIUM': float(risk_probabilities[1]),
                    'HIGH': float(risk_probabilities[2]),
                    'CRITICAL': float(risk_probabilities[3])
                },
                'top_risk_factors': risk_factors[:5],
                'dimension_scores': dimension_scores,
                'features': features,
                'predicted_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error predicting risk: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _is_high_risk_value(self, feature_name: str, value: float) -> bool:
        """Check if a feature value indicates high risk"""
        risk_thresholds = {
            'overdue_task_ratio': 0.2,
            'critical_task_ratio': 0.15,
            'build_failure_rate': 0.1,
            'overtime_ratio': 0.15,
            'dependency_risk_ratio': 0.25,
            'blocked_task_ratio': 0.15,
            'negative_sentiment_ratio': 0.25,
            'blocker_signal_count': 3,
            'tasks_per_remaining_day': 2.0
        }
        
        if feature_name in risk_thresholds:
            return value > risk_thresholds[feature_name]
        
        # Inverted thresholds (low values are risky)
        if feature_name == 'task_completion_rate' and value < 0.6:
            return True
        if feature_name == 'overall_sentiment_score' and value < 0.4:
            return True
        
        return False
    
    def _calculate_dimension_scores(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate risk scores for different dimensions"""
        dimensions = {
            'schedule_risk': (
                features.get('overdue_task_ratio', 0) * 40 +
                features.get('tasks_per_remaining_day', 0) * 10 +
                (1 - features.get('task_completion_rate', 1)) * 50
            ),
            'quality_risk': (
                features.get('build_failure_rate', 0) * 50 +
                max(0, -features.get('avg_test_coverage_delta', 0)) * 5 +
                features.get('avg_pr_age_days', 0) * 3
            ),
            'resource_risk': (
                features.get('overtime_ratio', 0) * 60 +
                features.get('workload_variance', 0) * 0.5
            ),
            'dependency_risk': (
                features.get('dependency_risk_ratio', 0) * 50 +
                features.get('blocked_task_ratio', 0) * 50
            ),
            'team_risk': (
                (1 - features.get('overall_sentiment_score', 0.5)) * 60 +
                features.get('negative_sentiment_ratio', 0) * 30 +
                features.get('blocker_signal_count', 0) * 2
            )
        }
        
        # Normalize to 0-100
        return {k: min(v, 100.0) for k, v in dimensions.items()}
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and metadata"""
        if self.model is None:
            return {
                'status': 'not_trained',
                'message': 'Model has not been trained yet'
            }
        
        return {
            'status': 'ready',
            'metadata': self.metadata,
            'model_exists': self.model_path.exists(),
            'scaler_exists': self.scaler_path.exists()
        }
    
    def save_model(self):
        """Save model, scaler, and metadata to disk"""
        if self.model:
            joblib.dump(self.model, self.model_path)
            print(f"Model saved to {self.model_path}")
        
        if self.scaler:
            joblib.dump(self.scaler, self.scaler_path)
            print(f"Scaler saved to {self.scaler_path}")
        
        if self.metadata:
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            print(f"Metadata saved to {self.metadata_path}")
    
    def load_model(self):
        """Load model, scaler, and metadata from disk"""
        try:
            if self.model_path.exists() and SKLEARN_AVAILABLE:
                self.model = joblib.load(self.model_path)
                print(f"Model loaded from {self.model_path}")
            
            if self.scaler_path.exists() and SKLEARN_AVAILABLE:
                self.scaler = joblib.load(self.scaler_path)
                print(f"Scaler loaded from {self.scaler_path}")
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                print(f"Metadata loaded from {self.metadata_path}")
        
        except Exception as e:
            print(f"Error loading model: {str(e)}")
    
    def check_auto_training_needed(self, db: Session) -> bool:
        """Check if model needs retraining based on new data"""
        if not self.metadata:
            return True
        
        trained_at = datetime.fromisoformat(self.metadata.get('trained_at', '2020-01-01'))
        days_since_training = (datetime.now() - trained_at).days
        
        # Retrain if more than 7 days old
        if days_since_training > 7:
            return True
        
        # Check if new historical data available
        hist_count = db.query(HistoricalProjectPerformance).count()
        if hist_count > self.metadata.get('n_samples', 0) * 1.2:  # 20% more data
            return True
        
        return False


# Singleton instance
_risk_service = None

def get_risk_service() -> RiskPredictionService:
    """Get or create risk prediction service instance"""
    global _risk_service
    if _risk_service is None:
        _risk_service = RiskPredictionService()
    return _risk_service
