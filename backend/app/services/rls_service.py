"""
Row-Level Security (RLS) Service
Implements dynamic query filtering based on security policies
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.security import SecurityPolicy, PolicyType
from app.models.user import User
import re


class RLSEngine:
    """Row-Level Security Engine for dynamic query filtering"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def apply_rls_policies(
        self,
        query_sql: str,
        user: User,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> str:
        """
        Apply RLS policies to a SQL query
        
        Args:
            query_sql: Original SQL query
            user: Current user
            resource_type: Type of resource (datasource, query, dashboard)
            resource_id: Optional specific resource ID
            
        Returns:
            Modified SQL query with RLS filters applied
        """
        # Get applicable RLS policies
        policies = self._get_applicable_policies(
            user, resource_type, resource_id, PolicyType.ROW_LEVEL
        )
        
        if not policies:
            return query_sql
        
        # Apply policies in priority order
        modified_query = query_sql
        for policy in sorted(policies, key=lambda p: p.priority, reverse=True):
            modified_query = self._apply_policy_to_query(
                modified_query, policy, user
            )
        
        return modified_query
    
    def _get_applicable_policies(
        self,
        user: User,
        resource_type: str,
        resource_id: Optional[str],
        policy_type: PolicyType
    ) -> List[SecurityPolicy]:
        """Get all applicable security policies for user"""
        query = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.tenant_id == user.tenant_id,
            SecurityPolicy.policy_type == policy_type,
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
    
    def _apply_policy_to_query(
        self, query_sql: str, policy: SecurityPolicy, user: User
    ) -> str:
        """
        Apply a single policy to a SQL query
        
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
                    "operator": "equals",
                    "value": "{{current_user.department}}"
                }
            ],
            "logic": "AND"  # or "OR"
        }
        """
        rules = policy.rules
        conditions = rules.get("conditions", [])
        logic = rules.get("logic", "AND")
        
        if not conditions:
            return query_sql
        
        # Build WHERE clause from conditions
        where_clauses = []
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            # Replace template variables
            value = self._replace_template_vars(value, user)
            
            # Build condition SQL
            condition_sql = self._build_condition_sql(field, operator, value)
            if condition_sql:
                where_clauses.append(condition_sql)
        
        if not where_clauses:
            return query_sql
        
        # Combine conditions
        combined_condition = f" {logic} ".join(where_clauses)
        
        # Add to query
        modified_query = self._inject_where_clause(query_sql, combined_condition)
        
        return modified_query
    
    def _replace_template_vars(self, value: Any, user: User) -> Any:
        """Replace template variables like {{current_user.id}}"""
        if not isinstance(value, str):
            return value
        
        # Replace user variables
        value = value.replace("{{current_user.id}}", str(user.id))
        value = value.replace("{{current_user.email}}", user.email)
        value = value.replace("{{current_user.role}}", user.role)
        value = value.replace("{{current_user.tenant_id}}", user.tenant_id)
        
        # Add more replacements as needed
        if hasattr(user, 'department'):
            value = value.replace("{{current_user.department}}", str(user.department))
        
        return value
    
    def _build_condition_sql(self, field: str, operator: str, value: Any) -> str:
        """Build SQL condition from field, operator, and value"""
        operator_map = {
            "equals": "=",
            "not_equals": "!=",
            "greater_than": ">",
            "less_than": "<",
            "greater_or_equal": ">=",
            "less_or_equal": "<=",
            "contains": "LIKE",
            "not_contains": "NOT LIKE",
            "in": "IN",
            "not_in": "NOT IN",
            "is_null": "IS NULL",
            "is_not_null": "IS NOT NULL"
        }
        
        sql_operator = operator_map.get(operator, "=")
        
        if operator in ["is_null", "is_not_null"]:
            return f"{field} {sql_operator}"
        
        if operator == "contains":
            return f"{field} {sql_operator} '%{value}%'"
        
        if operator == "not_contains":
            return f"{field} {sql_operator} '%{value}%'"
        
        if operator in ["in", "not_in"]:
            if isinstance(value, list):
                value_str = ", ".join([f"'{v}'" for v in value])
                return f"{field} {sql_operator} ({value_str})"
        
        # Default: simple comparison
        if isinstance(value, str):
            return f"{field} {sql_operator} '{value}'"
        else:
            return f"{field} {sql_operator} {value}"
    
    def _inject_where_clause(self, query_sql: str, condition: str) -> str:
        """Inject WHERE clause into SQL query"""
        query_upper = query_sql.upper()
        
        # Check if query already has WHERE clause
        if "WHERE" in query_upper:
            # Add condition to existing WHERE
            where_pos = query_upper.find("WHERE")
            # Find the position after WHERE clause
            group_by_pos = query_upper.find("GROUP BY", where_pos)
            order_by_pos = query_upper.find("ORDER BY", where_pos)
            limit_pos = query_upper.find("LIMIT", where_pos)
            
            insert_pos = len(query_sql)
            if group_by_pos != -1:
                insert_pos = min(insert_pos, group_by_pos)
            if order_by_pos != -1:
                insert_pos = min(insert_pos, order_by_pos)
            if limit_pos != -1:
                insert_pos = min(insert_pos, limit_pos)
            
            # Insert AND condition
            return (
                query_sql[:insert_pos] +
                f" AND ({condition})" +
                query_sql[insert_pos:]
            )
        else:
            # Add new WHERE clause
            # Find position before GROUP BY, ORDER BY, or LIMIT
            insert_pos = len(query_sql)
            
            group_by_pos = query_upper.find("GROUP BY")
            order_by_pos = query_upper.find("ORDER BY")
            limit_pos = query_upper.find("LIMIT")
            
            if group_by_pos != -1:
                insert_pos = min(insert_pos, group_by_pos)
            if order_by_pos != -1:
                insert_pos = min(insert_pos, order_by_pos)
            if limit_pos != -1:
                insert_pos = min(insert_pos, limit_pos)
            
            return (
                query_sql[:insert_pos].rstrip() +
                f" WHERE ({condition}) " +
                query_sql[insert_pos:]
            )
    
    def evaluate_policy(
        self, policy: SecurityPolicy, user: User, test_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a policy against test data for testing purposes
        
        Returns:
            {
                "applies": bool,
                "conditions_met": bool,
                "explanation": str
            }
        """
        applies = self._policy_applies_to_user(policy, user)
        
        if not applies:
            return {
                "applies": False,
                "conditions_met": False,
                "explanation": "Policy does not apply to this user"
            }
        
        conditions = policy.rules.get("conditions", [])
        logic = policy.rules.get("logic", "AND")
        
        conditions_met = []
        explanations = []
        
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            # Replace template variables
            value = self._replace_template_vars(value, user)
            
            # Check against test data
            if test_data and field in test_data:
                test_value = test_data[field]
                met = self._evaluate_condition(test_value, operator, value)
                conditions_met.append(met)
                explanations.append(
                    f"{field} {operator} {value}: {'✓' if met else '✗'}"
                )
        
        # Evaluate based on logic
        if logic == "AND":
            all_met = all(conditions_met) if conditions_met else True
        else:  # OR
            all_met = any(conditions_met) if conditions_met else True
        
        return {
            "applies": True,
            "conditions_met": all_met,
            "explanation": f"Logic: {logic}, " + ", ".join(explanations)
        }
    
    def _evaluate_condition(self, test_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate a single condition"""
        try:
            if operator == "equals":
                return test_value == expected_value
            elif operator == "not_equals":
                return test_value != expected_value
            elif operator == "greater_than":
                return test_value > expected_value
            elif operator == "less_than":
                return test_value < expected_value
            elif operator == "greater_or_equal":
                return test_value >= expected_value
            elif operator == "less_or_equal":
                return test_value <= expected_value
            elif operator == "contains":
                return expected_value in str(test_value)
            elif operator == "not_contains":
                return expected_value not in str(test_value)
            elif operator == "in":
                return test_value in expected_value
            elif operator == "not_in":
                return test_value not in expected_value
            elif operator == "is_null":
                return test_value is None
            elif operator == "is_not_null":
                return test_value is not None
        except Exception:
            return False
        
        return False
