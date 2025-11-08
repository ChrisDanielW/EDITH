def clean_text(text):
    # Remove unwanted characters and whitespace
    cleaned = ' '.join(text.split())
    return cleaned

def tokenize_text(text):
    # Split the text into tokens (words)
    tokens = text.split()
    return tokens

def format_for_analysis(text):
    # Format the text for analysis (e.g., lowercasing)
    formatted = text.lower()
    return formatted

def extract_keywords(text, num_keywords=5):
    # Simple keyword extraction based on word frequency
    from collections import Counter
    tokens = tokenize_text(text)
    keyword_counts = Counter(tokens)
    keywords = keyword_counts.most_common(num_keywords)
    return [keyword[0] for keyword in keywords]