import google.generativeai as genai
import json
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

class AppJSONGenerator:
    def __init__(self, api_key: str):
        # Initialize the generator with the API key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def generate_app_structure(self, user_prompt: str) -> Dict[str, Any]:
        # Enhanced prompt for better JSON generation
        enhanced_prompt = f"""
        Based on the following user request for an app, generate a comprehensive JSON structure for app development.
        
        User Request: "{user_prompt}"
        
        Please generate a JSON structure that includes:
        1. App metadata (intl, name, position, color, category, privacy)
        2. Status (active, archived, deleted)
        3. Fields (default fields: postRef, typeId, statusId, privacyId, description, tags, text, files, assignedTo, memId,createdAt, updatedAt)

        
        Return ONLY valid JSON without any markdown formatting or code blocks.
        Make it practical and implementable for developers.
        """
        
        try:
            response = self.model.generate_content(enhanced_prompt)
            
            # Clean the response text
            json_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.startswith('```'):
                json_text = json_text[3:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            # Parse JSON
            app_structure = json.loads(json_text.strip())
            
            # Add metadata
            app_structure['generated_at'] = datetime.now().isoformat()
            app_structure['original_prompt'] = user_prompt
            
            return app_structure
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response.text}")
            
            # Fallback structure
            
            
        except Exception as e:
            print(f"Error generating content: {e}")
            """Create a basic fallback structure if API call fails"""
        return e
    
    def save_to_file(self, app_structure: Dict[str, Any], filename: str = None) -> str:
        """
        Save the generated JSON to a file
        
        Args:
            app_structure (Dict[str, Any]): The app structure to save
            filename (str, optional): Custom filename. If None, auto-generates based on timestamp
            
        Returns:
            str: Path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"app_structure_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(app_structure, f, indent=2, ensure_ascii=False)
        
        return filename

def main():
    """Main function to run the application"""
    print("=== App Development JSON Generator ===")
    print("Using Google Gemini API\n")
    
    # Get API key from environment variable or user input
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        api_key = input("Enter your Google AI API key: ").strip()
        if not api_key:
            print("API key is required to continue.")
            return
    
    # Initialize the generator
    try:
        generator = AppJSONGenerator(api_key)
        print("✅ Successfully connected to Gemini API\n")
    except Exception as e:
        print(f"❌ Error initializing API: {e}")
        return
    
    while True:
        print("\n" + "="*50)
        user_prompt = input("Describe the app you want to build (or 'quit' to exit): ").strip()
        
        if user_prompt.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
        
        if not user_prompt:
            print("Please provide a valid app description.")
            continue
        
        print("\n🤖 Generating app structure...")
        
        # Generate the app structure
        app_structure = generator.generate_app_structure(user_prompt)
        
        # Display the generated structure
        print("\n📋 Generated App Structure:")
        print(json.dumps(app_structure, indent=2))
        
        # Ask if user wants to save to file
        save_choice = input("\n💾 Save to file? (y/n): ").strip().lower()
        
        if save_choice in ['y', 'yes']:
            custom_filename = input("Enter filename (or press Enter for auto-generated): ").strip()
            filename = custom_filename if custom_filename else None
            
            try:
                saved_path = generator.save_to_file(app_structure, filename)
                print(f"✅ JSON saved to: {saved_path}")
            except Exception as e:
                print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    # Example usage
    print("Example usage:")
    print("1. Set environment variable: export GOOGLE_AI_API_KEY='your_api_key_here'")
    print("2. Run the script: python app_json_generator.py")
    print("3. Enter your app description when prompted")
    print("\nStarting application...\n")
    
    main()