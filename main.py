"""
lets users input an artist name and we return a list of their top ten most popular songs
use flask to setup the website
use flask and setup a frontend and create an enter field for the artist and show the result in a list <ul>
"""
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from flask import Flask, render_template, request 

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
app = Flask(__name__)

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64, 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1" # get the top artist from the search result
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("no artist with this name exists")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id, countryID):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country={countryID}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


token = get_token()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/top", methods = ["GET", "POST"])
def artists():  
    if request.method == "POST":
        artist_name = request.form.get("fname")
        locationID = request.form.get("locate")
        
        result = search_for_artist(token, artist_name)
        artist_id = result["id"]
        songs = get_songs_by_artist(token, artist_id, locationID)

        popularSongs = {}
        for i, song in enumerate(songs):
            popularSongs[f"{song['name']}"] = f"{song['popularity']}"

        return render_template("results.html", popularSongs=popularSongs)

    return render_template("top.html") 

if __name__ == "__main__":
    app.run()