import requests
from dotenv import dotenv_values

BASEURL = dotenv_values('.env')['LEAGUE_BASE_URL']
LEAGUE_API_KEY = dotenv_values('.env')['LEAGUE_API_KEY']
HEADER = {
    "X-Riot-Token": LEAGUE_API_KEY
}

def check_league_api():
    url = f'{BASEURL}/lol/status/v4/platform-data'
    response = requests.get(url, headers= HEADER)
    if response.status_code == 200:
        return 'API key is valid'
    elif response.status_code == 403:
        return False
        
result = check_league_api()
if result == False:
    print('API Key is no longer valid. Place a new League API key in ".env" file')
    quit()
else:
    print(result)

async def get_summoner_info(summoner_name: str):
    url = f'{BASEURL}/lol/summoner/v4/summoners/by-name/{summoner_name}'
    response = requests.get(url, headers=HEADER)
    if response.status_code == 404:
        return f'WOAH THERE BESSIE\n{summoner_name} not found'
    elif response.status_code == 200:
        return response.json()
    else:
        return f'Response: {response.status_code}\nSomething went wrong'
