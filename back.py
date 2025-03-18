from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Supabase setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# APIs
@app.route('/assign-workout', methods=['POST'])
def assign_workout():
    """
    Assign a workout to a trainee.
    """
    data = request.json
    workout = {
        "trainer_id": data['trainer_id'],
        "trainee_id": data['trainee_id'],
        "workout_name": data['workout_name'],
        "reps": data['reps'],
        "sets": data['sets'],
        "weight": data['weight'],
        "date_assigned": datetime.now().isoformat()
    }
    supabase.table('workouts').insert(workout).execute()
    return jsonify({"message": "Workout assigned successfully!"}), 201


@app.route('/complete-workout', methods=['POST'])
def complete_workout():
     """
    Mark a workout as completed and update progress.
    """
    data = request.json
    supabase.table('workouts').update({"date_completed": datetime.now().isoformat()}).eq("workout_id", data['workout_id']).execute()


    # Update progress and check for level-up
    progress = supabase.table('progress').select("*").eq("trainee_id", data['trainee_id']).execute().data
    if progress:
        new_progress = progress[0]['progress_value'] + 10
        supabase.table('progress').update({"progress_value": new_progress}).eq("trainee_id", data['trainee_id']).execute()


        if new_progress % 100 == 0:
            level = progress[0]['level'] + 1
            supabase.table('progress').update({"level": level}).eq("trainee_id", data['trainee_id']).execute()
            supabase.table('badges').insert({
                "trainee_id": data['trainee_id'],
                "badge_name": f"Level {level} Achieved"
            }).execute()

    return jsonify({"message": "Workout completed!"}), 200


@app.route('/send-message', methods=['POST'])
def send_message():
    """
    Send a message from one user to another.
    """
    data = request.json
    supabase.table('messages').insert(data).execute()
    return jsonify({"message": "Message sent successfully!"}), 200


@app.route('/get-messages', methods=['GET'])
def get_messages():
    """
    Retrieve messages between two users.
       """
    sender_id = request.args.get('sender_id')
    receiver_id = request.args.get('receiver_id')
    messages = supabase.table('messages').select("*").eq("sender_id", sender_id).eq("receiver_id", receiver_id).execute().data
    return jsonify(messages), 200


# Run the app
if __name__ == '__main__':
    app.run(debug=True)