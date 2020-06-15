import os, sys, time, datetime
from socket import *

#IP and port as arguments
argv = sys.argv
host = argv[1]
port = int(argv[2])

#start the server up
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.listen(1)
print('The server is ready to receive on port: ' + str(port))

timeFormat = "%a, %d %h %Y %H:%M:%S GMT"

noCache = "nevereverforneverever"

while True:
    conn, address = serverSocket.accept()
    request = conn.recv(4096).decode().strip()
    date = datetime.datetime.now(datetime.timezone.utc).strftime(timeFormat)

    #server only handles GET requests
    if request.split(" ")[0] != "GET":
        print("ignoring request, only GET is allowed!")
        continue

    #only header to look out for is if modified since
    header = "If-Modified-Since:".lower();
    lastModified = noCache

    #retrieve data from request
    for line in request.split("\r\n"):
        for word in line.split(" "):
            if word[0] == "/":
                file = word.replace("/", "")
            elif header in word.lower():
                lastModified = line[len(header):].strip()

    #three possibilities, 404, 200, or 304
    #404
    if not os.path.isfile(file):
        response = "HTTP/1.1 404 Not Found\r\n"
        response += "Date: " + date + "\r\n"
        response += "\r\n"
        print("responding with 404")
    else:
        fileLastModified = time.strftime(timeFormat, time.gmtime(os.path.getmtime(file)))
        #304
        if fileLastModified < lastModified and lastModified != noCache:
            response = "HTTP/1.1 304 Not Modified\r\n"
            response += "Date: " + date + "\r\n"
            response += "\r\n"
            print("responding with 304")
        #200
        else:
            #taking the html out of the html
            body = open(file, 'r', encoding='utf-8').read()
            innerHTML = ""
            for line in open(file, 'r', encoding='utf-8').read().split('\n'):
                if "<p class=\"p1\">" in line:
                    innerHTML += line.replace("<p class=\"p1\">", "").replace("</p>", "").replace("&lt;", "<").replace("&gt;", ">")


            response = "HTTP/1.1 200 OK\r\n"
            response += "Date: " + date + "\r\n"
            response += "Last-Modified: " + fileLastModified + "\r\n"
            response += "Content-Length:" + "\r\n"
            response += "Content-Type: text/html; charset=UTF-8" + "\r\n"
            response += "\r\n"
            response += innerHTML
            print("responding with 200")

    conn.send(response.encode())
    conn.close()