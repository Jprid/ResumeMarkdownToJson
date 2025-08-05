# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
# ResumeModule

A Python module for processing resume markdown files into JSON and HOCON formats.

## Project Structure
- `resumemodule/` - The main module
- `example.py` - Example script of using component in code
- `setup.py` - Packaging file

## Installation

```sh
pip install .
```

## Before Using

Make sure to populate the info directory with a `contact.md` file and the `experience` directory with files of the format `<ORDINAL>_<COMPANY_NAME>.md`

the files in the experience folder must match the structure and format listed below in order to be properly parsed. You can extend
the scripts to handle different templates as necessary, just update the [`ParserFactory`](./resumemodule/parsers.py) to properly handle the template tag in the content.

## Example Required Directory Structure and Files

```
your_project/
├── info/
│   └── contact.md
└── experience/
    └── 01_ExampleCorp.md
    └── 02_AnotherCorp.md
```

**info/contact.md**

```markdown
first_name: Jane
nickname: Jay
last_name: Doe
Email: mailto:jane.doe@email.com
Site: www.janedoe.com
    Text: JaneDoe.com
Linkedin: https://linkedin.com/in/janedoe
    Text: Janedoe
Github: https://github.com/janedoe
    Text: janedoe
```

**experience/01_ExampleCorp.md**
```markdown
# template: project_based_bullets
## Title: Software Engineer
### Company: Example Corp
### Start: Jan 2020
### End: Dec 2022

### Tags:
- Tag1
- Tag2

#### <PROJECT_TITLE>
<PROJECT_BULLET_1>
<PROJECT_BULLET_2>
<PROJECT_BULLET_3>
#### <PROJECT_TITLE2>
<PROJECT2_BULLET_1>
```

---

## Usage

You can use the module in your Python code:

*using default path see [__main__](resumemodule/__main__.py) for example of custom output path as shown below*

```python
from resumemodule import ResumeProcessor
processor = ResumeProcessor()
experience_content = processor.process_resumes()
processor.store_data(experience_content)
```

Or run as a CLI script:

```sh
# Default output (resume_data.json)
python -m resumemodule

# Specify a custom output path
python -m resumemodule --output my_resume.json
# or using the short flag
python -m resumemodule -o my_resume.json
```


