from src.modules import *

base = env('base')
tokenKey = []

def getToken():
    header = endpoint()['header']
    header['X-Operator'] = env('XOperator')
    header['X-Key'] = env('XKey')
    response = requests.get(base + env('desc'), headers=header)
    tokenKey.append(response.json())

def gameKey():
    username = endpoint()['creds']
    username['username'] = env('username')
    point = env('key')
    token = tokenKey[0]['data']['token']
    endpoint()['header']['X-token'] = token
    header = endpoint()['header']
    header['X-token'] = token
    response = requests.get(base + point, params=username, headers=header)
    return response.json()['data']['key'], header

def play():
    getToken()
    key = gameKey()
    play = env('play')
    paramKey = endpoint()['URL']
    paramKey['key'] = key[0]
    response = requests.get(base + play, params=paramKey, headers=key[1])
    return response.json()['data']['url']

def addBalance(entry, amount=1100):
    getToken()
    header = endpoint()['header']
    token = tokenKey[0]['data']['token']
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