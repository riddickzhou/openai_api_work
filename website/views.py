from flask import Blueprint, Response, render_template, request, flash, redirect, jsonify, make_response
from . import mongo
from flask_login import login_required, current_user
import json
from .models import PromptResponse
from bson import json_util
from collections import defaultdict
import uuid
from datetime import datetime

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Retrieve PromptResponse data from the MongoDB collection
    json_items = mongo.db.prompt_responses.find({'user_id': current_user.id})
    json_items_list = []
    for item in json_items:
        prompt_response = PromptResponse(
            prompt=item['prompt'],
            response=item['response'],
            machine_feedback=item.get('machine_feedback', ''),
            human_feedback=item.get('human_feedback', ''),
            user_id=item.get('user_id', ''),
            _id=item.get('_id', ''),
            created_at=item.get('created_at', '')
        )
        json_items_list.append(prompt_response)
    return render_template("home.html", user=current_user, json_items=json_items_list)


@views.route('/upload_json', methods=['POST'])
@login_required
def upload_json():
    if 'json_file' not in request.files:
        flash('No file part', category='error')
        return redirect(request.url)

    file = request.files['json_file']

    if file.filename == '':
        flash('No selected file', category='error')
        return redirect(request.url)

    if file:
        try:
            # Read the JSON content from the uploaded file
            json_data = file.read().decode('utf-8')

            # Parse the JSON content
            data_list = json.loads(json_data)

            # Iterate through the JSON data list and save each item to the database
            for item in data_list:
                prompt = item.get('prompt', '')
                response = item.get('response', '')
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

                # Save the prompt and response to the MongoDB collection
                new_item = PromptResponse(
                    prompt=prompt,
                    response=response,
                    machine_feedback='',
                    human_feedback='',
                    user_id=current_user.id,
                    _id=uuid.uuid4().hex,
                    created_at=formatted_datetime
                )
                mongo.db.prompt_responses.insert_one(new_item.__dict__)

            flash(f'Items from {file.filename} uploaded and saved to the database.', category='success')
        except Exception as e:
            flash(f'Error processing JSON file: {str(e)}', category='error')

    # Call the function to remove duplicates
    remove_duplicate_json_items()
    return redirect('/')


def remove_duplicate_json_items():
    # Find duplicate items based on "prompt" and "response" values
    cursor = mongo.db.prompt_responses.find({}, {'prompt': 1, 'response': 1})

    # Create a dictionary to store items grouped by prompt and response
    grouped_items = defaultdict(list)

    # Iterate through the cursor and group items
    for item in cursor:
        prompt = item['prompt']
        response = item['response']
        grouped_items[(prompt, response)].append(item['_id'])

    # Remove duplicates, keeping the first occurrence
    for items_to_remove in grouped_items.values():
        print(items_to_remove)
        if len(items_to_remove) > 1:
            # Keep the first occurrence and delete the rest
            items_to_delete = items_to_remove[1:]

            for item_id in items_to_delete:
                mongo.db.prompt_responses.delete_one({'_id': item_id})


@views.route('/download_json', methods=['GET'])
def download_json():
    # Query the MongoDB collection to retrieve the JSON data
    json_items = mongo.db.prompt_responses.find()

    # Create a response with the JSON content and set the headers
    response = Response(json_util.dumps(json_items, ensure_ascii=False, indent=2).encode('utf-8'), content_type='application/json')
    response.headers['Content-Disposition'] = 'attachment; filename=json_data.json'

    return response


# Server-side route to handle saving edited JSON item
@views.route('/save_json_item', methods=['POST'])
@login_required
def save_json_item():
    try:
        data = request.get_json()  # Retrieve JSON data from the request body
        json_item_id = data.get('json_item_id')
        edited_human_feedback = data.get('edited_human_feedback')
        print('data:', data)
        print('edited_human_feedback:', edited_human_feedback)
        print('json_item_id:', json_item_id)

        # Update the JSON item in the MongoDB collection
        mongo.db.prompt_responses.update_one(
            {'_id': json_item_id, 'user_id': current_user.id},
            {'$set': {'human_feedback': edited_human_feedback}}
        )

        return jsonify(success=True, message='Changes saved')
    except Exception as e:
        return jsonify(success=False, message=str(e))


# Server-side route to handle deleting a JSON item
@views.route('/delete_json_item', methods=['POST'])
@login_required
def delete_json_item():
    try:
        data = request.get_json()
        json_item_id = data.get('json_item_id')
        print (json_item_id)

        # Delete the JSON item from the MongoDB collection
        result = mongo.db.prompt_responses.delete_one({'_id': json_item_id, 'user_id': current_user.id})

        if result.deleted_count > 0:
            return jsonify(success=True, message='JSON item deleted')
        else:
            return jsonify(success=False, message='JSON item not found'), 404
    except Exception as e:
        return jsonify(success=False, message=str(e))


@views.route('/delete_all_json_items', methods=['POST'])
@login_required
def delete_all_json_items():
    try:
        # Delete all JSON items associated with the current user
        result = mongo.db.prompt_responses.delete_many({'user_id': current_user.id})

        if result.deleted_count > 0:
            return jsonify(success=True, message='All items deleted')
        else:
            return jsonify(success=False, message='No items found to delete')
    except Exception as e:
        return jsonify(success=False, message=str(e))
