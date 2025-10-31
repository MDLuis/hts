from flask import Flask, request, jsonify,  render_template
from ..query import start_conv, continue_conv
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/start", methods=["POST"])
def start():
    data = request.get_json()
    desc = data.get("description", "").strip()
    if not desc:
        return jsonify({"error": "Missing description"}), 400

    result = start_conv(desc)
    return jsonify(result)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    reply = data.get("reply", "").strip()
    messages = data.get("messages")

    if not reply or not messages:
        return jsonify({"error": "Missing fields"}), 400

    result = continue_conv(reply, messages)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
