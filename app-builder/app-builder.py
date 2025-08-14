import google.generativeai as genai
import json
import jsonschema
from dotenv import load_dotenv
import os
import time
from typing import Dict, Tuple, Optional, Any

# Configure Gemini
load_dotenv()  # Load environment variables from .env file if needed
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# WizyVision canonical field types (x-wv-type) and contracts
WV_ALLOWED_TYPES = [
    "Toggle",
    "Checkbox",
    "Date",
    "Number",
    "Location",
    "Dropdown",
    "Text",
    "Paragraph",
    "People",
    "People List",
    "Signature Field"
]

# Human-readable descriptions for help output
WV_TYPE_DESCRIPTIONS = {
    "Toggle": "A boolean switch (yes/no)",
    "Checkbox": "Multi-select from a list of defined values (array of enum strings)",
    "Date": "Date or date-time string",
    "Number": "Numeric value",
    "Location": "Geolocation object with latitude/longitude",
    "Dropdown": "Single selection from a list of defined values (enum string)",
    "Text": "Single-line text",
    "Paragraph": "Multi-line text",
    "People": "Single user selection (userId string)",
    "People List": "Multiple user selection (array of userId strings)",
    "Signature Field": "Signature data (string). If unsupported, treat as optional"
}

# Structural contracts per x-wv-type for validator enforcement
TYPE_CONTRACTS = {
    "Toggle": {"type": "boolean"},
    "Checkbox": {"type": "array", "items": {"type": "string"}},
    "Date": {"type": "string", "format_in": ["date", "date-time"]},
    "Number": {"type_in": ["number", "integer"]},
    "Location": {
        "type": "object",
        "required": ["latitude", "longitude"],
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "label": {"type": "string"}
        }
    },
    "Dropdown": {"type": "string", "requires_enum": True},
    "Text": {"type": "string"},
    "Paragraph": {"type": "string"},
    "People": {"type": "string"},
    "People List": {"type": "array", "items": {"type": "string"}},
    "Signature Field": {"type": "string"}
}

# Predefined field structures from prototype.py for reference and templates
PREDEFINED_FIELDS = {
    "postRef": {
        "type": "string",
        "x-wv-type": "Text",
        "description": "Case ID (unique identifier)",
        "minLength": 1
    },
    "typeId": {
        "type": "string", 
        "x-wv-type": "Text",
        "description": "Application ID"
    },
    "statusId": {
        "type": "string",
        "enum": ["open", "closed"],
        "default": "open",
        "x-wv-type": "Dropdown",
        "description": "Status of the record"
    },
    "privacyId": {
        "type": "string",
        "enum": ["public", "private", "restricted"],
        "x-wv-type": "Dropdown",
        "description": "Privacy level"
    },
    "description": {
        "type": "string",
        "x-wv-type": "Paragraph",
        "description": "Detailed description",
        "minLength": 1
    },
    "tags": {
        "type": "array",
        "items": {"type": "string"},
        "x-wv-type": "Checkbox",
        "description": "Tags for categorization"
    },
    "assignedTo": {
        "type": "string",
        "x-wv-type": "People",
        "description": "Assigned user"
    },
    "memId": {
        "type": "string",
        "x-wv-type": "People",
        "description": "Created by user (auto-populated)"
    },
    "createdAt": {
        "type": "string",
        "format": "date-time",
        "x-wv-type": "Date",
        "description": "Creation timestamp (auto-populated)"
    },
    "updatedAt": {
        "type": "string",
        "format": "date-time",
        "x-wv-type": "Date",
        "description": "Last update timestamp (auto-updated)"
    }
}

