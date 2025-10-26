"""
Row-Level Security (RLS) Policy Engine
Dynamically filters query results based on security policies
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
from datetime import datetime

from app.models.security import SecurityPolicy, PolicyType
from app.models.user import User, UserRole


class RLSEngine:
    """
    Row-Level Security Engine
    Evaluates and applies RLS policies to queries
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_policies(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        user: Optional[User] = None
    ) -> List[SecurityPolicy]:
        """
        Get all active RLS policies for a given resource
        
        Args:
            resource_type: Type of resource (datasource, query, dashboard, etc.)
            resource_id: Specific resource ID (None for all resources)
            user: Current user (for filtering by user/role)
        
        Returns:
            List of active RLS policies sorted by priority
        """
        query = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.policy_type == PolicyType.ROW_LEVEL,
            SecurityPolicy.is_active == True,
            SecurityPolicy.resource_type == resource_type
        )
        
        # Filter by resource_id if specified, or include global policies
        if resource_id:
            query = query.filter(
                or_(
                    SecurityPolicy.resource_id == resource_id,
                    SecurityPolicy.resource_id.is_(None)
                )
            )
        else:
            query = query.filter(SecurityPolicy.resource_id.is_(None))
        
        # Filter by tenant
        if user and user.tenant_id:
            query = query.filter(SecurityPolicy.tenant_id == user.tenant_id)
        
        # Get all policies
        policies = query.order_by(SecurityPolicy.priority.desc()).all()
        
        # Filter by user/role applicability
        applicable_policies = []
        for policy in policies:
            if self._is_policy_applicable(policy, user):
                applicable_policies.append(policy)
        
        return applicable_policies
    
    def _is_policy_applicable(self, policy: SecurityPolicy, user: Optional[User]) -> bool:
        """Check if a policy applies to the current user"""
        if not user:
            return False
        
        # Check if applies to specific users
        if policy.applies_to_users and user.id in policy.applies_to_users:
            return True
        
        # Check if applies to user's role
        if policy.applies_to_roles and user.role.value in policy.applies_to_roles:
            return True
        
        # If no specific users/roles, applies to all
        if not policy.applies_to_users and not policy.applies_to_roles:
            return True
        
        return False
    
    def build_where_clause(
        self,
        policies: List[SecurityPolicy],
        user: User,
        table_alias: str = None
    ) -> str:
        """
        Build SQL WHERE clause from RLS policies
        
        Args:
            policies: List of RLS policies to apply
            user: Current user (for variable replacement)
            table_alias: Optional table alias for multi-table queries
        
        Returns:
            SQL WHERE clause string
        """
        if not policies:
            return ""
        
        conditions = []
        
        for policy in policies:
            condition = self._policy_to_sql(policy, user, table_alias)
            if condition:
                conditions.append(f"({condition})")
        
        if not conditions:
            return ""
        
        # Combine conditions with AND (all policies must be satisfied)
        where_clause = " AND ".join(conditions)
        return where_clause
    
    def _policy_to_sql(
        self,
        policy: SecurityPolicy,
        user: User,
        table_alias: str = None
    ) -> str:
        """
        Convert a single policy to SQL condition
        
        Policy rules format:
        {
            "conditions": [
                {
                    "field": "user_id",
                    "operator": "equals",
                    "value": "{{current_user.id}}"
                },
                {
                    "field": "department",
                    "operator": "in",
                    "value": "{{current_user.department}}"
                }
            ],
            "logic": "AND"  # or "OR"
        }
        """
        rules = policy.rules
        
        if not rules or "conditions" not in rules:
            return ""
        
        conditions = rules.get("conditions", [])
        logic = rules.get("logic", "AND").upper()
        
        sql_conditions = []
        
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator", "equals")
            value = condition.get("value")
            
            # Replace template variables
            value = self._replace_variables(value, user)
            
            # Build SQL condition
            sql_condition = self._build_condition(field, operator, value, table_alias)
            if sql_condition:
                sql_conditions.append(sql_condition)
        
        if not sql_conditions:
            return ""
        
        # Combine with specified logic
        separator = f" {logic} "
        return separator.join(sql_conditions)
    
    def _replace_variables(self, value: Any, user: User) -> Any:
        """
        Replace template variables in policy values
        
        Supported variables:
        - {{current_user.id}}
        - {{current_user.email}}
        - {{current_user.role}}
        - {{current_user.tenant_id}}
        - {{current_user.full_name}}
        """
        if not isinstance(value, str):
            return value
        
        replacements = {
            "{{current_user.id}}": user.id,
            "{{current_user.email}}": user.email,
            "{{current_user.role}}": user.role.value,
            "{{current_user.tenant_id}}": user.tenant_id or "",
            "{{current_user.full_name}}": user.full_name or "",
        }
        
        result = value
        for placeholder, replacement in replacements.items():
            result = result.replace(placeholder, str(replacement))
        
        return result
    
    def _build_condition(
        self,
        field: str,
        operator: str,
        value: Any,
        table_alias: str = None
    ) -> str:
        """Build SQL condition from field, operator, and value"""
        
        # Add table alias if provided
        field_name = f"{table_alias}.{field}" if table_alias else field
        
        # Escape value for SQL injection prevention
        if isinstance(value, str):
            value = value.replace("'", "''")
            value = f"'{value}'"
        elif value is None:
            value = "NULL"
        
        # Build condition based on operator
        operator_map = {
            "equals": f"{field_name} = {value}",
            "not_equals": f"{field_name} != {value}",
            "greater_than": f"{field_name} > {value}",
            "less_than": f"{field_name} < {value}",
            "greater_or_equal": f"{field_name} >= {value}",
            "less_or_equal": f"{field_name} <= {value}",
            "in": f"{field_name} IN ({value})",
            "not_in": f"{field_name} NOT IN ({value})",
            "like": f"{field_name} LIKE {value}",
            "not_like": f"{field_name} NOT LIKE {value}",
            "is_null": f"{field_name} IS NULL",
            "is_not_null": f"{field_name} IS NOT NULL",
            "between": f"{field_name} BETWEEN {value}",
        }
        
        return operator_map.get(operator, f"{field_name} = {value}")
    
    def apply_rls_to_query(
        self,
        original_query: str,
        resource_type: str,
        resource_id: Optional[str],
        user: User
    ) -> str:
        """
        Apply RLS policies to an SQL query
        
        Args:
            original_query: Original SQL query
            resource_type: Type of resource being queried
            resource_id: Specific resource ID
            user: Current user
        
        Returns:
            Modified SQL query with RLS filters applied
        """
        # Get applicable policies
        policies = self.get_active_policies(resource_type, resource_id, user)
        
        if not policies:
            return original_query
        
        # Build WHERE clause from policies
        rls_where = self.build_where_clause(policies, user)
        
        if not rls_where:
            return original_query
        
        # Inject RLS filters into query
        modified_query = self._inject_where_clause(original_query, rls_where)
        
        return modified_query
    
    def _inject_where_clause(self, original_query: str, rls_where: str) -> str:
        """
        Inject RLS WHERE clause into SQL query
        Handles queries with and without existing WHERE clauses
        """
        query_upper = original_query.upper()
        
        # Check if query already has WHERE clause
        if "WHERE" in query_upper:
            # Find WHERE position
            where_pos = query_upper.index("WHERE")
            
            # Insert RLS conditions after existing WHERE
            modified = (
                original_query[:where_pos + 5] +  # Up to and including "WHERE"
                f" ({rls_where}) AND " +
                original_query[where_pos + 5:]  # Rest of the query
            )
        else:
            # No WHERE clause, add one before GROUP BY, ORDER BY, or LIMIT
            keywords = ["GROUP BY", "ORDER BY", "LIMIT", "OFFSET"]
            insert_pos = len(original_query)
            
            for keyword in keywords:
                if keyword in query_upper:
                    pos = query_upper.index(keyword)
                    if pos < insert_pos:
                        insert_pos = pos
            
            # Insert WHERE clause
            modified = (
                original_query[:insert_pos] +
                f" WHERE {rls_where} " +
                original_query[insert_pos:]
            )
        
        return modified


