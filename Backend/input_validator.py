#!/usr/bin/env python3
"""
Comprehensive Input Validation and Sanitization System for HOLI Timecards Backend
Provides standardized validation for all user inputs and data sanitization.
"""

import re
import html
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from error_handler import ValidationError

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
    PHONE_PATTERN = re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$')
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input by removing HTML and limiting length"""
        if not isinstance(value, str):
            raise ValidationError(f"Expected string, got {type(value).__name__}")
        
        # Remove HTML tags and decode HTML entities
        sanitized = html.escape(value.strip())
        
        # Limit length
        if len(sanitized) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")
        
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate and sanitize email address"""
        if not email:
            raise ValidationError("Email is required")
        
        email = email.strip().lower()
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")
        
        return email
    
    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format"""
        if not username:
            raise ValidationError("Username is required")
        
        username = username.strip()
        
        if not InputValidator.USERNAME_PATTERN.match(username):
            raise ValidationError("Username must be 3-30 characters, alphanumeric and underscores only")
        
        return username
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password:
            raise ValidationError("Password is required")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number")
        
        return password
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate and format phone number"""
        if not phone:
            return ""  # Phone is optional
        
        phone = re.sub(r'[^\d+]', '', phone)  # Remove all non-digit characters except +
        
        if not InputValidator.PHONE_PATTERN.match(phone):
            raise ValidationError("Invalid phone number format")
        
        return phone
    
    @staticmethod
    def validate_integer(value: Any, min_val: int = None, max_val: int = None) -> int:
        """Validate integer input with optional range"""
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer: {value}")
        
        if min_val is not None and int_val < min_val:
            raise ValidationError(f"Value must be at least {min_val}")
        
        if max_val is not None and int_val > max_val:
            raise ValidationError(f"Value must be at most {max_val}")
        
        return int_val
    
    @staticmethod
    def validate_float(value: Any, min_val: float = None, max_val: float = None) -> float:
        """Validate float input with optional range"""
        try:
            float_val = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid number: {value}")
        
        if min_val is not None and float_val < min_val:
            raise ValidationError(f"Value must be at least {min_val}")
        
        if max_val is not None and float_val > max_val:
            raise ValidationError(f"Value must be at most {max_val}")
        
        return float_val
    
    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """Validate boolean input"""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
        
        if isinstance(value, int):
            return bool(value)
        
        raise ValidationError(f"Invalid boolean value: {value}")
    
    @staticmethod
    def validate_date(value: Any) -> date:
        """Validate date input"""
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
                raise ValueError("No matching date format")
            except ValueError:
                raise ValidationError(f"Invalid date format: {value}")
        
        raise ValidationError(f"Invalid date: {value}")
    
    @staticmethod
    def validate_datetime(value: Any) -> datetime:
        """Validate datetime input"""
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common datetime formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M']:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    raise ValueError("No matching datetime format")
                except ValueError:
                    raise ValidationError(f"Invalid datetime format: {value}")
        
        raise ValidationError(f"Invalid datetime: {value}")
    
    @staticmethod
    def validate_json(value: Any) -> Dict:
        """Validate JSON input"""
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON format")
        
        raise ValidationError(f"Invalid JSON: {value}")
    
    @staticmethod
    def validate_list(value: Any, item_validator=None) -> List:
        """Validate list input with optional item validation"""
        if not isinstance(value, list):
            raise ValidationError(f"Expected list, got {type(value).__name__}")
        
        if item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_items.append(item_validator(item))
                except ValidationError as e:
                    raise ValidationError(f"Invalid item at index {i}: {e}")
            return validated_items
        
        return value
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        if empty_fields:
            raise ValidationError(f"Empty required fields: {', '.join(empty_fields)}")

class ShiftValidator:
    """Specialized validation for shift-related data"""
    
    @staticmethod
    def validate_shift_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shift creation/update data"""
        validator = InputValidator()
        
        # Required fields
        validator.validate_required_fields(data, ['job_id', 'start_time', 'end_time'])
        
        # Validate individual fields
        validated_data = {
            'job_id': validator.validate_integer(data['job_id'], min_val=1),
            'start_time': validator.validate_datetime(data['start_time']),
            'end_time': validator.validate_datetime(data['end_time']),
        }
        
        # Validate time logic
        if validated_data['end_time'] <= validated_data['start_time']:
            raise ValidationError("End time must be after start time")
        
        # Optional fields
        if 'description' in data:
            validated_data['description'] = validator.sanitize_string(data['description'], 500)
        
        if 'required_workers' in data:
            validated_data['required_workers'] = validator.validate_integer(data['required_workers'], min_val=1, max_val=100)
        
        if 'hourly_rate' in data:
            validated_data['hourly_rate'] = validator.validate_float(data['hourly_rate'], min_val=0, max_val=1000)
        
        return validated_data

class UserValidator:
    """Specialized validation for user-related data"""
    
    @staticmethod
    def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user registration data"""
        validator = InputValidator()
        
        # Required fields
        validator.validate_required_fields(data, ['username', 'email', 'name'])
        
        # Validate individual fields
        validated_data = {
            'username': validator.validate_username(data['username']),
            'email': validator.validate_email(data['email']),
            'name': validator.sanitize_string(data['name'], 100),
        }
        
        # Optional password validation (for non-Google signups)
        if 'password' in data:
            validated_data['password'] = validator.validate_password(data['password'])
        
        # Optional fields
        if 'phone' in data:
            validated_data['phone'] = validator.validate_phone(data['phone'])
        
        if 'is_manager' in data:
            validated_data['is_manager'] = validator.validate_boolean(data['is_manager'])
        
        return validated_data

# Export commonly used validators
__all__ = [
    'InputValidator',
    'ShiftValidator', 
    'UserValidator',
    'ValidationError'
]
