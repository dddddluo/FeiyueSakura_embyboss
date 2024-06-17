import requests
import json
from bot import config, moviepilot_access_token, moviepilot_url, moviepilot_username, moviepilot_password,save_config
TIMEOUT = 15

def do_request(request):
    error_count = 0
    while error_count < 3:
        try:
            response = requests.request(
                method=request['method'], url=request['url'], headers=request['headers'], data=request.get('data', None), timeout=TIMEOUT)
            if response.status_code == 401:  # Unauthorized
                print("Token expired, attempting to re-login.")
                login()
                request['headers']['Authorization'] = moviepilot_access_token
                response = requests.request(
                    method=request['method'], url=request['url'], headers=request['headers'], data=request.get('data', None), timeout=TIMEOUT)
            return response
        except Exception as e:
            error_count += 1
            print(f"Error: {e}, Retrying...")
    return None


def login():
    url = f"{moviepilot_url}/api/v1/login/access-token"
    payload = f"username={moviepilot_username}&password={moviepilot_password}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers, timeout=TIMEOUT)
    result = response.json()
    if 'access_token' in result:
        config.moviepilot_access_token = result['token_type'] + ' ' + result['access_token']
        save_config()
        print("Login MP successful, token stored")
    else:
        print("Login MP failed:", result)


def site():
    url = f"{moviepilot_url}/api/v1/site/"
    headers = {'Authorization': moviepilot_access_token}
    request = {'method': 'GET', 'url': url, 'headers': headers}
    response = do_request(request)
    if response.status_code == 200:
        data = response.json()
        print("获取站点信息成功!")
        return data
    else:
        print("获取站点信息失败!")
        return []


def search(title):
    url = f"{moviepilot_url}/api/v1/search/title?keyword={title}"
    headers = {'Authorization': moviepilot_access_token}
    request = {'method': 'GET', 'url': url, 'headers': headers}
    response = do_request(request)
    data = response.json()
    results = []
    if data.get("success", False):
        data = data["data"]
        for item in data:
            print(data)
            meta_info = item.get("meta_info", {})
            torrent_info = item.get("torrent_info", {})
            result = {
                "title": meta_info.get("title", ""),
                "year": meta_info.get("year", ""),
                "type": meta_info.get("type", ""),
                "resource_pix": meta_info.get("resource_pix", ""),
                "video_encode": meta_info.get("video_encode", ""),
                "audio_encode": meta_info.get("audio_encode", ""),
                "resource_team": meta_info.get("resource_team", ""),
                "seeders": torrent_info.get("seeders", ""),
                "size": torrent_info.get("size", ""),
                "labels": torrent_info.get("labels", ""),
                "description": torrent_info.get("description", ""),
                "torrent_info": torrent_info,
            }
            results.append(result)
    results.sort(key=lambda x: int(x["seeders"]), reverse=True)
    if len(results) > 10:
        results = results[:10]
    else:
        results = results[:-1]
    return results


def subscribe(param):
    url = f"{moviepilot_url}/api/v1/media/subscribe"
    headers = {'Content-Type': 'application/json',
               'Authorization': moviepilot_access_token}
    jsonData = json.dumps(param)
    request = {'method': 'POST', 'url': url,
               'headers': headers, 'data': jsonData}
    response = do_request(request)
    result = response.json()
    if result.get("success", False):
        print("Subscription successful, ID:", result["data"]["id"])
    else:
        print("Subscription failed:", result.get("message"))