def create_system_prompt(include_examples: bool = True) -> str:
    """Create the system prompt for schema generation using Chain-of-Thought"""
    base_prompt = """You are a JSON schema generator for WizyVision applications. You will use Chain-of-Thought reasoning to create valid JSON schemas.

## Allowed x-wv-type values (choose one per field):
- Toggle: boolean
- Checkbox: array of strings (multi-select)
- Date: string with format "date" or "date-time"
- Number: number or integer
- Location: object with latitude:number, longitude:number, optional label:string
- Dropdown: string enum (must include enum array)
- Text: string (single-line)
- Paragraph: string (multi-line)
- People: string (userId)
- People List: array of strings (userIds)
- Signature Field: string (signature payload or ref)

## Predefined Field Templates (recommended for common use cases):
- postRef: Text field for unique case ID
- typeId: Text field for application ID
- statusId: Dropdown with ["open", "closed"] options
- privacyId: Dropdown with ["public", "private", "restricted"] options
- description: Paragraph field for detailed descriptions
- tags: Checkbox array for categorization
- assignedTo: People field for assignment
- memId: People field for creator (auto-populated)
- createdAt: Date field for creation timestamp (auto-populated)
- updatedAt: Date field for last update (auto-updated)

## Chain-of-Thought Process:

Follow these steps in order:

### Step 1: Analyze the Use Case
- Identify the core purpose and domain of the application
- Determine what type of data needs to be tracked
- Consider the business workflow and user interactions

### Step 2: Identify Required Fields
- Determine which fields are essential for the core functionality
- Consider what information must be captured for each record
- Think about unique identifiers and primary keys

### Step 3: Select Appropriate Field Types
- Match each data requirement to an appropriate x-wv-type from the list above
- Consider field relationships and dependencies
- Ensure only supported field types are used

### Step 4: Define Validation Rules
- Set appropriate constraints (minLength, maxLength, etc.)
- Define required vs optional fields based on business logic
- Add meaningful descriptions for each field

### Step 5: Consider Workflow Requirements
- Determine if status tracking is needed (statusId with open/closed options)
- Consider assignment and ownership (assignedTo, memId)
- Think about audit trail requirements (createdAt, updatedAt)
- Include privacy controls if needed (privacyId)
- Add categorization with tags if appropriate

### Step 6: Finalize Schema Structure
- Ensure JSON Schema Draft 7 compliance
- Include $schema and type properties
- Set appropriate required fields array

Additionally:
- For every property, include an "x-wv-type" key with one of the allowed values above
- Ensure the JSON Schema structure matches the chosen x-wv-type contract (e.g., Dropdown requires enum; Location requires latitude/longitude)

## Instructions:
1. Think through each step above before generating the schema
2. Use only the x-wv-type values listed above
3. Consider using predefined field templates for common requirements (postRef, statusId, description, etc.)
4. Include appropriate validation rules and constraints
5. Add clear descriptions for each field
6. Set required fields based on the use case analysis
7. Include default values where applicable
8. Always include $schema and type properties
9. Return ONLY valid JSON, no explanations or markdown formatting

User Request: {USER_PROMPT}

Now, follow the Chain-of-Thought process above and generate the schema."""
    
    if include_examples:
        examples = """

## Example Chain-of-Thought Process:

**Input:** "Create a schema for incident reports with severity levels"

**Step 1 Analysis:** This is for incident management in IT/operations. Need to track security, system, or process incidents.

**Step 2 Required Fields:** Need unique incident ID (postRef), detailed description, severity level, status tracking, assignment.

**Step 3 Field Selection:** priority as Dropdown, details as Paragraph, isResolved as Toggle, assignee as People, watchers as People List

**Step 4 Validation:** Description should have minimum length, statusId should default to "open".

**Step 5 Workflow:** Need status tracking, assignment capability, audit trail.

**Step 6 Schema:**
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "priority": {"type": "string", "enum": ["Low", "Medium", "High"], "x-wv-type": "Dropdown"},
    "details": {"type": "string", "minLength": 5, "x-wv-type": "Paragraph"},
    "isResolved": {"type": "boolean", "default": false, "x-wv-type": "Toggle"},
    "assignee": {"type": "string", "x-wv-type": "People"},
    "watchers": {"type": "array", "items": {"type": "string"}, "x-wv-type": "People List"},
    "scheduledAt": {"type": "string", "format": "date-time", "x-wv-type": "Date"}
  },
  "required": ["priority", "details"]
}"""
        base_prompt += examples
    
    return base_prompt

