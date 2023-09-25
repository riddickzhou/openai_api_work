import os
import openai
import datetime
from flask_login import login_required, current_user
from flask import Blueprint, jsonify
from .models import PromptResponse
from . import mongo

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = 'gpt-3.5-turbo'
INSTRUCTION_SYS = '你是一个题库错误梳理专家'
INSTRUCTION_USER = """下面我会输入一些问题以及对应的答案，问题与答案用'-|-'分隔。任务是判断答案是否正确。如果正确返回'YES'，并以专家的口吻作答一遍; 如果不正确，返回'NO'，指出存在的问题并用中文重新生成正确答案。"""
openai.api_key = OPENAI_API_KEY

gpt = Blueprint('gpt', __name__)

def get_results(input_messages):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=input_messages,
            temperature=0,
            max_tokens=3500
        )
        return response.choices[0].message['content']
    except Exception as e:  # Catch specific exception
        print(e)
        return f"Error occurred: {e}"


def build_messages(prompt, response):
    return [
        {"role": "system", "content": INSTRUCTION_SYS},
        {"role": "user", "content": INSTRUCTION_USER},
        {"role": "user", "content": f"{prompt}-|-{response}"}
    ]


def get_results(input_messages):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=input_messages,
            temperature=0,
            max_tokens=3500
        )
        return response.choices[0].message['content']
    except Exception as e:  # Catch specific exception
        print(f"Error occurred: {e}")
        return 'Error'


@gpt.route('/generate_machine_feedback', methods=['GET', 'POST'])
@login_required
def generate_machine_feedback():
    # Retrieve all PromptResponse documents from the MongoDB collection
    prompt_responses = mongo.db.prompt_responses.find()

    # Iterate through the PromptResponse documents and update the machine_feedback field
    for prompt_response in prompt_responses:
        message = build_messages(prompt_response['prompt'], prompt_response['response'])
        # Update the machine_feedback field
        prompt_response['machine_feedback'] = get_results(message)
        # prompt_response['machine_feedback'] = "dummy machine feedback added"

        # Save the updated document back to MongoDB
        mongo.db.prompt_responses.update_one(
            {'_id': prompt_response['_id']},
            {'$set': {'machine_feedback': prompt_response['machine_feedback']}}
        )

    return jsonify(success=True)
