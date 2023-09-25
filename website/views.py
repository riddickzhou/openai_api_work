from flask import Blueprint, render_template, request, flash, redirect,jsonify
from . import db   ##means from __init__.py import db
from flask_login import login_required, current_user
import json
from .models import Note, JsonItem

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
    json_items = JsonItem.query.all()

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
                new_item = JsonItem(
                    prompt=prompt,
                    response=response,
                    user_id=current_user.id
                )
                db.session.add(new_item)

            db.session.commit()

            flash('JSON file uploaded and saved to the database.', category='success')
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
        db.session.query(JsonItem.prompt, JsonItem.response)
        .group_by(JsonItem.prompt, JsonItem.response)
        .having(db.func.count() > 1)
        .distinct()
        .all()
    )

    # Remove duplicates, keeping the first occurrence
    for prompt, response in duplicate_items:
        duplicate_items_to_remove = JsonItem.query.filter_by(prompt=prompt, response=response).all()

        # Keep the first occurrence and delete the rest
        for item in duplicate_items_to_remove[1:]:
            db.session.delete(item)

    db.session.commit()
