"""
Security API Endpoints
Handles RLS, CLS, and Data Masking policies
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.security import SecurityPolicy, DataMaskingRule
from app.schemas.security import (
    SecurityPolicyCreate,
    SecurityPolicyUpdate,
    SecurityPolicyResponse,
    DataMaskingRuleCreate,
    DataMaskingRuleUpdate,
    DataMaskingRuleResponse,
    PolicyTestRequest,
    PolicyTestResponse
)
from app.services.rls_service import RLSEngine
from app.services.cls_service import CLSEngine
from app.services.data_masking_service import DataMaskingService
from app.services.audit_service import AuditService
import uuid

router = APIRouter()


# ===== Security Policies =====

@router.get("/policies", response_model=List[SecurityPolicyResponse])
def list_policies(
    policy_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all security policies"""
    query = db.query(SecurityPolicy).filter(
        SecurityPolicy.tenant_id == current_user.tenant_id
    )
    
    if policy_type:
        query = query.filter(SecurityPolicy.policy_type == policy_type)
    
    policies = query.offset(skip).limit(limit).all()
    return policies


@router.post("/policies", response_model=SecurityPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    policy_data: SecurityPolicyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new security policy"""
    policy = SecurityPolicy(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **policy_data.dict()
    )
    
    db.add(policy)
    db.commit()
    db.refresh(policy)
    
    # Log the action
    audit_service = AuditService(db)
    audit_service.log_security_policy_change(
        user=current_user,
        policy_id=policy.id,
        policy_name=policy.name,
        action="create"
    )
    
    return policy


@router.get("/policies/{policy_id}", response_model=SecurityPolicyResponse)
def get_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific security policy"""
    policy = db.query(SecurityPolicy).filter(
        SecurityPolicy.id == policy_id,
        SecurityPolicy.tenant_id == current_user.tenant_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    return policy


@router.put("/policies/{policy_id}", response_model=SecurityPolicyResponse)
def update_policy(
    policy_id: str,
    policy_data: SecurityPolicyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a security policy"""
    policy = db.query(SecurityPolicy).filter(
        SecurityPolicy.id == policy_id,
        SecurityPolicy.tenant_id == current_user.tenant_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Update fields
    for field, value in policy_data.dict(exclude_unset=True).items():
        setattr(policy, field, value)
    
    db.commit()
    db.refresh(policy)
    
    # Log the action
    audit_service = AuditService(db)
    audit_service.log_security_policy_change(
        user=current_user,
        policy_id=policy.id,
        policy_name=policy.name,
        action="update"
    )
    
    return policy


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a security policy"""
    policy = db.query(SecurityPolicy).filter(
        SecurityPolicy.id == policy_id,
        SecurityPolicy.tenant_id == current_user.tenant_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    policy_name = policy.name
    db.delete(policy)
    db.commit()
    
    # Log the action
    audit_service = AuditService(db)
    audit_service.log_security_policy_change(
        user=current_user,
        policy_id=policy_id,
        policy_name=policy_name,
        action="delete"
    )


@router.post("/policies/{policy_id}/test", response_model=PolicyTestResponse)
def test_policy(
    policy_id: str,
    test_request: PolicyTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test a security policy"""
    policy = db.query(SecurityPolicy).filter(
        SecurityPolicy.id == policy_id,
        SecurityPolicy.tenant_id == current_user.tenant_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    rls_engine = RLSEngine(db)
    result = rls_engine.evaluate_policy(
        policy=policy,
        user=current_user,
        test_data=test_request.test_data
    )
    
    return PolicyTestResponse(
        policy_applied=result["applies"],
        explanation=result["explanation"]
    )


# ===== Data Masking Rules =====

@router.get("/data-masking/rules", response_model=List[DataMaskingRuleResponse])
def list_masking_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all data masking rules"""
    rules = db.query(DataMaskingRule).filter(
        DataMaskingRule.tenant_id == current_user.tenant_id,
        DataMaskingRule.is_active == True
    ).all()
    
    return rules


@router.post("/data-masking/rules", response_model=DataMaskingRuleResponse, status_code=status.HTTP_201_CREATED)
def create_masking_rule(
    rule_data: DataMaskingRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new data masking rule"""
    masking_service = DataMaskingService(db)
    rule = masking_service.create_masking_rule(
        tenant_id=current_user.tenant_id,
        **rule_data.dict()
    )
    
    return rule


@router.put("/data-masking/rules/{rule_id}", response_model=DataMaskingRuleResponse)
def update_masking_rule(
    rule_id: str,
    rule_data: DataMaskingRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a data masking rule"""
    rule = db.query(DataMaskingRule).filter(
        DataMaskingRule.id == rule_id,
        DataMaskingRule.tenant_id == current_user.tenant_id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Masking rule not found"
        )
    
    for field, value in rule_data.dict(exclude_unset=True).items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.delete("/data-masking/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_masking_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a data masking rule"""
    rule = db.query(DataMaskingRule).filter(
        DataMaskingRule.id == rule_id,
        DataMaskingRule.tenant_id == current_user.tenant_id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Masking rule not found"
        )
    
    db.delete(rule)
    db.commit()
