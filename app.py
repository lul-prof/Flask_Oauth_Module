from flask import Flask, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

#OAuth Configuration
oauth = OAuth(app)

GITHUB_CLIENT_ID=os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET=os.environ.get('GITHUB_CLIENT_SECRET')
ACCESS_TOKEN_URL=os.environ.get('ACCESS_TOKEN_URL')
AUTHORIZE_URL=os.environ.get('AUTHORIZATION_BASE_URL')
API_BASE_URL=os.environ.get('API_BASE_URL')

GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET')
SERVER_METADATA_URL=os.environ.get('SERVER_METADATA_URL')


#GitHub OAuth Setup
github = oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url=ACCESS_TOKEN_URL,
    access_token_params=None,
    authorize_url=AUTHORIZE_URL,
    authorize_params=None,
    api_base_url=API_BASE_URL,
    client_kwargs={'scope': 'user:email'},
)

#Google OAuth Setup
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=SERVER_METADATA_URL,
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/')
def index():
    user = session.get('user')
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Login</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            .btn { display: inline-block; padding: 10px 20px; margin: 10px; 
                   background: #0366d6; color: white; text-decoration: none; 
                   border-radius: 5px; }
            .btn-google { background: #4285f4; }
            .user-info { background: #f6f8fa; padding: 20px; border-radius: 5px; 
                        margin: 20px 0; }
            .logout { background: #d73a49; }
        </style>
    </head>
    <body>
        <h1>Flask OAuth Module</h1>
    '''
    
    if user:
        html += f'''
        <div class="user-info">
            <h2>Logged in as: {user.get('name', 'Unknown')}</h2>
            <p><strong>Email:</strong> {user.get('email', 'N/A')}</p>
            <p><strong>Provider:</strong> {user.get('provider', 'N/A')}</p>
            <pre>{user}</pre>
        </div>
        <a href="/logout" class="btn logout">Logout</a>
        '''
    else:
        html += '''
        <p>Choose a provider to login:</p>
        <a href="/login/github" class="btn">Login with GitHub</a>
        <a href="/login/google" class="btn btn-google">Login with Google</a>
        '''

    return html

# GitHub OAuth Routes
@app.route('/login/github')
def github_login():
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/login/github/authorized')
def github_authorize():
    token = github.authorize_access_token()
    resp = github.get('user', token=token)
    user_info = resp.json()
    
    session['user'] = {
        'provider': 'github',
        'name': user_info.get('name') or user_info.get('login'),
        'email': user_info.get('email'),
        'id': user_info.get('id'),
        'avatar': user_info.get('avatar_url'),
    }
    return redirect('/')

# Google OAuth Routes
@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorized')
def google_authorize():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    session['user'] = {
        'provider': 'google',
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'id': user_info.get('sub'),
        'avatar': user_info.get('picture'),
    }
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)