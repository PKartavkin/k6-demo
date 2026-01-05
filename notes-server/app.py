from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'notes_db')
COLLECTION_NAME = 'notes'

try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    notes_collection = db[COLLECTION_NAME]
    # Ensure collection exists by creating an index
    notes_collection.create_index('title')
except PyMongoError as e:
    print(f"Warning: Could not connect to MongoDB: {e}")
    notes_collection = None

# Basic Auth credentials (in production, use environment variables)
users = {
    os.getenv('API_USER', 'admin'): os.getenv('API_PASSWORD', 'password')
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

def get_collection():
    """Get or create the collection"""
    global notes_collection
    if notes_collection is None:
        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            notes_collection = db[COLLECTION_NAME]
            notes_collection.create_index('title')
        except PyMongoError as e:
            raise Exception(f"Database connection failed: {e}")
    return notes_collection

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint (no auth required)"""
    try:
        collection = get_collection()
        collection.find_one()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.route('/notes', methods=['GET'])
@auth.login_required
def get_notes():
    """Get all notes"""
    try:
        collection = get_collection()
        notes = list(collection.find({}))
        for note in notes:
            note['id'] = str(note['_id'])
            del note['_id']
        return jsonify(notes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<note_id>', methods=['GET'])
@auth.login_required
def get_note(note_id):
    """Get a specific note by ID"""
    try:
        collection = get_collection()
        try:
            note = collection.find_one({'_id': ObjectId(note_id)})
        except InvalidId:
            return jsonify({'error': 'Invalid note ID'}), 400
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        note['id'] = str(note['_id'])
        del note['_id']
        return jsonify(note), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes', methods=['POST'])
@auth.login_required
def create_note():
    """Create a new note"""
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        collection = get_collection()
        now = datetime.utcnow()
        note = {
            'title': data['title'],
            'content': data.get('content', ''),
            'created_at': now,
            'updated_at': now
        }
        
        result = collection.insert_one(note)
        note['id'] = str(result.inserted_id)
        
        return jsonify(note), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<note_id>', methods=['PUT'])
@auth.login_required
def update_note(note_id):
    """Update an existing note"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        collection = get_collection()
        try:
            update_data = {'updated_at': datetime.utcnow()}
            if 'title' in data:
                update_data['title'] = data['title']
            if 'content' in data:
                update_data['content'] = data['content']
            
            result = collection.update_one(
                {'_id': ObjectId(note_id)},
                {'$set': update_data}
            )
        except InvalidId:
            return jsonify({'error': 'Invalid note ID'}), 400
        
        if result.matched_count == 0:
            return jsonify({'error': 'Note not found'}), 404
        
        note = collection.find_one({'_id': ObjectId(note_id)})
        note['id'] = str(note['_id'])
        del note['_id']
        
        return jsonify(note), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<note_id>', methods=['DELETE'])
@auth.login_required
def delete_note(note_id):
    """Delete a note"""
    try:
        collection = get_collection()
        try:
            result = collection.delete_one({'_id': ObjectId(note_id)})
        except InvalidId:
            return jsonify({'error': 'Invalid note ID'}), 400
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Note not found'}), 404
        
        return jsonify({'message': 'Note deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

