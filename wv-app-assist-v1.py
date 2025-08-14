import google.generativeai as genai
import json
import jsonschema
from jsonschema import validate, Draft7Validator
from dotenv import load_dotenv
import os

# Configure Gemini
load_dotenv()  # Load environment variables from .env file if needed
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# Draft 7 Schema for validation
SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "postRef": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "string"},
                "key": {"type": "string", "const": "postRef"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position"],
            "additionalProperties": False
        },
        "typeId": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "enum": ["string", "integer"]},
                "key": {"type": "string", "const": "typeId"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position"],
            "additionalProperties": False
        },
        "statusId": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "enum"},
                "key": {"type": "string", "const": "statusId"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "options": {"type": "array", "items": {"type": "string", "enum": ["open", "closed"]}},
                "default": {"type": "string", "const": "open"}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "options", "default"],
            "additionalProperties": False
        },
        "privacyId": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "enum"},
                "key": {"type": "string", "const": "privacyId"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position"],
            "additionalProperties": False
        },
        "description": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "string"},
                "key": {"type": "string", "const": "description"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "multiline": {"type": "boolean", "const": True}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "multiline"],
            "additionalProperties": False
        },
        "tags": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "array"},
                "key": {"type": "string", "const": "tags"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "items": {"type": "object", "properties": {"type": {"type": "string", "const": "string"}}, "required": ["type"]}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "items"],
            "additionalProperties": False
        },
        "texts": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "array"},
                "key": {"type": "string", "const": "texts"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "items": {"type": "object", "properties": {"type": {"type": "string", "const": "string"}}, "required": ["type"]},
                "readOnly": {"type": "boolean", "const": True}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "items", "readOnly"],
            "additionalProperties": False
        },
        "files": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "array"},
                "key": {"type": "string", "const": "files"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "items": {"type": "object", "properties": {"type": {"type": "string", "const": "object"}}, "required": ["type"]}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "items"],
            "additionalProperties": False
        },
        "assignedTo": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "string"},
                "key": {"type": "string", "const": "assignedTo"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "references": {"type": "string", "const": "user"}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "references"],
            "additionalProperties": False
        },
        "memId": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "string"},
                "key": {"type": "string", "const": "memId"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "autoPopulated": {"type": "boolean", "const": True}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "autoPopulated"],
            "additionalProperties": False
        },
        "createdAt": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "string"},
                "key": {"type": "string", "const": "createdAt"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "format": {"type": "string", "const": "date-time"},
                "autoPopulated": {"type": "boolean", "const": True}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "format", "autoPopulated"],
            "additionalProperties": False
        },
        "updatedAt": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "kind": {"type": "string", "enum": ["System", "Standard", "Custom"]},
                "type": {"type": "string", "const": "string"},
                "key": {"type": "string", "const": "updatedAt"},
                "description": {"type": "string"},
                "viewableInList": {"type": "boolean"},
                "allowImageAttachment": {"type": "boolean"},
                "position": {"type": "integer", "minimum": 1},
                "format": {"type": "string", "const": "date-time"},
                "autoUpdated": {"type": "boolean", "const": True}
            },
            "required": ["label", "kind", "type", "key", "description", "viewableInList", "allowImageAttachment", "position", "format", "autoUpdated"],
            "additionalProperties": False
        }
    },
    "required": ["postRef", "typeId", "statusId", "privacyId", "description", "tags", "texts", "files", "assignedTo", "memId", "createdAt", "updatedAt"],
    "additionalProperties": False
}

def validate_generated_json(generated_json_str):
    """
    Validates the generated JSON against Draft 7 schema
    
    Args:
        generated_json_str (str): JSON string to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    try:
        # Parse JSON string
        generated_data = json.loads(generated_json_str)
        
        # Validate against schema
        validator = Draft7Validator(SCHEMA)
        errors = list(validator.iter_errors(generated_data))
        
        if not errors:
            return True, "✅ JSON is valid and conforms to schema"
        else:
            error_messages = []
            for error in errors:
                path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                error_messages.append(f"❌ Path '{path}': {error.message}")
            
            return False, f"JSON validation failed:\n" + "\n".join(error_messages)
            
    except json.JSONDecodeError as e:
        return False, f"❌ Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, f"❌ Validation error: {str(e)}"

def generate_json(user_prompt):
    system_prompt = """
Available Field Types:
1. postRef - Case ID (string, unique identifier)
2. typeId - Application ID (string/integer)  
3. statusId - Status dropdown (enum: "open", "closed", with "open" as default)
4. privacyId - Privacy dropdown (enum, role-dependent)
5. description - Description text (string, multiline)
6. tags - Multi-select tags (array of strings)
7. texts - OCR text from images (array of strings, read-only)
8. files - Attached files (array of objects with file metadata)
9. assignedTo - Assignee dropdown (string, references user ID)
10. memId - Created by (string, user ID, auto-populated)
11. createdAt - Created date (string, ISO datetime, auto-populated)
12. updatedAt - Last updated (string, ISO datetime, auto-updated)

Each field has these standard properties:
- label: Translatable display name
- kind: System/Standard/Custom category
- type: Field data type
- key: Technical API identifier
- description: Brief field description
- viewableInList: Boolean for list screen display
- allowImageAttachment: Boolean for image upload capability
- position: Ordinal position among fields

Instructions:
1. Create a JSON object with all 12 field objects listed above
2. Each field object must have all the standard properties
3. Add appropriate values for each field based on the user request
4. Use only the field types listed above
5. All fields must be included (postRef, typeId, statusId, privacyId, description, tags, texts, files, assignedTo, memId, createdAt, updatedAt)
6. Position values should be unique integers starting from 1

IMPORTANT: Respond with ONLY valid JSON. Do not include any explanatory text, markdown formatting, or code blocks. Start your response with { and end with }.

User Request: {USER_PROMPT}
"""
    
    full_prompt = system_prompt.replace("{USER_PROMPT}", user_prompt)
    
    response = model.generate_content(full_prompt)
    
    # Clean up response text (remove markdown if present)
    schema_text = response.text.strip()
    if schema_text.startswith("```json"):
        schema_text = schema_text[7:]
    if schema_text.startswith("```"):
        schema_text = schema_text[3:]
    if schema_text.endswith("```"):
        schema_text = schema_text[:-3]
    
    return schema_text.strip()


def main():
    print("🚀JSON Generator with Draft 7 Validation")
    print("=" * 55)
    
    while True:
        user_input = input("\nEnter your request for a schema (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        print("\n📝 Generating JSON...")
        generated_json = generate_json(user_input)
        
        print("\n🔍 Validating with draft 7 schema...")
        is_valid, validation_message = validate_generated_json(generated_json)
        
        print("\n" + "="*50)
        print("GENERATED JSON:")
        print("="*50)
        
        # Pretty print JSON if valid
        try:
            formatted_json = json.dumps(json.loads(generated_json), indent=2)
            print(formatted_json)
        except:
            print(generated_json)
        
        print("\n" + "="*50)
        print("VALIDATION RESULT:")
        print("="*50)
        print(validation_message)
        
        if not is_valid:
            print("\n💡 Tip: Try rephrasing your request or being more specific about field requirements.")

if __name__ == "__main__":
    main()