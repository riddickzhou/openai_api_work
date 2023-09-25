from flask import Blueprint, Response, render_template, request, flash, redirect, jsonify, make_response
from . import db   ##means from __init__.py import db
from flask_login import login_required, current_user
import json
from .models import Note, PromptResponse

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    processed_text = ""  # Initialize an empty processed text

    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            # Process the note
            processed_text = process_text(note)
            new_note = Note(data=note, processed_data=processed_text, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    # Retrieve JsonItem data from the database
    json_items = PromptResponse.query.all()

    return render_template("home.html", user=current_user, json_items=json_items)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})



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

                # Save the prompt and response to the database
                new_item = PromptResponse(
                    prompt=prompt,
                    response=response,
                    machine_feedback='',
                    human_feedback='',
                    user_id=current_user.id
                )
                db.session.add(new_item)

            db.session.commit()

            flash(f'Items from {file} uploaded and saved to the database.', category='success')
        except Exception as e:
            flash(f'Error processing JSON file: {str(e)}', category='error')

    # Call the function to remove duplicates
    remove_duplicate_json_items()
    return redirect('/')


def process_text(text):
    return text[::-1]


def remove_duplicate_json_items():
    # Find duplicate items based on "prompt" and "response" values
    duplicate_items = (
        db.session.query(PromptResponse.prompt, PromptResponse.response)
        .group_by(PromptResponse.prompt, PromptResponse.response)
        .having(db.func.count() > 1)
        .distinct()
        .all()
    )

    # Remove duplicates, keeping the first occurrence
    for prompt, response in duplicate_items:
        duplicate_items_to_remove = PromptResponse.query.filter_by(prompt=prompt, response=response).all()

        # Keep the first occurrence and delete the rest
        for item in duplicate_items_to_remove[1:]:
            db.session.delete(item)

    db.session.commit()


@views.route('/download_json', methods=['GET'])
def download_json():
    # Query the JsonItem table to retrieve the JSON data
    json_items = PromptResponse.query.all()

    # Create a list to store JSON objects
    json_data = []

    for item in json_items:
        json_data.append({
            'prompt': item.prompt,
            'response': item.response,
            'machine_feedback': item.machine_feedback,
            'human_feedback': item.human_feedback,
        })

    # Convert the list of JSON objects to a JSON string
    json_string = json.dumps(json_data, ensure_ascii=False, indent=2)

    # Create a response with the JSON content and set the headers
    response = make_response(json_string)
    response.headers['Content-Type'] = 'application/json'
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

        # Update the JSON item in the database
        json_item = PromptResponse.query.get(json_item_id)

        if json_item:
            json_item.human_feedback = edited_human_feedback
            db.session.commit()

            return jsonify(success=True, message='Changes saved')
        else:
            return jsonify(success=False, message='JSON item not found'), 404
    except Exception as e:
        return jsonify(success=False, message=str(e))


# Server-side route to handle deleting a JSON item
@views.route('/delete_json_item', methods=['POST'])
@login_required
def delete_json_item():
    try:
        data = request.get_json()
        json_item_id = data.get('json_item_id')

        # Retrieve the JSON item from the database
        json_item = PromptResponse.query.get(json_item_id)

        if json_item:
            # Check if the logged-in user owns the JSON item (you may need to implement this check)
            if json_item.user_id == current_user.id:
                db.session.delete(json_item)
                db.session.commit()
                return jsonify(success=True, message='JSON item deleted')
            else:
                return jsonify(success=False, message='You do not have permission to delete this JSON item'), 403
        else:
            return jsonify(success=False, message='JSON item not found'), 404
    except Exception as e:
        return jsonify(success=False, message=str(e))


# Server-side route to fetch JSON items
@views.route('/get_json_items', methods=['GET'])
@login_required
def get_json_items():
    json_items = PromptResponse.query.all()
    return jsonify(json_items=[json_item.serialize() for json_item in json_items])


@views.route('/delete_all_json_items', methods=['POST'])
@login_required
def delete_all_json_items():
    try:
        # Delete all JSON items associated with the current user
        PromptResponse.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify(success=True, message='All items deleted')
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(success=False, message='Failed to delete all items'), 500