class CLSEngine:
    """
    Column-Level Security Engine
    Filters columns from query results based on security policies
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_allowed_columns(
        self,
        resource_type: str,
        resource_id: Optional[str],
        all_columns: List[str],
        user: User
    ) -> List[str]:
        """
        Get list of columns the user is allowed to see
        
        Args:
            resource_type: Type of resource
            resource_id: Specific resource ID
            all_columns: List of all available columns
            user: Current user
        
        Returns:
            List of allowed column names
        """
        # Get CLS policies
        policies = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.policy_type == PolicyType.COLUMN_LEVEL,
            SecurityPolicy.is_active == True,
            SecurityPolicy.resource_type == resource_type
        ).all()
        
        # Filter policies applicable to this user
        applicable_policies = [
            p for p in policies
            if self._is_policy_applicable(p, user)
        ]
        
        if not applicable_policies:
            return all_columns  # No restrictions
        
        # Determine which columns to hide
        hidden_columns = set()
        
        for policy in applicable_policies:
            rules = policy.rules
            if "columns" in rules:
                action = rules.get("action", "hide")
                except_roles = rules.get("except_roles", [])
                
                # Skip if user's role is excepted
                if user.role.value in except_roles:
                    continue
                
                if action == "hide":
                    hidden_columns.update(rules["columns"])
        
        # Return columns not hidden
        allowed = [col for col in all_columns if col not in hidden_columns]
        return allowed
    
    def _is_policy_applicable(self, policy: SecurityPolicy, user: User) -> bool:
        """Check if policy applies to user"""
        if policy.applies_to_users and user.id in policy.applies_to_users:
            return True
        if policy.applies_to_roles and user.role.value in policy.applies_to_roles:
            return True
        if not policy.applies_to_users and not policy.applies_to_roles:
            return True
        return False
    
    def filter_result_columns(
        self,
        results: List[Dict[str, Any]],
        allowed_columns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter query results to only include allowed columns
        
        Args:
            results: List of result dictionaries
            allowed_columns: List of allowed column names
        
        Returns:
            Filtered results
        """
        if not results:
            return results
        
        filtered_results = []
        for row in results:
            filtered_row = {
                col: val for col, val in row.items()
                if col in allowed_columns
            }
            filtered_results.append(filtered_row)
        
        return filtered_results


# Singleton instances
_rls_engine = None
_cls_engine = None


def get_rls_engine(db: Session) -> RLSEngine:
    """Get RLS engine instance"""
    return RLSEngine(db)


def get_cls_engine(db: Session) -> CLSEngine:
    """Get CLS engine instance"""
    return CLSEngine(db)
