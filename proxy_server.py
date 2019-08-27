import socketserver
import http.server
import urllib.request
import re
from bs4 import BeautifulSoup

PORT = 8233


class Proxy(http.server.SimpleHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        site_url = 'https://habr.com{}'.format(self.path)
        symbol = '™'
        self._set_headers()

        with urllib.request.urlopen(site_url) as url:
            content = url.read()
            soup = BeautifulSoup(content, 'html.parser')
            article = soup.find("div", {"class": "post__text-html"})

            if article is not None:
                for idx, child in enumerate(article.children):
                    if type(child).__name__ == 'NavigableString':
                        article.contents[idx].replaceWith(re.sub(r'\b(\w{6})\b', lambda m: m.group(0) + symbol, child))
                    else:
                        if child.name in ['pre', 'br', 'code', 'img']:
                            continue

                        if child.name == 'a':
                            child['href'] = '#'

                        child.string = re.sub(r'\b(\w{6})\b', lambda m: m.group(0) + symbol, child.text)
                        article.contents[idx].replaceWith(child)
            self.wfile.write(bytes(str(soup), 'utf-8'))

    def do_HEAD(self):
        self._set_headers()


proxy = socketserver.ThreadingTCPServer(('localhost', PORT), Proxy)
print("serving at port", PORT)
proxy.serve_forever()
