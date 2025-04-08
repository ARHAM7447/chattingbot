import boto3
import hmac
import hashlib
import base64
import os

# AWS Cognito Config
AWS_REGION = "ap-southeast-2"
USER_POOL_ID = "ap-southeast-2_0vVIpJCap"
CLIENT_ID = "3gk0nh5onrtvm8kr276qgmeuuj"
CLIENT_SECRET = "ulqdjgbb7ikdt3llvh9fqan62346rm5v0uv62gumnt9ht5qjrhq"  # <- Replace with your actual secret

# Create Cognito client
client = boto3.client('cognito-idp', region_name=AWS_REGION)


# 🔐 Secret hash generator
def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(client_secret.encode('utf-8'),
                   message.encode('utf-8'),
                   hashlib.sha256).digest()
    return base64.b64encode(dig).decode()


# ✅ Signup Function
def signup_user(email, password):
    print("⚙️ Inside signup_user function")
    try:
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}

        response = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=get_secret_hash(email, CLIENT_ID, CLIENT_SECRET),
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email}
            ]
        )
        print("✅ Cognito signup response:", response)
        return {'success': True, 'message': 'Signup successful! Please check your email to verify your account.'}

    except client.exceptions.UsernameExistsException:
        return {'success': False, 'error': 'User already exists. Try logging in.'}
    except client.exceptions.InvalidPasswordException as e:
        return {'success': False, 'error': 'Password does not meet security requirements.'}
    except client.exceptions.InvalidParameterException as e:
        return {'success': False, 'error': 'Invalid signup parameters. Please check email format and password.'}
    except client.exceptions.UserLambdaValidationException as e:
        return {'success': False, 'error': 'Signup blocked by a pre-signup Lambda trigger.'}
    except Exception as e:
        print("🚨 Unexpected error:", str(e))
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}


# ✅ Login Function
def login_user(email, password):
    print("⚙️ Inside login_user function")
    try:
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}

        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': get_secret_hash(email, CLIENT_ID, CLIENT_SECRET)
            },
            ClientId=CLIENT_ID
        )
        print("✅ Cognito login response:", response)
        return {'success': True, 'message': 'Login successful!', 'tokens': response['AuthenticationResult']}

    except client.exceptions.NotAuthorizedException:
        return {'success': False, 'error': 'Incorrect username or password.'}
    except client.exceptions.UserNotConfirmedException:
        return {'success': False, 'error': 'User is not confirmed. Please verify your email.'}
    except Exception as e:
        print("🚨 Unexpected login error:", str(e))
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

def confirm_user(email, code):
    try:
        secret_hash = get_secret_hash(email, CLIENT_ID, CLIENT_SECRET)  # 🔐 Generate secret hash
        response = client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            SecretHash=secret_hash  # ✅ Add this
        )
        return {"success": True, "message": "User confirmed successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}  # ✅ Good change
