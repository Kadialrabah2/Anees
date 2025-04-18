from flask import Flask, request, jsonify
from diagnosis import get_diagnosis_response
from cognitive_therapy import get_cognitive_response
from acceptance_commitment import get_act_response
from physical_act import get_physical_response

app = Flask(__name__)

@app.route('/diagnosis', methods=['POST'])
def diagnosis_route():
    data = request.get_json()
    message = data.get("message")
    user_id = data.get("user_id")

    result = get_diagnosis_response(user_id, message)
    return jsonify({
        "response": result["reply"],
        "mood_analysis": result["mood"]
    })

@app.route('/cognitive', methods=['POST'])
def cognitive_route():
    data = request.get_json()
    message = data.get("message")
    user_id = data.get("user_id")
    response = get_cognitive_response(user_id, message)
    return jsonify({"response": response})

@app.route('/act', methods=['POST'])
def act_route():
    data = request.get_json()
    message = data.get("message")
    user_id = data.get("user_id")
    response = get_act_response(user_id, message)
    return jsonify({"response": response})

@app.route('/physical', methods=['POST'])
def physical_route():
    data = request.get_json()
    message = data.get("message")
    user_id = data.get("user_id")
    response = get_physical_response(user_id, message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
