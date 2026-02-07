
import os
import sys
import django
import json
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workhub.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from django.test import Client
from core.models import Admin, User

def get_error_title(html_content):
    search = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    if search:
        return search.group(1)
    return "Unknown Error"

def verify_admin_profile():
    print("\n--- Verifying ADMIN Profile ---")
    email = "test_verify_admin@example.com"
    password = "adminpassword123"
    
    try:
        admin, created = Admin.objects.get_or_create(email=email)
        admin.set_password(password)
        admin.first_name = "Verify"
        admin.last_name = "Admin"
        admin.role = "master_admin" 
        admin.is_active = True
        admin.save()
    except Exception as e:
        print(f"Error creating admin: {e}")
        return

    client = Client()
    login_data = {"email": email, "password": password}
    
    print(f"Logging in as {email}...")
    response = client.post('/api/admin/login/', data=login_data, content_type='application/json')
    
    if response.status_code != 200:
        print(f"Login failed! Status: {response.status_code}")
        print(response.content.decode()[:500])
        return

    token = response.json().get('data', {}).get('access') or response.json().get('access')
    if not token:
        print(f"No token found in response: {response.json()}")
        return
        
    print("Login successful.")

    print("Fetching Admin Profile...")
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    profile_response = client.get('/api/admin/profile/', **headers)
    
    if profile_response.status_code == 200:
        print("SUCCESS! Admin Profile fetched.")
        print(json.dumps(profile_response.json(), indent=2))
    else:
        print(f"FAILURE! Status: {profile_response.status_code}")
        try:
             print(json.dumps(profile_response.json(), indent=2))
        except:
             print(f"Error Page Title: {get_error_title(profile_response.content.decode())}")
             # print(profile_response.content.decode()[:1000])

def verify_user_profile():
    print("\n--- Verifying USER Profile ---")
    email = "test_verify_user@example.com"
    password = "userpassword123"
    
    try:
        user, created = User.objects.get_or_create(email=email)
        user.set_password(password)
        user.first_name = "Verify"
        user.last_name = "User"
        user.is_active = True
        user.save()
    except Exception as e:
        print(f"Error creating user: {e}")
        return

    client = Client()
    login_data = {"email": email, "password": password}
    
    print(f"Logging in as {email}...")
    response = client.post('/api/user/login/', data=login_data, content_type='application/json')
    
    if response.status_code != 200:
        print(f"Login failed! Status: {response.status_code}")
        print(response.content.decode()[:500])
        return

    token = response.json().get('data', {}).get('access') or response.json().get('access')
    if not token:
        print(f"No token found in response: {response.json()}")
        return
        
    print("Login successful.")

    print("Fetching User Profile...")
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    profile_response = client.get('/api/user/profile/', **headers)
    
    if profile_response.status_code == 200:
        print("SUCCESS! User Profile fetched.")
        print(json.dumps(profile_response.json(), indent=2))
    else:
        print(f"FAILURE! Status: {profile_response.status_code}")
        try:
             print(json.dumps(profile_response.json(), indent=2))
        except:
             print(f"Error Page Title: {get_error_title(profile_response.content.decode())}")
             # print(profile_response.content.decode()[:1000])

if __name__ == "__main__":
    verify_admin_profile()
    verify_user_profile()
