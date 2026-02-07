import requests
import json
import random
import string
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def generate_random_email():
    """Generates a random email address."""
    return f"user_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"

def verify_user_profile():
    print("Step 1: Registering a new user...")
    email = generate_random_email()
    password = "password123"
    register_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/user/register/", json=register_data)
        
        if register_response.status_code != 201:
            print(f"Failed to register user. Status: {register_response.status_code}")
            print(register_response.text)
            return

        print("User registered successfully.")
        
        print("Step 2: Logging in...")
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = requests.post(f"{BASE_URL}/user/login/", json=login_data)
        
        if login_response.status_code != 200:
            print(f"Failed to login. Status: {login_response.status_code}")
            print(login_response.text)
            return

        response_json = login_response.json()
        if 'data' in response_json:
            tokens = response_json['data']
        else:
            tokens = response_json # Fallback if structure is different
            
        access_token = tokens.get('access')
        if not access_token:
             print(f"Access token not found in response: {response_json}")
             return

        print("Login successful. Access token obtained.")
        
        print("Step 3: Fetching User Profile...")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        profile_response = requests.get(f"{BASE_URL}/user/profile/", headers=headers)
        
        if profile_response.status_code == 200:
            print("Profile fetched successfully!")
            print(json.dumps(profile_response.json(), indent=2))
        else:
            print(f"Failed to fetch profile. Status: {profile_response.status_code}")
            print(profile_response.text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server located at http://127.0.0.1:8000. Make sure it's running.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_user_profile()
