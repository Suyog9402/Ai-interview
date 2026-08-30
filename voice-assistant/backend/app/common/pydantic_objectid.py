from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue

class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId that works with Pydantic v2.
    
    This class handles:
    - Validation of ObjectId strings
    - JSON schema generation
    - Serialization to string for JSON responses
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type, _handler
    ) -> core_schema.CoreSchema:
        """Define how to validate and parse the ObjectId."""
        def validate(value: str | ObjectId) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str) and ObjectId.is_valid(value):
                return ObjectId(value)
            raise ValueError("Invalid ObjectId")

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x), when_used="json"
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Define the JSON schema for OpenAPI documentation."""
        return {
            "type": "string",
            "pattern": "^[a-fA-F0-9]{24}$",
            "title": "ObjectId",
            "description": "MongoDB ObjectId",
        }
