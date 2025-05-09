# Import necessary libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import random # Import random for selecting a User-Agent

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow requests from your React frontend's origin.
# Replace 'http://localhost:5173' with the actual URL where your React app is running
# if it's different (e.g., http://localhost:3000 for create-react-app).
# For production, you should specify your actual frontend domain(s) instead of '*'.
CORS(app, origins=["http://localhost:5173"]) # Or your specific frontend origin

# Define a list of common User-Agent strings to rotate through
# This can help avoid being blocked if a server detects repeated requests
# from the exact same User-Agent.
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/109.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
]


# Define a route that the frontend will call
@app.route('/check_url', methods=['POST'])
def check_url():
    """
    Receives a URL from the frontend, checks its status using requests,
    and returns the result. Includes browser-like headers.
    """
    # Get the JSON data from the request body
    data = request.get_json()

    # Extract the URL from the data
    url = data.get('url')

    # Validate if URL is provided
    if not url:
        return jsonify({
            'status': 'error',
            'message': 'No URL provided',
            'statusCode': 'N/A',
            'responseTime': 'N/A'
        }), 400 # Bad Request

    print(f"Checking URL: {url}") # Log the URL being checked

    try:
        # Select a random User-Agent from the list
        selected_user_agent = random.choice(USER_AGENTS)

        # Define headers to send with the request
        headers = {
            'User-Agent': selected_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', # Common Accept header
            'Accept-Language': 'en-US,en;q=0.9', # Common Accept-Language header
            'Referer': url, # Include a Referer header (can sometimes help)
            'DNT': '1', # Do Not Track header
            'Connection': 'keep-alive', # Connection header
            'Upgrade-Insecure-Requests': '1', # Indicate preference for HTTPS
        }

        # Record the start time for response time calculation
        start_time = time.time()

        # Use requests to perform a GET request to the target URL with added headers
        # Add a timeout to prevent the request from hanging indefinitely
        # allow_redirects=False prevents requests from automatically following redirects,
        # so you get the status of the initial response (e.g., 301, 302).
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=False) # Increased timeout slightly

        # Record the end time
        end_time = time.time()

        # Calculate response time in milliseconds
        response_time_ms = (end_time - start_time) * 1000

        # Return the status code and response time in a JSON response
        return jsonify({
            'status': 'success',
            'message': 'URL check successful',
            'statusCode': response.status_code,
            'responseTime': f"{response_time_ms:.2f}" # Format to 2 decimal places
        }), 200 # OK

    except requests.exceptions.Timeout:
        # Handle request timeout
        print(f"Timeout checking URL: {url}")
        return jsonify({
            'status': 'error',
            'message': 'Request timed out',
            'statusCode': 'Timeout', # Custom status for timeout
            'responseTime': 'N/A'
        }), 504 # Gateway Timeout (appropriate for a proxy timeout)

    except requests.exceptions.RequestException as e:
        # Handle other requests-related errors (e.g., connection errors, invalid URL format for requests)
        print(f"Error checking URL {url}: {e}")
        # You might want to return a more specific status code based on the requests exception type
        # For simplicity, returning 500 here.
        return jsonify({
            'status': 'error',
            'message': f'Request failed: {str(e)}',
            'statusCode': 'Error', # Custom status for general request error
            'responseTime': 'N/A'
        }), 500 # Internal Server Error (or 502 Bad Gateway)

    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred checking URL {url}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'An unexpected error occurred: {str(e)}',
            'statusCode': 'Error',
            'responseTime': 'N/A'
        }), 500 # Internal Server Error

# To run the Flask app:
# Ensure you have Flask, Flask-CORS, and requests installed: pip install Flask Flask-CORS requests
# Save this code as app.py
# Run from your terminal: python app.py
# It will typically run on http://127.0.0.1:5000 (localhost:5000) by default.
if __name__ == '__main__':
    # Debug mode is useful during development
    # Set debug=False in production
    app.run(debug=False)
