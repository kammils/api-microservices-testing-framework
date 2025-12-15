"""
JSON Schema Validator Module

Provides JSON schema validation for API responses using jsonschema library.
"""

from typing import Any, Dict, List, Optional
import jsonschema
from jsonschema import Draft7Validator, ValidationError

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SchemaValidator:
    """
    JSON Schema validator for API responses.
    
    Uses jsonschema library to validate response data against predefined schemas.
    """
    
    def __init__(self):
        """Initialize the schema validator."""
        self.validator_class = Draft7Validator
    
    def validate(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        raise_on_error: bool = True
    ) -> bool:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema definition
            raise_on_error: Whether to raise exception on validation error
            
        Returns:
            True if validation passes, False otherwise
            
        Raises:
            ValidationError: If validation fails and raise_on_error is True
        """
        try:
            validator = self.validator_class(schema)
            validator.validate(data)
            logger.debug("Schema validation passed")
            return True
        except ValidationError as e:
            logger.error(
                "Schema validation failed",
                context={
                    "error": str(e.message),
                    "path": ".".join(str(p) for p in e.path) if e.path else "root"
                }
            )
            if raise_on_error:
                raise
            return False
    
    def validate_list(
        self,
        data_list: List[Dict[str, Any]],
        schema: Dict[str, Any],
        raise_on_error: bool = True
    ) -> bool:
        """
        Validate list of items against JSON schema.
        
        Args:
            data_list: List of data items to validate
            schema: JSON schema definition
            raise_on_error: Whether to raise exception on validation error
            
        Returns:
            True if all items pass validation, False otherwise
            
        Raises:
            ValidationError: If validation fails and raise_on_error is True
        """
        for idx, item in enumerate(data_list):
            try:
                self.validate(item, schema, raise_on_error=True)
            except ValidationError as e:
                logger.error(
                    f"Schema validation failed for item {idx}",
                    context={"index": idx, "error": str(e.message)}
                )
                if raise_on_error:
                    raise
                return False
        
        logger.debug(f"Schema validation passed for {len(data_list)} items")
        return True
    
    @staticmethod
    def create_object_schema(
        properties: Dict[str, Dict[str, Any]],
        required: Optional[List[str]] = None,
        additional_properties: bool = True
    ) -> Dict[str, Any]:
        """
        Create a JSON schema for an object.
        
        Args:
            properties: Dictionary of property definitions
            required: List of required property names
            additional_properties: Whether to allow additional properties
            
        Returns:
            JSON schema definition
            
        Example:
            schema = SchemaValidator.create_object_schema(
                properties={
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                required=["id", "name"]
            )
        """
        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": additional_properties
        }
        
        if required:
            schema["required"] = required
        
        return schema
    
    @staticmethod
    def create_array_schema(
        items_schema: Dict[str, Any],
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: bool = False
    ) -> Dict[str, Any]:
        """
        Create a JSON schema for an array.
        
        Args:
            items_schema: Schema for array items
            min_items: Minimum number of items
            max_items: Maximum number of items
            unique_items: Whether items must be unique
            
        Returns:
            JSON schema definition
            
        Example:
            schema = SchemaValidator.create_array_schema(
                items_schema={"type": "object", "properties": {"id": {"type": "integer"}}},
                min_items=1
            )
        """
        schema = {
            "type": "array",
            "items": items_schema
        }
        
        if min_items is not None:
            schema["minItems"] = min_items
        
        if max_items is not None:
            schema["maxItems"] = max_items
        
        if unique_items:
            schema["uniqueItems"] = True
        
        return schema


# Common schema definitions
COMMON_SCHEMAS = {
    "user": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "username": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "phone": {"type": "string"},
            "website": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    },
    "post": {
        "type": "object",
        "properties": {
            "userId": {"type": "integer"},
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "body": {"type": "string"}
        },
        "required": ["userId", "id", "title", "body"]
    },
    "comment": {
        "type": "object",
        "properties": {
            "postId": {"type": "integer"},
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "body": {"type": "string"}
        },
        "required": ["postId", "id", "name", "email", "body"]
    },
    "todo": {
        "type": "object",
        "properties": {
            "userId": {"type": "integer"},
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "completed": {"type": "boolean"}
        },
        "required": ["userId", "id", "title", "completed"]
    }
}


# Global validator instance
validator = SchemaValidator()
