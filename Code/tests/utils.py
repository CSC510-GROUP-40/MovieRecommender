
import pytest
from unittest.mock import MagicMock
import logging
from flask import session
import sys
sys.path.append('../recommenderapp')
from recommenderapp.app import app, db, User, login_user

class OAuth:
    def prepare_token_request(
            grant_type, body='', include_client_id=True, code_verifier=None, **kwargs):
        """mock prepreate the tokens

        Args:
            grant_type (_type_): grant type
            body (str, optional): body. Defaults to ''.
            include_client_id (bool, optional): id of client. Defaults to True.
            code_verifier (_type_, optional): code verify. Defaults to None.

        Returns:
            _type_: mockparam1
        """
        return (
            "something to do ",  # Return the original token endpoint
            {"Content-Type": "application/x-www-form-urlencoded"},  # Headers
            f"code=4223"  # Body of the request
        )
    
    def parse_request_body_response(a, b):
        """parse response of body

        Args:
            a (_type_): mockparam1
            b (_type_): mockparam2
        """
        pass

    def add_token(a, b):
        """adds token to  payload

        Args:
            a (_type_): mockparam1
            b (_type_): mockparam2

        Returns:
            _type_: _description_
        """
        return ('uri', {'headers': 'value'}, "body")

    def prepare_request_uri(self, uri, redirect_uri=None, scope=None,
                            state=None, code_challenge=None, code_challenge_method='plain', **kwargs):
        """prepare the request URI

        Args:
            uri (_type_): uri
            redirect_uri (_type_, optional): redirect uri. Defaults to None.
            scope (_type_, optional): scope. Defaults to None.
            state (_type_, optional): state. Defaults to None.
            code_challenge (_type_, optional): code challenge. Defaults to None.
            code_challenge_method (str, optional): code challenge method. Defaults to 'plain'.

        Returns:
            _type_: _description_
        """
        return "/"

   
@pytest.fixture
def client():
    """Create a test client and initialize database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    oauthclient = OAuth()
    app.oauthclient = oauthclient
   
    app.app_context().push()
    client = app.test_client()
    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()