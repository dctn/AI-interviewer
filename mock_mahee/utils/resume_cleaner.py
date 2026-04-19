import re
from typing import List


def clean_resume_text(raw_text: str, remove_emails: bool = True, remove_urls: bool = True) -> str:
    text = raw_text

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove page numbers
    text = re.sub(r'\b\d+\b\s*Page\s*\d+', '', text, flags=re.IGNORECASE)

    # Clean bullet points
    text = re.sub(r'[-•*+]\s*', '', text)

    # If remove emails
    if remove_emails:
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    # If remove URLs
    if remove_urls:
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', text)

    return text.strip()
