import re
import requests

from bs4 import BeautifulSoup

class Client:
    def __init__(self, username: str, password: str, auto_login=True):
        self.auth_response: requests.Response = None
        self.username = username
        self.password = password
        self.url = "https://siac.ufba.br"
        self.paths = {
            "login": "/SiacWWW/LogonSubmit.do",
            "get_history": "/SiacWWW/ConsultarComponentesCurricularesCursados.do"
        }
        if auto_login:
            self.login()

    def get_url(self, path):
        return self.url + self.paths.get(path)

    def get_headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://siac.ufba.br',
            'Pragma': 'no-cache',
            'Referer': 'https://siac.ufba.br/SiacWWW/Logoff.do',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"'
        }

    def login(self, username=None, password=None):
        self.username = username or self.username
        self.password = password or self.password
        result = requests.post(self.get_url("login"), headers=self.get_headers(), data={
            'cpf': self.username,
            'senha': self.password,
            'x': '28',
            'y': '11'
        })
        if result.status_code == 200:
            self.auth_response = result
            return self
        else:
            raise Exception("Login Failed!")

    def get_history(self):
        semester = ''
        history = []
        response = requests.get(self.get_url("get_history"), cookies=self.auth_response.cookies)

        if response.status_code != 200:
            raise Exception('Failed to Get History')

        rows = (BeautifulSoup(response.content, 'html.parser')
                .find('table', {'class': 'corpoHistorico'})
                .find_all('tr'))

        for row in rows:
            cells = row.find_all('td')

            # A Line with Correct Size on Table ( Current the Normal Size is 8 )
            if len(cells) != 8:
                continue

            # Check if the Line Contains a Current Semester to Change the Context
            if cells[0].b is not None:
                semester = cells[0].b.text.strip()

            # Check if The Line Contais Valid Information to Course
            if len(cells[1].text.strip()) > 3:
                history.append({
                    "semester": semester,
                    "code": cells[1].text.strip(),
                    "title": cells[2].text.strip(),
                    "score": cells[6].text.strip(),
                    "status": cells[7].text.strip(),
                })

        return history