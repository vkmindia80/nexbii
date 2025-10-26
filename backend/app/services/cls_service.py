"""
Column-Level Security (CLS) Service
Implements column visibility and masking based on security policies
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.security import SecurityPolicy, PolicyType
from app.models.user import User


class CLSEngine:
    """Column-Level Security Engine for hiding/masking columns"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def apply_cls_policies(
        self,
        query_results: List[Dict[str, Any]],
        user: User,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply CLS policies to query results
        
        Args:
            query_results: List of result rows
            user: Current user
            resource_type: Type of resource
            resource_id: Optional specific resource ID
            
        Returns:
            Filtered results with columns hidden/masked
        """
        if not query_results:
            return query_results
        
        # Get applicable CLS policies
        policies = self._get_applicable_policies(
            user, resource_type, resource_id
        )
        
        if not policies:
            return query_results
        
        # Apply policies
        filtered_results = []
        for row in query_results:
            filtered_row = self._apply_policies_to_row(row, policies, user)
            filtered_results.append(filtered_row)
        
        return filtered_results
    
    def _get_applicable_policies(
        self,
        user: User,
        resource_type: str,
        resource_id: Optional[str]
    ) -> List[SecurityPolicy]:
        """Get all applicable CLS policies for user"""
        query = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.tenant_id == user.tenant_id,
            SecurityPolicy.policy_type == PolicyType.COLUMN_LEVEL,
            SecurityPolicy.is_active == True
        )
        
        # Filter by resource type
        if resource_type:
            query = query.filter(
                (SecurityPolicy.resource_type == resource_type) |
                (SecurityPolicy.resource_type == None)
            )
        
        # Filter by resource ID
        if resource_id:
            query = query.filter(
                (SecurityPolicy.resource_id == resource_id) |
                (SecurityPolicy.resource_id == None)
            )
        
        policies = query.all()
        
        # Filter policies that apply to this user
        applicable_policies = []
        for policy in policies:
            if self._policy_applies_to_user(policy, user):
                applicable_policies.append(policy)
        
        return applicable_policies
    
    def _policy_applies_to_user(self, policy: SecurityPolicy, user: User) -> bool:
        """Check if policy applies to the given user"""
        # Check for exception roles (users who can see everything)
        rules = policy.rules
        except_roles = rules.get("except_roles", [])
        if user.role in except_roles:
            return False
        
        # If policy applies to specific users
        if policy.applies_to_users and user.id in policy.applies_to_users:
            return True
        
        # If policy applies to specific roles
        if policy.applies_to_roles and user.role in policy.applies_to_roles:
            return True
        
        # If no specific users or roles, policy applies to all
        if not policy.applies_to_users and not policy.applies_to_roles:
            return True
        
        return False
    
    def _apply_policies_to_row(
        self, row: Dict[str, Any], policies: List[SecurityPolicy], user: User
    ) -> Dict[str, Any]:
        """
        Apply CLS policies to a single row
        
        Policy rules format:
        {
            "columns": ["email", "ssn", "salary"],
            "action": "hide",  # or "mask"
            "except_roles": ["admin"]
        }
        """
        filtered_row = row.copy()
        
        for policy in sorted(policies, key=lambda p: p.priority, reverse=True):
            rules = policy.rules
            columns = rules.get("columns", [])
            action = rules.get("action", "hide")
            
            for column in columns:
                if column in filtered_row:
                    if action == "hide":
                        # Remove column completely
                        filtered_row.pop(column, None)
                    elif action == "mask":
                        # Mask the value
                        filtered_row[column] = self._mask_value(
                            filtered_row[column], column
                        )
        
        return filtered_row
    
    def _mask_value(self, value: Any, column_name: str) -> str:
        """Mask a value based on column type"""
        if value is None:
            return None
        
        value_str = str(value)
        
        # Email masking
        if '@' in value_str:
            parts = value_str.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                masked_username = username[0] + ('*' * (len(username) - 1))
                return f"{masked_username}@{domain}"
        
        # Phone number masking (show last 4 digits)
        if column_name.lower() in ['phone', 'phone_number', 'mobile']:
            if len(value_str) >= 4:
                return '***-***-' + value_str[-4:]
        
        # SSN masking (show last 4 digits)
        if column_name.lower() in ['ssn', 'social_security']:
            if len(value_str) >= 4:
                return '***-**-' + value_str[-4:]
        
        # Credit card masking (show last 4 digits)
        if column_name.lower() in ['credit_card', 'card_number']:
            if len(value_str) >= 4:
                return '****-****-****-' + value_str[-4:]
        
        # Salary/financial masking
        if column_name.lower() in ['salary', 'income', 'revenue', 'amount']:
            return '***REDACTED***'
        
        # Default masking
        if len(value_str) <= 4:
            return '*' * len(value_str)
        else:
            return value_str[0] + ('*' * (len(value_str) - 2)) + value_str[-1]
    
    def get_visible_columns(
        self,
        all_columns: List[str],
        user: User,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> List[str]:
        """
        Get list of columns visible to user after applying CLS
        
        Returns:
            List of column names that user can see
        """
        # Get applicable CLS policies
        policies = self._get_applicable_policies(
            user, resource_type, resource_id
        )
        
        if not policies:
            return all_columns
        
        # Start with all columns
        visible_columns = set(all_columns)
        
        # Remove hidden columns based on policies
        for policy in policies:
            rules = policy.rules
            columns = rules.get("columns", [])
            action = rules.get("action", "hide")
            
            if action == "hide":
                for column in columns:
                    visible_columns.discard(column)
        
        return list(visible_columns)
    
    def get_masked_columns(
        self,
        user: User,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> List[str]:
        """
        Get list of columns that will be masked for user
        
        Returns:
            List of column names that will be masked
        """
        # Get applicable CLS policies
        policies = self._get_applicable_policies(
            user, resource_type, resource_id
        )
        
        if not policies:
            return []
        
        masked_columns = set()
        
        for policy in policies:
            rules = policy.rules
            columns = rules.get("columns", [])
            action = rules.get("action", "hide")
            
            if action == "mask":
                masked_columns.update(columns)
        
        return list(masked_columns)
    
    def preview_cls_effect(
        self,
        sample_data: Dict[str, Any],
        user: User,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview how CLS policies will affect sample data
        
        Returns:
            {
                "original": {...},
                "filtered": {...},
                "hidden_columns": [...],
                "masked_columns": [...]
            }
        """
        policies = self._get_applicable_policies(
            user, resource_type, resource_id
        )
        
        filtered_data = self._apply_policies_to_row(
            sample_data, policies, user
        )
        
        hidden_columns = []
        masked_columns = []
        
        for key in sample_data:
            if key not in filtered_data:
                hidden_columns.append(key)
            elif sample_data[key] != filtered_data.get(key):
                masked_columns.append(key)
        
        return {
            "original": sample_data,
            "filtered": filtered_data,
            "hidden_columns": hidden_columns,
            "masked_columns": masked_columns
        }
