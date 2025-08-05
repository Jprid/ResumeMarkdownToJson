import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable

def parse_header(line: str) -> Optional[Dict[str, str]]:
    """Parse a markdown header line into a key-value dictionary."""
    match = re.match(r"^(#|##|###|####)\s+(?P<key>.*?):\s*(?P<value>.*)$", line)
    if match:
        key = match.group("key").strip().lower()
        return {key: match.group("value").strip()} if key else None
    return None

class ResumeParserStrategy(ABC):
    """Abstract base class for parsing resume markdown files."""
    def __init__(self, company: str = ""):
        self.company = company
        self.curr_item: Dict = {}  # Initialize as empty; set in parse()
        self.curr_key = None

    @abstractmethod
    def parse(self, lines: List[str]) -> List[Dict]:
        """Parse markdown lines into a list of structured dictionaries."""
        pass

    def parse_common(self, lines: List[str], new_item_callback: Callable[[str, List[Dict]], None],
                    line_handler: Callable[[str, bool], None]) -> List[Dict]:
        """Common parsing logic using callbacks for strategy-specific behavior."""
        content = []
        self.curr_item = self.default_fields()  # Initialize curr_item
        for line in lines:
            match line:
                case l if self.is_empty(l) or self.is_template_header(l):
                    continue
                case l if self.is_role_header(l) and ":" in l:
                    new_item_callback(line, content)
                case l if self.is_sub_header(l) and ":" in l:
                    self.extract_and_add_field(line)
                case l if self.is_sub_header(l):
                    line_handler(line, is_sub_header=True)
                    self.curr_key = None
                case _ if self.curr_key and self.curr_key == "tags":
                        self.curr_item[self.curr_key].append(line.replace('-', '', 1).strip())
                case _:
                    self.curr_key = None
                    line_handler(line, is_sub_header=False)

        if self.curr_item["title"] and self.curr_item not in content:
            content.append(self.curr_item)
        return content

    def default_fields(self) -> Dict:
        """Return default fields for a resume item."""
        return {
            "company": self.company,
            "title": "",
            "start": "",
            "end": "",
            "experience_content": []
        }

    def is_empty(self, line: str) -> bool:
        """Check if a line is empty or contains only whitespace."""
        return line.strip() == ""

    def is_template_header(self, line: str) -> bool:
        """Check if a line is a template header (starts with '# ')."""
        return line.startswith("# ")

    def is_role_header(self, line: str) -> bool:
        """Check if a line is a role header (starts with '## ')."""
        return line.startswith("## ")

    def is_sub_header(self, line: str) -> bool:
        """Check if a line is a sub-header (starts with '### ' or '#### ')."""
        return line.startswith("###") or line.startswith("####")

    def extract_and_add_field(self, line: str) -> None:
        """Extract key-value pair from a header line and add to current item."""
        header = parse_header(line)
        if header:
            self.curr_key = [*header.keys()][0].strip()
            if self.curr_key == "tags":
                self.curr_item[self.curr_key] = []
                return
            self.curr_item.update(header)

class ProjParasParserStrategy(ResumeParserStrategy):
    """Parser for project-based resume with paragraph-style content."""
    def new_item_callback(self, line: str, content: List[Dict]) -> None:
        header = parse_header(line)
        self.curr_item = self.default_fields()
        if header:
            self.curr_item["title"] = header.get("title", "")

    def line_handler(self, line: str, is_sub_header: bool) -> None:
        if is_sub_header:
            project_item = {"project_title": line.split("#### ")[1].strip(), "experience_content": ""}
            self.curr_item["experience_content"].append(project_item)
        else:
            if self.curr_item["experience_content"]:
                self.curr_item["experience_content"][-1]["experience_content"] = line.strip()

    def parse(self, lines: List[str]) -> List[Dict]:
        return self.parse_common(lines, self.new_item_callback, self.line_handler)

class GalileoParserStrategy(ResumeParserStrategy):
    """Parser for project-based resume with bullet-style content."""
    def parse(self, lines: List[str]) -> List[Dict]:
        def new_item_callback(line: str, content: List[Dict]) -> None:
            header = parse_header(line)
            self.curr_item = self.default_fields()
            if header:
                self.curr_item["title"] = header.get("title", "")

        def line_handler(line: str, is_sub_header: bool) -> None:
            if is_sub_header:
                line_content = line.split("#### ")[1].strip()
                new_item = {"project_title": line_content, "experience_content": []}
                self.curr_item["experience_content"].append(new_item)
            else:
                if self.curr_item["experience_content"]:
                    self.curr_item["experience_content"][-1]["experience_content"].append(line.strip())

        return self.parse_common(lines, new_item_callback, line_handler)

class RelativityParserStrategy(ResumeParserStrategy):
    """Parser for multiple roles with bullet-style content."""
    def parse(self, lines: List[str]) -> List[Dict]:
        def new_item_callback(line: str, content: List[Dict]) -> None:
            if self.curr_item["title"]:
                content.append(self.curr_item)
            self.curr_item = self.default_fields()
            header = parse_header(line)
            if header:
                self.curr_item["title"] = header.get("title", "")

        def line_handler(line: str, is_sub_header: bool) -> None:
            if not is_sub_header:
                self.curr_item["experience_content"].append(line.strip())

        return self.parse_common(lines, new_item_callback, line_handler)

class ParserFactory:
    """Factory to create resume parser strategies based on template type."""
    @staticmethod
    def get_parser(template: str, company: str) -> ResumeParserStrategy:
        parsers = {
            "project_based_paras": ProjParasParserStrategy,
            "project_based_bullets": GalileoParserStrategy,
            "multiple_roles_bullets": RelativityParserStrategy,
        }
        parser_class = parsers.get(template)
        if not parser_class:
            raise ValueError(f"Unknown template: {template}")
        return parser_class(company)