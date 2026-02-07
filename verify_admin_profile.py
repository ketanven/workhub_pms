
import os
import sys
import django
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workhub.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from django.test import Client
from core.models import Admin

def verify_admin_profile():
    print("Step 1: Setting up Admin User...")
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
        if created:
            print("Created new test admin user.")
        else:
            print("Updated existing test admin user.")
    except Exception as e:
        print(f"Error creating admin: {e}")
        return

    print("Step 2: Authenticating via API...")
    client = Client()
    login_data = {
        "email": email,
        "password": password
    }
    
    response = client.post('/api/admin/login/', data=login_data, content_type='application/json')
    
    if response.status_code != 200:
        print(f"Login failed! Status: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.content.decode())
        return

    json_response = response.json()
    data = json_response.get('data', {})
    access_token = data.get('access')
    
    if not access_token:
        # Fallback check if structure is flat
        access_token = json_response.get('access')
        
    if not access_token:
        print("No access token found in response.")
        print(json_response)
        return
        
    print("Login successful. Access Token obtained.")

    print("Step 3: Accessing Admin Profile...")
    # Authentication header for Django test client uses HTTP_ prefix
    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {access_token}'
    }
    
    profile_response = client.get('/api/admin/profile/', **headers)
    
    if profile_response.status_code == 200:
        print("SUCCESS! Admin Profile fetched correctly.")
        print(json.dumps(profile_response.json(), indent=2))
    else:
        print(f"FAILURE! Status: {profile_response.status_code}")
        try:
             print(json.dumps(profile_response.json(), indent=2))
        except:
             print(profile_response.content.decode())

if __name__ == "__main__":
    verify_admin_profile()
