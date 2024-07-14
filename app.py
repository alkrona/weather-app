import requests
import pandas as pd
import json
from github import Auth, Github, GithubException
def get_data():
    api_key = '2bfadace9e23a0c08c0027cdf60fd2a2'
    latitude = -37.92512
    longitude = 145.11429
    units = 'metric'

    # Construct the URL
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    url = f"{base_url}?lat={latitude}&lon={longitude}&appid={api_key}&units={units}"

    # Make the API call
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
    return data
def clean_data(data):
    df = pd.json_normalize(data=data['list'])
    df['weather_main'] = df['weather'].apply(lambda x: x[0]['main'] if x else None)
    df['weather_description'] = df['weather'].apply(lambda x: x[0]['description'] if x else None)
    df['weather_id'] = df['weather'].apply(lambda x: x[0]['id'] if x else None)
    df['weather_icon'] = df['weather'].apply(lambda x: x[0]['icon' if x else None])
    df.loc[df['weather_icon'].str.contains('n'), 'weather_id'] *= 10
    df.loc[df['weather_icon'].str.contains('n'), 'weather_id'] += 1
    df = df.drop('weather', axis=1)
    
    df.to_csv("data.csv")
def sent_data(file_path):
        # Authentication is defined via github.Auth
    # using an access token
    auth = Auth.Token("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")

    # Public Web Github
    g = Github(auth=auth)
    repo = g.get_repo("alkrona/weather-app")

    try:
        contents = repo.get_contents("data.csv", ref="main")
        sha = contents.sha
    except GithubException as e:
        if e.status == 404:
            # File doesn't exist, so we'll create it
            sha = None
        else:
            # Some other error occurred
            raise

    # Read the contents of ff.csv
    with open(file_path, 'r') as file:
        csv_content = file.read()

    # Convert the content to bytes
    csv_bytes = csv_content.encode('utf-8')

    if sha:
        # File exists, so we update it
        repo.update_file("data.csv", "Updating data.csv with contents from ff.csv", csv_bytes, sha, branch="main")

    else:
        # File doesn't exist, so we create it
        repo.create_file("data.csv", "Creating data.csv with contents from ff.csv", csv_bytes, branch="main")

    g.close()

if __name__ =='__main__':
    data = get_data()
    clean_data(data)
    sent_data('data.csv')
        
    