from flask import Flask, request, jsonify
from tiktok_bot_worker import start_follow_bot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "TikTok Automation API is running"}), 200

@app.route("/run-bot", methods=["POST"])
def run_bot():
    try:
        data = request.get_json()

        session_cookie = data.get("session_cookie")
        user_id = data.get("user_id")
        hashtag = data.get("hashtag", "日本トレンド")

        if not session_cookie or not user_id:
            return jsonify({"error": "Missing required fields"}), 400

        start_follow_bot(session_cookie, user_id, hashtag)

        return jsonify({"status": "Bot executed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
