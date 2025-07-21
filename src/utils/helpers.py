def clean_text(text):
    """Cleans the input text by stripping whitespace and removing unwanted characters."""
    return ' '.join(text.split())

def format_data(data):
    """Formats the scraped data into a desired structure."""
    # Example: Convert data to a dictionary or a specific format
    return {key: value for key, value in data.items()}

def log_message(message):
    """Logs a message to the console or a log file."""
    print(f"[LOG] {message}")