def generate_schema(user_prompt: str, max_retries: int = 3) -> Tuple[Optional[Dict], str]:
    """
    Generate a JSON schema based on user prompt with retry logic
    
    Returns:
        Tuple of (schema_dict, status_message)
    """
    system_prompt = create_system_prompt()
    full_prompt = system_prompt.replace("{USER_PROMPT}", user_prompt)
    
    for attempt in range(max_retries):
        try:
            print(f"Generating schema (attempt {attempt + 1}/{max_retries})...")
            
            response = model.generate_content(full_prompt)
            
            if not response.text:
                return None, "Empty response from Gemini API"
            
            # Clean the response text - remove markdown formatting if present
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            schema = json.loads(cleaned_text)
            
            # Validate the schema
            is_valid, validation_message = validate_generated_schema(schema)
            
            if is_valid:
                return schema, f"Schema generated successfully on attempt {attempt + 1}"
            else:
                print(f"Validation failed: {validation_message}")
                if attempt < max_retries - 1:
                    print("Retrying with enhanced Chain-of-Thought prompt...")
                    # Try with a more explicit Chain-of-Thought prompt
                    enhanced_prompt = full_prompt + """

IMPORTANT: Please follow the Chain-of-Thought process more carefully:

1. First, think about what this use case really needs
2. Then, identify the essential fields step by step
3. Finally, create the schema with proper validation

Remember: Only use the specified WizyVision field types and ensure JSON Schema Draft 7 compliance."""
                    response = model.generate_content(enhanced_prompt)
                    cleaned_text = response.text.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]
                    cleaned_text = cleaned_text.strip()
                    schema = json.loads(cleaned_text)
                    is_valid, validation_message = validate_generated_schema(schema)
                    if is_valid:
                        return schema, f"Schema generated successfully on retry {attempt + 1}"
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON generated on attempt {attempt + 1}: {str(e)}"
            print(error_msg)
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(1)  # Brief delay before retry
            else:
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Error on attempt {attempt + 1}: {str(e)}"
            print(error_msg)
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(1)
            else:
                return None, error_msg
    
    return None, f"Failed to generate valid schema after {max_retries} attempts"

