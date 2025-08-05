if __name__ == "__main__":
    from resumemodule import ResumeProcessor
    processor = ResumeProcessor()
    experience_content = processor.process_resumes()
    processor.store_data(experience_content)
