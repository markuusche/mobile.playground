from src.modules import *

def getToken():
    header = {}
    header['X-Operator'] = env('XOp')
    header['X-Key'] = env('Xkey')
    response = requests.get(env('base') + env('desc'), headers=header)
    return response.json()

def gameKey():
    fetch = getToken()
    username = {'username': env('username')}
    token = fetch['data']['token']
    header = {'X-token': token}
    response = requests.get(env('base') + env('key'), \
    params=username, headers=header)
    return response.json()['data']['key'], header

def play():
    key = gameKey()
    paramKey = {'key': key[0]}
    response = requests.get(env('base') + env('play'), \
    params=paramKey, headers=key[1])
    return response.json()['data']['url']

def addBalance(entry, amount):
    fetch = getToken()
    token = fetch['data']['token']
    header = {'X-token': token}
    body = {}
    body['username'] = env('username')
    body['balance'] = amount
    body['action'] = entry
    body['transferId'] = fake.passport_number()
    response = requests.post(env('base') + env('balance'), \
    headers=header, json=body)
    assert response.status_code == 200
    return response.json()['data']['balance']
