import os
import json
import re
from typing import List, Dict
from resumemodule.parsers import ParserFactory, parse_header

# Main Resume Processor
class ResumeProcessor:
    def __init__(
        self, directory: str = "experience", storage_file: str = "resume_data.json"
    ):
        self.directory = directory
        self.storage_file = storage_file
        self.parser_factory = ParserFactory()

    def get_sorted_files(self) -> List[str]:
        """Retrieve and sort markdown files by order prefix."""
        files = [f for f in os.listdir(self.directory) if f.endswith(".md")]
        # Sort files based on numeric prefix using string split
        return sorted(files, key=lambda x: int(x.split("_")[0]))

    def process_resumes(self) -> Dict[str, List[Dict]]:
        """Process all resume files in the directory and store results."""
        experience_content = []
        body = {
            "contact": self.parse_markdown_file(os.path.join("info", "contact.md")),
            "experience": []
        }
        for filename in self.get_sorted_files():
            # Extract company name from filename using regex
            company = re.sub(r"^\d+_|\.md$", "", filename)
            file_path = os.path.join(self.directory, filename)

            if not os.path.exists(file_path):
                print(f"File {file_path} does not exist.")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                template = parse_header(lines[0])
                if not template:
                    print(f"Skipping {filename} due to missing template header.")
                    continue
                parser = self.parser_factory.get_parser(template['template'], company)
                results = parser.parse(lines)  # Skip the first line which is the header
                if results:
                    for result in results:
                        experience_content.append(result)
                else:
                    experience_content.append(results)
        # Store parsed data for later evaluation
        body["experience"] = experience_content
        self.store_data(body)
        return body
    
    def parse_markdown_file(self, file_path):
        result = {}
        current_key = None
        
        # Regular expressions to match key-value pairs and text lines
        key_value_pattern = re.compile(r'^(\w+):\s*(.*)$')
        text_pattern = re.compile(r'^\s+Text:\s*(.*)$')
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.rstrip('\n')  # Remove trailing newline
                
                # Check for key-value pair
                key_value_match = key_value_pattern.match(line)
                if key_value_match and 'name' not in key_value_match.group(1):
                    current_key = key_value_match.group(1)
                    value = key_value_match.group(2).strip()
                    result[current_key] = {'link': value, 'description': ''}
                    continue
                elif key_value_match:
                    result[key_value_match.group(1)] = key_value_match.group(2).strip() if key_value_match else {}
                
                # Check for text line
                text_match = text_pattern.match(line)
                if text_match and current_key:
                    text_value = text_match.group(1).strip()
                    result[current_key]['description'] = text_value
        
        return result
        
    def store_data(self, content: Dict[str, List[Dict]]) -> None:
        """Store parsed data in a JSON file."""
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)

    def load_stored_data(self) -> Dict[str, List[Dict]]:
        """Load previously stored data from JSON file."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
