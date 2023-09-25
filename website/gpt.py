import os
import openai
import datetime
from flask_login import login_required, current_user
from flask import Blueprint, jsonify
from .models import PromptResponse
from . import db

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
    # Retrieve all JsonItem objects from the database
    json_items = PromptResponse.query.all()

    # Iterate through the JsonItem objects and update the machine_feedback column
    for json_item in json_items:
        message = build_messages(json_item.prompt, json_item.response)
        # Update the machine_feedback column
        json_item.machine_feedback = get_results(message)
        # json_item.machine_feedback = "dummy machine feedback added"

        # Commit the changes to the database
        db.session.commit()

    return jsonify(success=True)
