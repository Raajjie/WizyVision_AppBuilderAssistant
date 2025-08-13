import google.generativeai as genai
import json
import jsonschema
from dotenv import load_dotenv
import os

# Configure Gemini
load_dotenv()  # Load environment variables from .env file if needed
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_schema(user_prompt):
    system_prompt = """
You are a JSON schema generator for WizyVision applications. Based on user requirements, create a valid JSON schema using only the supported field types listed below.

## Available WizyVision Field Types:

1. **postRef** - Case ID (string, unique identifier)
2. **typeId** - Application ID (string/integer)
3. **statusId** - Status dropdown (enum: "open", "closed", with "open" as default)
4. **privacyId** - Privacy dropdown (enum, role-dependent)
5. **description** - Description text (string, multiline)
6. **tags** - Multi-select tags (array of strings)
7. **texts** - OCR text from images (array of strings, read-only)
8. **files** - Attached files (array of objects with file metadata)
9. **assignedTo** - Assignee dropdown (string, references user ID)
10. **memId** - Created by (string, user ID, auto-populated)
11. **createdAt** - Created date (string, ISO datetime, auto-populated)
12. **updatedAt** - Last updated (string, ISO datetime, auto-updated)

## Instructions:
1. Create a JSON Schema Draft 7 compliant schema
2. Use only the field types listed above
3. Include appropriate validation rules and constraints
4. Add clear descriptions for each field
5. Set required fields based on the use case
6. Include default values where applicable
7. Consider field relationships and dependencies

User Request: {USER_PROMPT}

Respond with only valid JSON schema.

"""
    
    full_prompt = system_prompt.replace("{USER_PROMPT}", user_prompt)
    
    response = model.generate_content(full_prompt)
    
    try:
        # Parse and validate JSON
        schema = response.text
        return schema
        
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON generated: {str(e)}"}
    

def validate_generated_schema(schema):
    """Validate that the generated schema is valid JSON Schema"""
    try:
        # Check if it's valid JSON Schema
        jsonschema.Draft7Validator.check_schema(schema)
        
        # Check if only WizyVision fields are used
        allowed_fields = {
            "postRef", "typeId", "statusId", "privacyId", 
            "description", "tags", "texts", "files", 
            "assignedTo", "memId", "createdAt", "updatedAt"
        }
        
        schema_fields = set(schema.get("properties", {}).keys())
        invalid_fields = schema_fields - allowed_fields
        
        if invalid_fields:
            return False, f"Invalid fields used: {invalid_fields}"
            
        return True, "Schema is valid"
        
    except Exception as e:
        return False, f"Schema validation failed: {str(e)}"
    

def create_enhanced_prompt(user_request, include_examples=True):
    base_prompt = """You are a JSON schema generator for WizyVision applications. Based on user requirements, create a valid JSON schema using only the supported field types listed below.

## Available WizyVision Field Types:

1. **postRef** - Case ID (string, unique identifier)
2. **typeId** - Application ID (string/integer)
3. **statusId** - Status dropdown (enum: "open", "closed", with "open" as default)
4. **privacyId** - Privacy dropdown (enum, role-dependent)
5. **description** - Description text (string, multiline)
6. **tags** - Multi-select tags (array of strings)
7. **texts** - OCR text from images (array of strings, read-only)
8. **files** - Attached files (array of objects with file metadata)
9. **assignedTo** - Assignee dropdown (string, references user ID)
10. **memId** - Created by (string, user ID, auto-populated)
11. **createdAt** - Created date (string, ISO datetime, auto-populated)
12. **updatedAt** - Last updated (string, ISO datetime, auto-updated)

## Instructions:
1. Create a JSON Schema Draft 7 compliant schema
2. Use only the field types listed above
3. Include appropriate validation rules and constraints
4. Add clear descriptions for each field
5. Set required fields based on the use case
6. Include default values where applicable
7. Consider field relationships and dependencies

User Request: {USER_PROMPT}

Respond with only valid JSON schema."""
    
    if include_examples:
        examples = """
## Examples:

**Input:** "Create a schema for incident reports with severity levels"
**Output:** 
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "postRef": {"type": "string", "description": "Incident ID"},
    "statusId": {"type": "string", "enum": ["open", "closed"], "default": "open"},
    "description": {"type": "string", "minLength": 5},
    "tags": {"type": "array", "items": {"type": "string"}},
    "assignedTo": {"type": "string"},
    "memId": {"type": "string", "readOnly": true},
    "createdAt": {"type": "string", "format": "date-time", "readOnly": true}
  },
  "required": ["postRef", "description", "memId", "createdAt"]
}
        """
        base_prompt += examples
    
    return base_prompt.replace("{USER_PROMPT}", user_request)

while True:
    user_input = input("Enter your request for a WizyVision schema (or 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break

    orig = generate_schema(user_input)
    is_valid, validation_message = validate_generated_schema(orig)
    print("Generated Schema:", orig)

    enhanced = create_enhanced_prompt(user_input)
    print("Enhanced Prompt:", enhanced)

    # print("Validation Result:", validation_message, "Validation result", validation_message)
