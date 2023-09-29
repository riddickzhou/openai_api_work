import json
import math
import datetime

def split_json(input_filename, prefix, users):
    # Read the input JSON file
    with open(input_filename, 'r') as json_file:
        input_data = json.load(json_file)

    # Calculate the number of items per output file
    items_per_file = math.ceil(len(input_data) / len(users))

    # Split the input data into chunks
    data_chunks = [input_data[i:i+items_per_file] for i in range(0, len(input_data), items_per_file)]

    output_prefix = f"{prefix}_files{len(input_data)}_users{len(users)}"
    # Create and save each chunk as a separate JSON file
    for i, chunk in enumerate(data_chunks):
        output_filename = f"{output_prefix}_{users[i]}.json"
        with open(output_filename, 'w') as output_file:
            json.dump(chunk, output_file, indent=4, ensure_ascii=False)

def preprocess_and_save_to_json(input_data, output_filename):
    # Process the input data into the desired format (list of dictionaries)
    processed_data = []

    for item in input_data:
        # Determine the "source" based on the presence of "id" or "source" in the item
        if "id" in item:
            source = item["id"]
        elif "source" in item:
            source = item["source"]
        else:
            source = "None"

        # Create a dictionary for each item
        processed_item = {
            "prompt": item["prompt"][0],
            "response": item.get("response", 'None'),
            "original_response": item.get("original_response", "None"),
            "source": source
        }

        # Append the processed item to the list
        processed_data.append(processed_item)

    # Save the processed data to a JSON file
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(processed_data, json_file, ensure_ascii=False, indent=4)


# Define a function to read and process the text file into JSON
def text_to_json(input_file):
    processed_lines = []

    with open(input_file, 'r') as file:
        for line in file:
            # Remove leading and trailing whitespace, and add curly braces
            processed_line = f'{line.strip()}'
            processed_lines.append(json.loads(processed_line))
    return processed_lines

if __name__ == "__main__":
    input_file = '/Users/jiamingzhou/Documents/GitHub/openai_api_work/data/tiku_forgreat_0828_altered_checked_filtered_0914.json'
    output_filename = 'tiku_forgreat_0828_altered_checked_filtered_0914_fullbatch.json'

    input_data = text_to_json(input_file)
    preprocess_and_save_to_json(input_data, output_filename)

    users = ['user_a', 'user_b', 'user_c', 'user_d']
    split_json(output_filename, 'tiku_forgreat_0828_altered_checked_filtered_0914', users)
