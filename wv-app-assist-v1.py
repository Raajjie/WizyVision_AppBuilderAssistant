import google.generativeai as genai
import json

# Configure Gemini
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')

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
        schema = json.loads(response.text)
        return schema
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON generated: {str(e)}"}