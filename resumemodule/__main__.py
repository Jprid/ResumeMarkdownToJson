
import argparse
import os
from resumemodule import ResumeProcessor

def main():
    parser = argparse.ArgumentParser(description="Process resume markdown files to JSON.")
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Path to output JSON file (overrides default resume_data.json)"
    )
    args = parser.parse_args()

    # Check for required directories and files
    missing = []
    info_dir = "info"
    exp_dir = "experience"
    info_contact = os.path.join(info_dir, "contact.md")
    exp_files = []
    if os.path.isdir(exp_dir):
        exp_files = [f for f in os.listdir(exp_dir) if f.endswith(".md")]
    if not os.path.isdir(info_dir) or not os.path.isfile(info_contact):
        missing.append("info/contact.md")
    if not os.path.isdir(exp_dir) or not exp_files:
        missing.append("experience/*.md")
    if missing:
        print("[ERROR] The following required files or directories are missing or empty:")
        for m in missing:
            print(f"  - {m}")
        print("\nPlease populate them as described in the README before running this script.")
        return

    if args.output:
        processor = ResumeProcessor(storage_file=args.output)
    else:
        processor = ResumeProcessor()
    experience_content = processor.process_resumes()
    processor.store_data(experience_content)

if __name__ == "__main__":
    main()
