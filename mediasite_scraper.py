import requests


gateway_request = requests.session()
gateway_request.headers.update({'User-Agent':'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'})

getway_get_headers = {'Host': 'gateway.sfsu.edu'}
getway_get = gateway_request.get('https://gateway.sfsu.edu/')
print(getway_get.history[0].headers, getway_get.history[0].url)
print(getway_get.history[1].headers, getway_get.history[1].url)
print(getway_get.url)



print(gateway_request.cookies)

print(getway_get.content)

