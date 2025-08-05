import os
import shutil
import tempfile
import unittest
from resumemodule import ResumeProcessor

# Helper to create minimal valid contact and experience files
def setup_minimal_files(tmpdir, contact_content, exp_content, exp_filename="01_Test.md"):
    info_dir = os.path.join(tmpdir, "info_test")
    exp_dir = os.path.join(tmpdir, "experience_test")
    os.makedirs(info_dir)
    os.makedirs(exp_dir)
    with open(os.path.join(info_dir, "contact.md"), "w", encoding="utf-8") as f:
        f.write(contact_content)
    with open(os.path.join(exp_dir, exp_filename), "w", encoding="utf-8") as f:
        f.write(exp_content)
    return info_dir, exp_dir

class TestResumeProcessor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))

    def test_process_resumes_success(self):
        contact = "name: Jane Doe\nemail: jane@email.com"
        exp = "# template: project_based_bullets\n### Title: Engineer\n"
        setup_minimal_files(self.tmpdir, contact, exp)
        processor = ResumeProcessor(directory=os.path.join(self.tmpdir, "experience_test"), storage_file=os.path.join(self.tmpdir, "out.json"))
        result = processor.process_resumes()
        self.assertIn("contact", result)
        self.assertIn("experience", result)
        self.assertIsInstance(result["experience"], list)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "out.json")))

    def test_missing_experience_dir(self):
        info_dir = os.path.join(self.tmpdir, "info_test")
        os.makedirs(info_dir)
        with open(os.path.join(info_dir, "contact.md"), "w") as f:
            f.write("name: Jane Doe\n")
        processor = ResumeProcessor(directory=self.tmpdir, storage_file=os.path.join(self.tmpdir, "out.json"))
        result = processor.process_resumes()
        self.assertEqual(result["experience"], [])

    def test_empty_experience_file(self):
        contact = "name: Jane Doe\n"
        exp = ""
        setup_minimal_files(self.tmpdir, contact, exp)
        processor = ResumeProcessor(directory=self.tmpdir, storage_file=os.path.join(self.tmpdir, "out.json"))
        result = processor.process_resumes()
        self.assertEqual(result["experience"], [])

    def test_parse_markdown_file_various(self):
        contact_content = "email: jane@email.com\n    Text: Jane's email\nsite: www.jane.com\n    Text: Jane's site"
        info_dir = os.path.join(self.tmpdir, "info")
        os.makedirs(info_dir)
        contact_path = os.path.join(info_dir, "contact.md")
        with open(contact_path, "w") as f:
            f.write(contact_content)
        processor = ResumeProcessor()
        result = processor.parse_markdown_file(contact_path)
        self.assertIn("email", result)
        self.assertEqual(result["email"]["description"], "Jane's email")
        self.assertIn("site", result)
        self.assertEqual(result["site"]["description"], "Jane's site")

if __name__ == "__main__":
    unittest.main()
