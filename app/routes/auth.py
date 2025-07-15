from flask import redirect, url_for, session, current_app, request
from flask_restx import Namespace, Resource
# Create the namespace for authentication
api = Namespace('auth', description='Authentication related operations')


@api.route('/login')
class Login(Resource):
    @api.doc(description="Redirects user to Cognito Hosted UI for login.")
    def get(self):
        """Initiate the OIDC login flow."""
        # Get the oauth object attached to the app in create_app
        oauth = current_app.oauth.cognito

        # Use url_for to generate the correct callback URL with API prefix
        callback_url = url_for('auth_callback', _external=True)
        return oauth.authorize_redirect(callback_url)


@api.route('/callback')
class Callback(Resource):
    @api.doc(description="Handles the callback from Cognito after a successful login.")
    def get(self):
        """Process the OIDC callback and create a session."""
        try:
            oauth = current_app.oauth.cognito
            token = oauth.authorize_access_token()

            # Store user info in the session
            session['user'] = token.get('userinfo', {})

            # Return a success response with the redirect URL
            return {
                'message': 'Login successful',
                'user': token.get('userinfo', {}),
                'redirect_url': url_for('auth_profile', _external=True)
            }, 200
        except Exception as e:
            # Handle OAuth errors
            return {
                'error': 'Authentication failed',
                'message': str(e)
            }, 400


@api.route('/logout')
class Logout(Resource):
    @api.doc(description="Logs the user out from the application and Cognito.")
    def get(self):
        """Initiate the OIDC logout flow."""
        # Clear the local user session
        session.pop('user', None)
        session.pop('oauth_state', None)

        # Get config values
        cognito_domain = current_app.config['AWS_COGNITO_DOMAIN']
        client_id = current_app.config['AWS_COGNITO_APP_CLIENT_ID']

        # Use the profile endpoint as the logout redirect destination
        logout_uri = url_for('auth_profile', _external=True)

        # Clean the domain to remove any existing protocol
        cleaned_domain = cognito_domain.replace('https://', '').replace('http://', '')

        # Construct the final logout URL
        logout_url = (f"https://{cleaned_domain}/logout?"
                      f"client_id={client_id}&"
                      f"logout_uri={logout_uri}")

        # Redirect the user's browser to the Cognito logout page
        return redirect(logout_url)


@api.route('/profile')
class Profile(Resource):
    @api.doc(description="Get the current logged-in user's profile information.")
    def get(self):
        """Returns user data if a session exists."""
        user = session.get('user')
        if user:
            return user, 200

        api.abort(401, "User is not authenticated.")
