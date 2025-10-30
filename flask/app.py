from flask import Flask, request, jsonify,  render_template
app = Flask(__name__)

def llama(description: str) -> dict:
    return {
        "description": description,
    }

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/", methods=["POST"])
def get_desc():
    data = request.get_json()

    if not data or "description" not in data:
        return jsonify({"error": "Missing 'description' field"}), 400

    result = llama(data["description"].strip())
    return jsonify({"result": result})
