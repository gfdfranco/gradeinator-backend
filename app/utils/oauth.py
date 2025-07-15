from authlib.integrations.flask_client import OAuth


def init_oauth(app):
    """Initializes the OAuth client with Cognito configuration."""
    oauth = OAuth(app)

    # Construct the OIDC metadata URL from your config
    metadata_url = (
        f"https://cognito-idp.{app.config['AWS_COGNITO_REGION']}.amazonaws.com/"
        f"{app.config['AWS_COGNITO_USERPOOL_ID']}/.well-known/openid-configuration"
    )

    # Register the Cognito OIDC client
    oauth.register(
        name='cognito',
        client_id=app.config['AWS_COGNITO_APP_CLIENT_ID'],
        client_secret=app.config['AWS_COGNITO_APP_CLIENT_SECRET'],
        server_metadata_url=metadata_url,
        client_kwargs={
            'scope': 'openid email phone profile'
        }
    )
    return oauth
