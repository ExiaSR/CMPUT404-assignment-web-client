#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return self.body


class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        lines = data.splitlines()
        first_line = lines[0].split(' ')
        return int(first_line[1])

    def get_headers(self, data):
        data = data.split('\r\n\r\n')
        headers = data[0]
        return headers

    def get_body(self, data):
        lines = data.splitlines()

        cnt = 0
        for line in lines:
            cnt += 1
            if not line:
                break

        if cnt+1 <= len(lines):
            return ''.join(lines[cnt:])
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    def _parse_url(self, url):
        result = urlparse(url)

        protocol = result.scheme
        path = result.path
        hostname = result.hostname
        port = result.port
        querystring = result.query

        if not path:
            path = '/'

        if querystring:
            path += '?{}'.format(querystring)

        if not port:
            if protocol == 'http':
                port = 80
            elif protocol == 'https':
                raise ValueError('TLS Not Supported')
            else:
                raise ValueError('Unexpected Protocol')

        return hostname, port, path

    # read everything from the socket
    def recvall(self, sock):
        buffer = b""
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer += part
            else:
                done = not part
        return buffer.decode('utf-8')

    def _build_http_request(self, method, path='/', body=None, headers={}):
        payload = '{} {} HTTP/1.1\r\n'.format(method, path)

        for key, value in headers.items():
            payload += '{}: {}\r\n'.format(key, value)

        payload += '\r\n'

        if body:
            payload += body

        return payload

    def GET(self, url, args=None):
        host, port, path = self._parse_url(url)
        headers = {
            'Host': '{}'.format(host),
            'Accept': '*/*',
            'User-Agent': 'curl/7.54.0'
        }

        request = self._build_http_request('GET', path, headers=headers)

        self.connect(host, port)
        self.sendall(request)

        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)

        print(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self._parse_url(url)

        headers = {
            'Host': '{}'.format(host),
            'Accept': '*/*',
            'Content-Length': 0
        }

        if args:
            args = urlencode(args)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = len(args)

        request = self._build_http_request('POST', path, headers=headers, body=args)

        self.connect(host, port)
        self.sendall(request)

        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)

        print(data)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    print(sys.argv)
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
