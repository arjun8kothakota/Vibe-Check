import requests

import os
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from urllib.parse import urlencode

class SpotifyClient():
    access_token = None
    access_token_did_expire = True
    access_token_expire_time = datetime.now()
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self):
        """
        Method returns the updated access token. If the time is expired for the existing access token, a new one is generated by making a call to perform_auth().

        Args: None
        Return: (str) The access token.
        """
        token = self.access_token
        expire_time = self.access_token_expire_time
        curr_time = datetime.now()

        if expire_time < curr_time or token is None:
            self.perform_auth()
            return self.get_access_token()
        
        return token

    def get_album(self, lookup_id):
        return self.get_resource(lookup_id=lookup_id, resource_type="albums")

    def get_artist(self, lookup_id):
        return self.get_resource(lookup_id=lookup_id, resource_type="artists")

    def get_client_credentials(self):
        """
        Args: None
        Return: (b64encode) Returns a base64 encoded string of the client_id and client_secret.
        """
        if self.client_id is None or self.client_secret is None:
            raise ValueError("You have to set the client ID and client SECRET")

        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_resource(self, lookup_id, resource_type, version="v1"):
        """
        Gives information about a particular type of "resource". This may be an artist, album, track, or any other Spotify endpoint reference.

        Args:
            -> lookup_id (str): The id associated with a particular resource.
            -> resource_type (str): May be artist, album, track, etc.
            -> version (str): Version of the API
        Return: (dict) Contains information about the resource being returned. Example: name and genres.
        """
        result = {}
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_headers()
        request = requests.get(endpoint, headers=headers)

        if request.status_code in range(200, 299):
            result = request.json()
        
        return result

    def get_resource_headers(self):
        """
        Returns headers used to make a GET request to acces information about particular resources.

        Args: None
        Return: (dict) Contains "Authorization" as the key and access token as the value. The token associated with the access token is "Bearer".
        """
        return {
            "Authorization": f"Bearer {self.get_access_token()}"
        }

    def get_token_data(self):
        """
        The token header contains the grant_type, telling Spotify what data it should exactly give us.

        Args: None
        Return: (dict) Contains a key "grant_type" which has the value of the authorization flow that is being used. In this case it is "client_credentials".
        """
        return {
            "grant_type": "client_credentials"
        }
    
    def get_token_headers(self):
        """
        Used to provide auth in making a POST request to the API. Value uses the token "Basic".

        Args: None
        Return: (dict) Contains "Authorization" as the key with the client credentials in Base64 as the value.
        """
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_track(self, lookup_id):
        return self.get_resource(lookup_id=lookup_id, resource_type="tracks")
    
    def perform_auth(self):
        """
        This method is used to authorize or authenticate a client. Anytime a call is made to the API, a POST request is made sharing the token data and token headers. The access token and the expiration time for a particular access token are updated in this method and referenced in other methods. (FYI I have a vague understanding of this method so I may be wrong) - Barjun.

        Args: None
        Return: None
        """
        request = requests.post(
            url=self.token_url,
            data=self.get_token_data(),
            headers=self.get_token_headers()
        )

        # If not a valid status code
        if request.status_code  not in range(200, 299):
            raise ValueError("Authentication Failed")
        
        response = request.json()
        curr_time = datetime.now()
        self.access_token = response['access_token']
        # seconds after which access token expires
        expires_in = response['expires_in'] 
        self.access_token_expire_time = curr_time + timedelta(seconds=expires_in)
        self.access_token_did_expire = self.access_token_expire_time < curr_time
    
    def search(self, query, search_type):
        """
        Information about an artist, album, track, etc. are returned based on the search query and the search type.

        Args:
            -> query (str): Anything that the user enters (hopefully something related to music).
            -> search_type (str): Can be "artist", "album", "track", or any other endpoint reference.
        Return: (dict) Contains result(s) from the search and provides information about the artist, album, or track.
        """
        result = {}
        headers = self.get_resource_headers()
        endpoint = "https://api.spotify.com/v1/search"
        response = urlencode({"q": query, "type": search_type.lower()})
        lookup_url = f"{endpoint}?{response}"
        request = requests.get(lookup_url, headers=headers)

        if request.status_code in range(200, 299):
            result = request.json()
        
        return result

if __name__ == '__main__':
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    client = SpotifyClient(client_id, client_secret)

    print(client.search(query="Stitches", search_type="Track"))
    print(client.get_album("41zMFsCjcGenYKVJYUXU2n"))