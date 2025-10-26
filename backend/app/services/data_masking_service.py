"""
Data Masking Service
Implements comprehensive data masking for PII/PHI/PCI data
"""

import re
from typing import Any, Optional, Dict, List
from sqlalchemy.orm import Session
from app.models.security import DataMaskingRule, DataClassification


class DataMaskingService:
    """Service for masking sensitive data"""
    
    def __init__(self, db: Session):
        self.db = db
        # Predefined masking patterns
        self.patterns = {
            "email": {
                "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "mask": self._mask_email
            },
            "phone": {
                "regex": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                "mask": self._mask_phone
            },
            "ssn": {
                "regex": r'\b\d{3}-\d{2}-\d{4}\b',
                "mask": self._mask_ssn
            },
            "credit_card": {
                "regex": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                "mask": self._mask_credit_card
            },
            "ip_address": {
                "regex": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                "mask": self._mask_ip
            },
            "date_of_birth": {
                "regex": r'\b\d{2}/\d{2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b',
                "mask": self._mask_dob
            }
        }
    
    def mask_data(
        self, data: Any, data_type: str, tenant_id: str
    ) -> Any:
        """
        Mask sensitive data based on type
        
        Args:
            data: Data to mask
            data_type: Type of data (email, phone, ssn, etc.)
            tenant_id: Tenant ID for custom masking rules
            
        Returns:
            Masked data
        """
        if data is None:
            return None
        
        # Get custom masking rule if exists
        custom_rule = self.db.query(DataMaskingRule).filter(
            DataMaskingRule.tenant_id == tenant_id,
            DataMaskingRule.data_type == data_type,
            DataMaskingRule.is_active == True
        ).first()
        
        if custom_rule:
            return self._apply_custom_mask(data, custom_rule)
        
        # Use predefined masking
        if data_type in self.patterns:
            mask_func = self.patterns[data_type]["mask"]
            return mask_func(str(data))
        
        # Default masking
        return self._mask_default(str(data))
    
    def auto_detect_and_mask(
        self, data: Dict[str, Any], tenant_id: str
    ) -> Dict[str, Any]:
        """
        Automatically detect sensitive data and mask it
        
        Args:
            data: Dictionary of data
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with masked sensitive fields
        """
        masked_data = data.copy()
        
        for key, value in data.items():
            if value is None:
                continue
            
            value_str = str(value)
            
            # Check each pattern
            for data_type, pattern_info in self.patterns.items():
                regex = pattern_info["regex"]
                if re.search(regex, value_str):
                    masked_data[key] = self.mask_data(
                        value, data_type, tenant_id
                    )
                    break
        
        return masked_data
    
    def mask_query_results(
        self,
        results: List[Dict[str, Any]],
        datasource_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Mask query results based on data classifications
        
        Args:
            results: Query results
            datasource_id: Data source ID
            tenant_id: Tenant ID
            
        Returns:
            Masked results
        """
        if not results:
            return results
        
        # Get data classifications for this datasource
        classifications = self.db.query(DataClassification).filter(
            DataClassification.datasource_id == datasource_id,
            DataClassification.tenant_id == tenant_id
        ).all()
        
        if not classifications:
            return results
        
        # Build column -> classification mapping
        column_classifications = {}
        for classification in classifications:
            key = f"{classification.table_name}.{classification.column_name}"
            column_classifications[key] = classification
        
        # Mask results
        masked_results = []
        for row in results:
            masked_row = {}
            for column, value in row.items():
                # Check if this column is classified
                classification = column_classifications.get(column)
                
                if classification and classification.masking_rule_id:
                    # Get masking rule
                    masking_rule = self.db.query(DataMaskingRule).filter(
                        DataMaskingRule.id == classification.masking_rule_id
                    ).first()
                    
                    if masking_rule:
                        masked_row[column] = self._apply_custom_mask(
                            value, masking_rule
                        )
                    else:
                        masked_row[column] = value
                else:
                    masked_row[column] = value
            
            masked_results.append(masked_row)
        
        return masked_results
    
    # Predefined masking functions
    
    def _mask_email(self, email: str) -> str:
        """Mask email address"""
        if '@' not in email:
            return email
        
        parts = email.split('@')
        username = parts[0]
        domain = parts[1]
        
        if len(username) <= 2:
            masked_username = '*' * len(username)
        else:
            masked_username = username[0] + ('*' * (len(username) - 2)) + username[-1]
        
        return f"{masked_username}@{domain}"
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) >= 10:
            return f"(***) ***-{digits[-4:]}"
        elif len(digits) >= 4:
            return f"***-{digits[-4:]}"
        else:
            return '***'
    
    def _mask_ssn(self, ssn: str) -> str:
        """Mask Social Security Number"""
        digits = re.sub(r'\D', '', ssn)
        
        if len(digits) >= 4:
            return f"***-**-{digits[-4:]}"
        else:
            return '***-**-****'
    
    def _mask_credit_card(self, card: str) -> str:
        """Mask credit card number"""
        digits = re.sub(r'\D', '', card)
        
        if len(digits) >= 4:
            return f"****-****-****-{digits[-4:]}"
        else:
            return '****-****-****-****'
    
    def _mask_ip(self, ip: str) -> str:
        """Mask IP address"""
        parts = ip.split('.')
        if len(parts) == 4:
            return f"***.***.***.{parts[3]}"
        return '***.***.***'
    
    def _mask_dob(self, dob: str) -> str:
        """Mask date of birth"""
        # Keep only year
        if '-' in dob:
            parts = dob.split('-')
            return f"****-**-{parts[2] if len(parts) == 3 else '**'}"
        elif '/' in dob:
            parts = dob.split('/')
            return f"**/**/{parts[2] if len(parts) == 3 else '****'}"
        return '**/**/**'
    
    def _mask_default(self, data: str) -> str:
        """Default masking for unknown data types"""
        if len(data) <= 4:
            return '*' * len(data)
        else:
            return data[0] + ('*' * (len(data) - 2)) + data[-1]
    
    def _apply_custom_mask(
        self, data: Any, masking_rule: DataMaskingRule
    ) -> str:
        """Apply custom masking rule"""
        if data is None:
            return None
        
        data_str = str(data)
        pattern = masking_rule.masking_pattern
        
        # Pattern can include:
        # * - mask character
        # {n} - show first n characters
        # {-n} - show last n characters
        # Example: "{1}***{-4}" means show first 1 char, mask middle, show last 4
        
        # Simple pattern: just * characters
        if pattern.count('*') == len(pattern):
            return pattern
        
        # Complex pattern with placeholders
        if '{' in pattern:
            result = pattern
            
            # Replace {n} with first n characters
            import re
            first_match = re.search(r'\{(\d+)\}', result)
            if first_match:
                n = int(first_match.group(1))
                result = result.replace(
                    first_match.group(0),
                    data_str[:n] if len(data_str) >= n else data_str
                )
            
            # Replace {-n} with last n characters
            last_match = re.search(r'\{-(\d+)\}', result)
            if last_match:
                n = int(last_match.group(1))
                result = result.replace(
                    last_match.group(0),
                    data_str[-n:] if len(data_str) >= n else data_str
                )
            
            return result
        
        return pattern
    
    def create_masking_rule(
        self,
        tenant_id: str,
        name: str,
        data_type: str,
        masking_pattern: str,
        detection_regex: Optional[str] = None,
        description: Optional[str] = None
    ) -> DataMaskingRule:
        """Create a new masking rule"""
        import uuid
        
        rule = DataMaskingRule(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            data_type=data_type,
            masking_pattern=masking_pattern,
            detection_regex=detection_regex,
            description=description,
            is_active=True
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def get_masking_rules(self, tenant_id: str) -> List[DataMaskingRule]:
        """Get all masking rules for tenant"""
        return self.db.query(DataMaskingRule).filter(
            DataMaskingRule.tenant_id == tenant_id,
            DataMaskingRule.is_active == True
        ).all()
    
    def detect_sensitive_data(
        self, data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Detect sensitive data in a dictionary
        
        Returns:
            Dictionary mapping data types to detected fields
        """
        detected = {}
        
        for key, value in data.items():
            if value is None:
                continue
            
            value_str = str(value)
            
            for data_type, pattern_info in self.patterns.items():
                regex = pattern_info["regex"]
                if re.search(regex, value_str):
                    if data_type not in detected:
                        detected[data_type] = []
                    detected[data_type].append(key)
        
        return detected
