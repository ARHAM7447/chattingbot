import boto3  # AWS SDK for Python to interact with Cognito
import hmac  # For generating HMAC for secret hash
import hashlib  # For SHA-256 hashing
import base64  # To encode the hash result in base64
import os  # For environment variable support if needed

# AWS Cognito Config
AWS_REGION = "ap-southeast-2"  # Your AWS region where Cognito User Pool is hosted
USER_POOL_ID = "ap-southeast-2_0vVIpJCap"  # Cognito User Pool ID
CLIENT_ID = "3gk0nh5onrtvm8kr276qgmeuuj"  # App client ID from Cognito
CLIENT_SECRET = "ulqdjgbb7ikdt3llvh9fqan62346rm5v0uv62gumnt9ht5qjrhq"  # App client secret (keep this safe!)

# Create Cognito client
client = boto3.client('cognito-idp', region_name=AWS_REGION)  # Creates a client to interact with Cognito Identity Provider


# 🔐 Secret hash generator
def get_secret_hash(username, client_id, client_secret):
    # Concatenate username and client ID as required by Cognito
    message = username + client_id
    # Generate HMAC using client secret as key and message as payload, hashed with SHA256
    dig = hmac.new(client_secret.encode('utf-8'),
                   message.encode('utf-8'),
                   hashlib.sha256).digest()
    # Encode the result in base64
    return base64.b64encode(dig).decode()


# ✅ Signup Function
def signup_user(email, password):
    print("⚙️ Inside signup_user function")
    try:
        # Basic check for password length
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}

        # Call Cognito to sign up user with email and password
        response = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=get_secret_hash(email, CLIENT_ID, CLIENT_SECRET),  # Secure the request
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email}  # Set email as a required attribute
            ]
        )
        print("✅ Cognito signup response:", response)
        # If successful, return success message
        return {'success': True, 'message': 'Signup successful! Please check your email to verify your account.'}

    # Catch various common Cognito exceptions and return user-friendly messages
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
        # Basic check for password length
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}

        # Initiate auth request using USER_PASSWORD_AUTH flow
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',  # Use username-password based authentication
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': get_secret_hash(email, CLIENT_ID, CLIENT_SECRET)  # Required if app client has secret
            },
            ClientId=CLIENT_ID
        )
        print("✅ Cognito login response:", response)
        # If login is successful, return tokens and success
        return {'success': True, 'message': 'Login successful!', 'tokens': response['AuthenticationResult']}

    # Handle specific exceptions
    except client.exceptions.NotAuthorizedException:
        return {'success': False, 'error': 'Incorrect username or password.'}
    except client.exceptions.UserNotConfirmedException:
        return {'success': False, 'error': 'User is not confirmed. Please verify your email.'}
    except Exception as e:
        print("🚨 Unexpected login error:", str(e))
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}


# ✅ Confirm User Function
def confirm_user(email, code):
    try:
        # Generate secret hash
        secret_hash = get_secret_hash(email, CLIENT_ID, CLIENT_SECRET)
        # Call Cognito confirm_sign_up API with confirmation code
        response = client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            SecretHash=secret_hash  # Add secret hash for security
        )
        # If successful, return confirmation success
        return {"success": True, "message": "User confirmed successfully!"}
    except Exception as e:
        # Catch all other errors
        return {"success": False, "error": str(e)}
