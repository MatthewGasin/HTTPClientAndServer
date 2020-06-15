import sys, os, time
from socket import *

#URL as argument
argv = sys.argv
URL = argv[1].strip()
host = URL.split(":")[0]
port = URL.split(":")[1].split("/")[0]
file = URL.split(":")[1].split("/")[1]

timeFormat = "%a, %d %h %Y %H:%M:%S GMT"
cacheName = "cache.html"

#create client socket
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((host, int(port)))

request = "GET /" + file + " HTTP/1.1" + "\r\n"
request += host + ":" + port + "\r\n"

#check if cache exists
hasCache = os.path.isfile(cacheName)
if hasCache:
    #cache exists, check if it is up to date
    request += "If-Modified-Since: " + time.strftime(timeFormat, time.gmtime(os.path.getmtime(cacheName))) + "\r\n"

request += "\r\n"

clientSocket.send(request.encode())
response = clientSocket.recv(4096).decode()

#check for 404
if "404" in response.split("\r\n")[0]:
    print("404, file " + file + " not found!")
    exit()
elif "200" in response.split("\r\n")[0]:
    cache = open(cacheName, "w")
    cache.write(response.split("\r\n")[6])
    cache.close()

#cache is now def up to date, print it!
cache = open(cacheName, "r")
print(cache.read())
cache.close()
clientSocket.close()
