import openai
import os
import time

def summarize_text(text, max_length=2048, step=2000):
    model = 'gpt-3.5-turbo-instruct-0914'
    summarized_text = ""

    for i in range(0, len(text), step):
        chunk = text[i:i + max_length]
        prompt = f"Give a list of advanced vocabulary or slang, provide explanation: {chunk}"
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=0.5,
            max_tokens=2500,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=None #[" Human:", " AI:"]
        )
        summarized_text += response.choices[0].text.strip() + " "
        print(summarized_text)

    return summarized_text.strip()


def main(input_file):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Define input text
    with open(input_file, 'r') as file:
        input_text = file.read()

    # Call the summarization function
    summarized_text = summarize_text(input_text)
    # print(summarized_text)

    # Save the summarized text to a file with a timestamp and the keyword 'openai'
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"openai_summarized_{timestamp}.txt"

    with open(output_filename, "w") as file:
        file.write(summarized_text)


if __name__ == "__main__":
    input_file = 'The History of Jazz.txt'
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
    )
    print(response)
    print()
    # main(input_file)