def validate_generated_schema(schema: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that the generated schema is valid JSON Schema and that each property
    declares a valid WizyVision x-wv-type and adheres to its structural contract.
    
    Returns:
        Tuple of (is_valid, validation_message)
    """
    try:
        # JSON Schema Draft 7 compliance of the overall document
        jsonschema.Draft7Validator.check_schema(schema)

        # Required top-level properties
        if schema.get("type") != "object":
            return False, "Schema 'type' must be 'object'"
        if "$schema" not in schema:
            return False, "Schema must include '$schema' property"

        properties: Dict[str, Any] = schema.get("properties", {})
        if not isinstance(properties, dict) or not properties:
            return False, "Schema must define non-empty 'properties' object"

        errors: list[str] = []

        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_schema, dict):
                errors.append(f"Property '{prop_name}' must be an object schema")
                continue

            x_type = prop_schema.get("x-wv-type")
            if x_type is None:
                errors.append(f"Property '{prop_name}' must include 'x-wv-type'")
                continue
            if x_type not in WV_ALLOWED_TYPES:
                errors.append(f"Property '{prop_name}' has invalid x-wv-type '{x_type}'")
                continue

            contract = TYPE_CONTRACTS.get(x_type, {})
            declared_type = prop_schema.get("type")

            # Type equality or membership checks
            if "type" in contract and declared_type != contract["type"]:
                errors.append(f"'{prop_name}' with x-wv-type '{x_type}' must have type '{contract['type']}'")
            if "type_in" in contract and declared_type not in contract["type_in"]:
                allowed = ", ".join(contract["type_in"])  # type: ignore[index]
                errors.append(f"'{prop_name}' with x-wv-type '{x_type}' type must be one of [{allowed}]")

            # Format constraints (e.g., Date)
            if "format_in" in contract:
                fmt = prop_schema.get("format")
                if fmt not in contract["format_in"]:
                    allowed = ", ".join(contract["format_in"])  # type: ignore[index]
                    errors.append(f"'{prop_name}' must specify format in [{allowed}]")

            # Enum requirement (e.g., Dropdown)
            if contract.get("requires_enum") is True and not isinstance(prop_schema.get("enum"), list):
                errors.append(f"'{prop_name}' with x-wv-type '{x_type}' must define an 'enum' array")

            # Array items checks (Checkbox / People List)
            if contract.get("type") == "array" or x_type in ("Checkbox", "People List"):
                items = prop_schema.get("items")
                if not isinstance(items, dict) or items.get("type") != "string":
                    errors.append(f"Array property '{prop_name}' must have items of type 'string'")

            # Location structural checks
            if x_type == "Location":
                if prop_schema.get("type") != "object":
                    errors.append(f"'${prop_name}' must be an object")
                req = prop_schema.get("required", [])
                if not all(k in req for k in ["latitude", "longitude"]):
                    errors.append(f"'{prop_name}' must require latitude and longitude")
                props = prop_schema.get("properties", {})
                if not isinstance(props, dict) or props.get("latitude", {}).get("type") != "number" or props.get("longitude", {}).get("type") != "number":
                    errors.append(f"'{prop_name}' must define numeric latitude/longitude properties")

        if errors:
            return False, "; ".join(errors)

        return True, "Schema is valid for WizyVision types"

    except jsonschema.exceptions.SchemaError as e:
        return False, f"JSON Schema validation failed: {str(e)}"
    except Exception as e:
        return False, f"Schema validation failed: {str(e)}"

def format_schema_output(schema: Dict[str, Any]) -> str:
    """Format the schema for nice output"""
    return json.dumps(schema, indent=2)

def create_example_schema() -> Dict[str, Any]:
    """Create an example schema for demonstration"""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "priority": {"type": "string", "enum": ["Low", "Medium", "High"], "x-wv-type": "Dropdown"},
            "details": {"type": "string", "minLength": 10, "x-wv-type": "Paragraph"},
            "isResolved": {"type": "boolean", "default": False, "x-wv-type": "Toggle"},
            "assignee": {"type": "string", "x-wv-type": "People"},
            "watchers": {"type": "array", "items": {"type": "string"}, "x-wv-type": "People List"},
            "scheduledAt": {"type": "string", "format": "date-time", "x-wv-type": "Date"},
            "site": {
                "type": "object",
                "required": ["latitude", "longitude"],
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "label": {"type": "string"}
                },
                "x-wv-type": "Location"
            }
        },
        "required": ["priority", "details"]
    }

def create_predefined_schema() -> Dict[str, Any]:
    """Create a schema using predefined field structures"""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": PREDEFINED_FIELDS,
        "required": ["postRef", "typeId", "statusId", "description"]
    }

def create_custom_predefined_schema(selected_fields: list) -> Dict[str, Any]:
    """Create a schema using selected predefined fields plus custom fields"""
    properties = {}
    required = []
    
    # Add selected predefined fields
    for field_name in selected_fields:
        if field_name in PREDEFINED_FIELDS:
            properties[field_name] = PREDEFINED_FIELDS[field_name]
            if field_name in ["postRef", "typeId", "statusId", "description"]:
                required.append(field_name)
    
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
        "required": required
    }

def main():
    """Main application loop"""
    print("=== WizyVision Schema Generator (Gemini 2.5 Flash) ===")
    print("This tool generates JSON schemas for WizyVision applications.")
    print("Commands: 'exit', 'example', 'predefined', 'templates', 'help'")
    print()
    while True:
        try:
            user_input = input("Enter your request for a WizyVision schema: ").strip()

            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'example':
                example_schema = create_example_schema()
                print("\n=== Example Schema ===")
                print(format_schema_output(example_schema))
                print()
                continue
            elif user_input.lower() == 'help':
                print("\n=== Allowed x-wv-type values ===")
                for t, desc in WV_TYPE_DESCRIPTIONS.items():
                    print(f"• {t}: {desc}")
                print()
                continue
            elif user_input.lower() == 'predefined':
                predefined_schema = create_predefined_schema()
                print("\n=== Predefined Schema (All Fields) ===")
                print(format_schema_output(predefined_schema))
                print()
                continue
            elif user_input.lower() == 'templates':
                print("\n=== Predefined Field Templates ===")
                for field_name, field_schema in PREDEFINED_FIELDS.items():
                    desc = field_schema.get('description', 'No description')
                    wv_type = field_schema.get('x-wv-type', 'Unknown')
                    print(f"• {field_name}: {wv_type} - {desc}")
                print()
                continue
            elif not user_input:
                print("Please enter a valid request.")
                continue

            print(f"\nGenerating schema for: '{user_input}'")
            print("-" * 50)

            schema, status_message = generate_schema(user_input)

            if schema:
                print("✅ " + status_message)
                print("\n=== Generated Schema ===")
                print(format_schema_output(schema))
            else:
                print("❌ " + status_message)
                print("\nSuggestion: Try rephrasing your request or be more specific about the fields you need.")

            print("-" * 50)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()
