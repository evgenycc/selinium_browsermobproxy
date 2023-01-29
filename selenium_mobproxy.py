import os
import time
from pathlib import Path
from platform import system
from urllib.parse import urlparse

import validators
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

if system() == "Windows":
    exec_path = str(Path.cwd() / 'driver' / 'chromedriver.exe')
elif system() == "Linux":
    exec_path = str(Path.cwd() / 'driver' / 'chromedriver')
serv_path = str(Path.cwd() / 'driver' / 'browsermob-proxy-2.1.4' / 'bin' / 'browsermob-proxy')


class SelenProxy:
    def __init__(self, url: str, har: str, driver_path: str, ser_path: str):
        self.url = url
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument("--ignore-certificate-errors")
        self.server = Server(ser_path, options={'port': 8090})
        self.server.start()
        self.proxy = self.server.create_proxy(params={"trustAllServers": "true"})
        self.options.add_argument("--proxy-server={0}".format(self.proxy.proxy))
        self.driver = webdriver.Chrome(options=self.options, service=Service(log_path=os.devnull,
                                                                             executable_path=driver_path))
        self.proxy.new_har(har)

    def driver_get(self) -> (list, bool):
        try:
            url_list = []
            self.driver.get(self.url)
            time.sleep(10)
            for item in self.proxy.har['log']['entries']:
                if url := item['request'].get('url'):
                    url_list.append(url)
            self.driver.quit()
            self.server.stop()
            return url_list if url_list else False
        except Exception:
            return False


def main():
    # http://2tv.one/1hd
    global exec_path, serv_path

    url_input = input("Введите страницу для перехвата: ")
    if validators.url(url_input):
        print("\nЗапуск сервера. Загрузка страницы")
        driver = SelenProxy(url=url_input, har=f'{urlparse(url_input).hostname}/', driver_path=exec_path,
                            ser_path=serv_path)
        if urls := driver.driver_get():
            print(f"\nНайдены ссылки\n{'-'*25}")
            for url in urls:
                if Path(str(urlparse(url).path.split("/")[-1])).suffix in [".m3u", ".m3u8", ".mpd"]:
                    print(url)
        else:
            print(f"\nСсылок не найдено. Список пуст\n{'-'*25}")
    else:
        print(f"\nВведенная строка не содержит ссылку\n{'-'*25}")


if __name__ == "__main__":
    main()
