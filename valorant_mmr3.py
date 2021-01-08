#!/usr/bin/env python3
import http.cookiejar
import getpass
import json
import os
import sys
import time
import urllib.parse
import urllib.request, urllib.error, urllib.parse

map_names = {
    '/Game/Maps/Duality/Duality': 'bind',
    '/Game/Maps/Bonsai/Bonsai': 'split',
    '/Game/Maps/Ascent/Ascent': 'ascent',
    '/Game/Maps/Port/Port': 'icebox',
    '/Game/Maps/Triad/Triad': 'haven',
}

def get_cookies(username, password):
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/',
        'response_type': 'token id_token',
        'scope': 'account openid',
    }
    headers = {
        'Content-Type': 'application/json'
    }

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)
    req = urllib.request.Request('https://auth.riotgames.com/api/v1/authorization', json.dumps(data).encode('utf-8'), headers)
    urllib.request.urlopen(req)
    return cookie_jar


class PutRequest(urllib.request.Request):
    def get_method(self, *args, **kwargs):
        return 'PUT'


def get_access_token(username, password, cookie_jar):
    data = {
      'type': 'auth',
      'username': username,
      'password': password
    }
    headers = {
      'Content-Type': "application/json"
    }
    req = PutRequest('https://auth.riotgames.com/api/v1/authorization', json.dumps(data).encode('utf-8'), headers)
    cookie_jar.add_cookie_header(req)
    res = urllib.request.urlopen(req)
    raw_res = res.read()
    decoded_response = json.loads(raw_res)
    uri = decoded_response['response']['parameters']['uri']
    jsonUri = urllib.parse.parse_qs(uri)
    access_token = jsonUri['https://playvalorant.com/#access_token'][0]

    return access_token

def get_entitlements_token(access_token, cookie_jar):
    headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json'
    }
    req = urllib.request.Request('https://entitlements.auth.riotgames.com/api/token/v1', b'{}', headers)
    cookie_jar.add_cookie_header(req)
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    return data['entitlements_token']

def get_user_info(access_token, cookie_jar):
    headers = {
      'Authorization': 'Bearer ' + access_token
    }
    req = urllib.request.Request('https://auth.riotgames.com/userinfo', b'{}', headers)
    cookie_jar.add_cookie_header(req)
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    user_id = data['sub']
    name = data['acct']['game_name']
    tag  = data['acct']['tag_line']
    game_name = name + ' #' +  tag

    return user_id, game_name

def get_match_history(user_id, access_token, entitlements_token, cookie_jar):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'X-Riot-Entitlements-JWT': entitlements_token,
        'User-Agent': "valelo/0.1"
    }
    RIOT_REGION = os.environ.get('RIOT_REGION') or 'NA'
    url = 'https://pd.%s.a.pvp.net/mmr/v1/players/%s/competitiveupdates?startIndex=0&endIndex=20' % (
        RIOT_REGION, user_id
    )
    req = urllib.request.Request(url, None, headers)
    #cookie_jar.add_cookie_header(req)
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    return data

def show_history(match_data):
    print("Old MMR\tNew MMR\tChange\tMap\tTimestamp\tMovement")
    for match in match_data['Matches']:
        if match['TierAfterUpdate'] == 0 and match['TierBeforeUpdate'] == 0:
            # must be unrated ...
            continue
        if match['MapID'] in map_names:
            map_name = map_names[match['MapID']]
        else:
            map_name = 'Unknown'

        match_timestamp = time.strftime('%Y-%m-%d', time.localtime(match['MatchStartTime']/1000))

        elo_before = match['TierBeforeUpdate'] * 100 + match['TierProgressBeforeUpdate']
        elo_after = match['TierAfterUpdate'] * 100 + match['TierProgressAfterUpdate']
        elo_diff = elo_after - elo_before

        print("%d\t%d\t%d\t%s\t%s\t%s" % (elo_before, elo_after, elo_diff, map_name, match_timestamp, match['CompetitiveMovement']))


def main():
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    cookie_jar = get_cookies(username, password)
    access_token = get_access_token(username, password, cookie_jar)
    entitlements_token = get_entitlements_token(access_token, cookie_jar)
    user_id, handle = get_user_info(access_token, cookie_jar)
    print("Data for: " + handle)
    match_history = get_match_history(user_id, access_token, entitlements_token, cookie_jar)
    show_history(match_history)


if __name__ == '__main__':
    main()
