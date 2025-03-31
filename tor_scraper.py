import requests
import string
import stem
import random
import time
from stem.control import Controller
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import setup_tor

class TorScraper:
    def __init__(self, use_browser=False):
        """
        Initializes the scraper, routing traffic through Tor.
        
        :param use_browser: Whether to use undetected Chrome (default: False).
        """
        self.use_browser = use_browser
        self.tor_socks_proxy = "socks5h://127.0.0.1:9050"
        self.detection = 0
        self.tor_port = 9050
        self.tor_control_port = 9051

        setup_tor.stop_all_tor_processes()
        setup_tor.start_tor_confs()

        self.session = self._new_tor_session()
        

    def poll(self):
        self.detection += 1
        if self.detection >= 5:
            self.rotate_identity()
            self.detection = 0

    def _new_tor_session(self):
        """Creates a new requests session using different Tor circuits."""
        tor_ports = setup_tor.get_open_tor_ports()
        session = requests.Session()
        self.tor_port = random.choice(tor_ports)
        self.tor_control_port = self.tor_port + 1
        print(f"Tor port {self.tor_port} chosen")
        session.proxies = {
            "http": f"socks5h://127.0.0.1:{self.tor_port}",
            "https": f"socks5h://127.0.0.1:{self.tor_port}",
        }
        return session


    def rotate_identity(self):
        """Requests a new identity from Tor via the control port and resets session."""
        try:
            with Controller.from_port(port=self.tor_control_port) as controller:
                controller.authenticate()
                controller.signal("NEWNYM")
            time.sleep(random.uniform(2, 4)) 
            self.session = self._new_tor_session() 
            print("🔄 New Tor identity requested!")
        except Exception as e:
            print(f"❌ Failed to request new identity: {e}")

    def random_cookie(self):
        """Generates a random cookie string."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    def random_accept(self):
        """Randomize the 'accept' header."""
        accept_list = [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "application/json, text/plain, */*",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        ]
        return random.choice(accept_list)

    def random_accept_encoding(self):
        """Randomize the 'accept-encoding' header."""
        encoding_list = ["gzip, deflate, br", "gzip, deflate", "gzip, br"]
        return random.choice(encoding_list)

    def random_accept_language(self):
        """Randomize the 'accept-language' header."""
        language_list = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en;q=0.9"]
        return random.choice(language_list)

    def random_user_agent(self):
        """Randomize the 'user-agent' header."""
        user_agent_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        ]
        return random.choice(user_agent_list)

    def random_sec_ch_ua(self):
        """Randomize the 'sec-ch-ua' header."""
        return '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"'

    def random_sec_ch_ua_mobile(self):
        """Randomize the 'sec-ch-ua-mobile' header."""
        return random.choice(["?0", "?1"])

    def random_sec_ch_ua_platform(self):
        """Randomize the 'sec-ch-ua-platform' header."""
        return random.choice(["macOS", "Windows", "Linux"])

    def random_headers(self):
        """Generate randomized headers."""
        return {
            "Accept": self.random_accept(),
            "Accept-Encoding": self.random_accept_encoding(),
            "Accept-Language": self.random_accept_language(),
            "Cookie": f"guest_id_marketing={self.random_cookie()}; guest_id_ads={self.random_cookie()}",
            "User-Agent": self.random_user_agent(),
            "Sec-CH-UA": self.random_sec_ch_ua(),
            "Sec-CH-UA-Mobile": self.random_sec_ch_ua_mobile(),
            "Sec-CH-UA-Platform": self.random_sec_ch_ua_platform(),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Connection": "keep-alive",
            "DNT": "1"
        }

    def fetch_requests(self, url):
        """
        Fetch a URL using requests routed through Tor.
        
        :param url: The URL to fetch.
        :return: Response text or None if failed.
        """
        headers = self.random_headers()
        self.poll()

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def fetch_browser(self, url):
        """
        Fetch a URL using undetected Chrome routed through Tor.
        
        :param url: The URL to fetch.
        :return: Page source or None if failed.
        """
        chrome_options = Options()
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9050")  # Route Chrome through Tor
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        driver = uc.Chrome(options=chrome_options)

        try:
            driver.get(url)
            page_source = driver.page_source
            return page_source
        except Exception as e:
            print(f"❌ Browser fetch failed: {e}")
            return None
        finally:
            driver.quit()

    def fetch(self, url):
        """
        Fetch a URL using either requests or browser mode.
        
        :param url: The URL to fetch.
        :return: Page source or None if failed.
        """
        if self.use_browser:
            return self.fetch_browser(url)
        return self.fetch_requests(url)