from src.modules import *

base = env('base')

def getToken():
    header = endpoint()['header']
    header['X-Operator'] = env('XOperator')
    header['X-Key'] = env('XKey')
    response = requests.get(base + env('desc'), headers=header)
    return response.json()

def gameKey():
    fetch = getToken()
    username = endpoint()['creds']
    username['username'] = env('username')
    point = env('key')
    token = fetch['data']['token']
    endpoint()['header']['X-token'] = token
    header = endpoint()['header']
    header['X-token'] = token
    response = requests.get(base + point, params=username, headers=header)
    return response.json()['data']['key'], header

def play():
    key = gameKey()
    play = env('play')
    paramKey = endpoint()['URL']
    paramKey['key'] = key[0]
    response = requests.get(base + play, params=paramKey, headers=key[1])
    return response.json()['data']['url']

def addBalance(entry, amount=1191.78):
    fetch = getToken()
    header = endpoint()['header']
    token = fetch['data']['token']
    header['X-token'] = token
    coin = env('balance')
    body = {
        "username": f"{env('username')}",
        "balance": f'{amount}',
        "action": f"{entry}",
        "transferId": f"{fake.passport_number()}xyz"
    }
    response = requests.post(base + coin, headers=header, json=body)
    assert response.status_code == 200
    return response.json()['data']['balance']