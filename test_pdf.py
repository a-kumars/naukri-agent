#!/usr/bin/env python3
"""
Test PDF text extraction
"""

from resume_reader import ResumeReader

reader = ResumeReader()
text = reader.extract_text_from_pdf()

print("=== Extracted Text from PDF ===")
print(text)
print("\n" + "="*50)
print(f"Total characters: {len(text)}")