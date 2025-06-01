from flask import Flask, render_template, request, jsonify
import requests
from model import make_recommendation

# webapp
app = Flask(__name__, template_folder='./')

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/get')
def get_from_api():
    query = request.args.get('msg')
    try:
        # Call your recommendation function directly
        response = make_recommendation(str(query))
        return jsonify(response)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Something went wrong"}), 500  # Return a valid error response

if __name__ == '__main__':
    app.run(debug=True)
