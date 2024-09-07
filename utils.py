import re

def clean_line(line):
    line = re.sub(r'\s+', ' ', line)
    line = re.sub(r'[^A-Za-z\s]', '', line)
    return line.strip().lower()