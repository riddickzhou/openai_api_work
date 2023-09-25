import re
import json
import csv


def read_data(file_path, n=-1):
    with open(file_path, 'r', encoding='utf8') as f:
        lines = [json.loads(line.strip()) for line in f.readlines()[:n] or []]
    return [("prompt: " + i['prompt'].strip(), "response: "+ i['response'].strip()) for i in lines]


# Read the text from the file
with open("data/result_jz.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Use regular expressions to extract relevant information
pattern = r"\*\*\* NO\.(\d+) \*\*\*\s+\nA:: (.*?)\n\n(.*?)---------------------------------------"

matches = re.findall(pattern, text, re.DOTALL)

DATA_FILE_PATH = '/Users/jiamingzhou/Documents/GitHub/openai_api_work/data/time_space_evol_web_results_0915.json'
prompt_dict = read_data(DATA_FILE_PATH, n=-1)

# Create a list of dictionaries
data = []
for match in matches:
    if match[1][:1] == 'N':
        line_number = int(match[0]) + 260
        entry = {
            "original line number": line_number,
            "original response": prompt_dict[line_number],
            "corrected response": match[1:],
            "reason": match[1:],
        }
        data.append(entry)

# Save the data as a CSV file
with open("output.csv", "w", newline="") as csv_file:
    fieldnames = ["original line number", "original response", "corrected response", 'reason']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for entry in data:
        writer.writerow(entry)






