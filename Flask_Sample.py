from flask import Flask,jsonify

app = Flask(__name__)

data = [{"id": 1, "Name": "Company One"}, {"id": 2, "Name": "Company Two"}]

@app.route('/')
def index():
    return " Hello Yashwanth let's start Flask"

@app.route('/data', methods=['GET'])
def get():
    return jsonify({'Data':data})

@app.route('/data/<int:id>', methods=['GET'])
def get_name(id):
    return jsonify({'Data':data[id]})

@app.route('/data', methods=['POST'])
def create():
    datan = {"id": 3, "Name": "Company Three"}
    data.append(datan)
    return jsonify({'Created':data})

if __name__ == "__main__":
    app.run(debug=True)

