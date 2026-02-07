from curl_cffi.requests import AsyncSession
from fake_useragent import FakeUserAgent
from http.cookies import SimpleCookie
from eth_account import Account
from dotenv import load_dotenv
from datetime import datetime
from colorama import *
import asyncio, random, secrets, string, pytz, sys, re, os

load_dotenv()

wib = pytz.timezone('Asia/Jakarta')

class Diamante:
    def __init__(self) -> None:
        self.API_URL = {
            "campaign": "https://campapi.diamante.io/api/v1",
            "explorer": "https://sentinel.diamante.io/#/tx/",
        }

        self.TRANSFER_COUNT = int(os.getenv("TRANSFER_COUNT") or "10")
        self.TRANSFER_AMOUNT = int(os.getenv("TRANSFER_AMOUNT") or "1")
        self.TRANSFER_FEE = 0.001

        self.USE_PROXY = False
        self.ROTATE_PROXY = False

        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.accounts = {}
        
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Diamante {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.txt"
        try:
            with open(filename, 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
            return None
        
    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"
    
    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"

        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)

        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]

        return proxy_url
    
    def initialize_headers(self, address: str):
        if address not in self.HEADERS:

            user_agent = FakeUserAgent(
                browsers=["chrome"], os="windows"
            ).random

            self.HEADERS[address] = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Access-Token": "key",
                "Cache-Control": "no-cache",
                "Origin": "https://campaign.diamante.io",
                "Pragma": "no-cache",
                "Referer": "https://campaign.diamante.io/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": user_agent
            }

        return self.HEADERS[address].copy()
    
    def generate_address(self, private_key: str):
        try:
            acc = Account.from_key(private_key)
            address = acc.address
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    def generate_random_recipient(self):
        return "0x" + secrets.token_hex(20)
        
    def generate_device_id(self):
        hex_chars = string.hexdigits.lower()[:16]
        random_hex = ''.join(secrets.choice(hex_chars) for _ in range(4))
        return f"DEV{random_hex.upper()}"
    
    def generate_payload(self, address: str):
        try:
            return {
                "address": address,
                "deviceId": self.accounts[address]["deviceId"],
                "deviceSource": "web_app",
                "deviceType": "Windows",
                "browser": "Chrome",
                "ipAddress": "0.0.0.0",
                "latitude": 12.9715987,
                "longitude": 77.5945627,
                "countryCode": "Unknown",
                "country": "Unknown",
                "continent": "Unknown",
                "continentCode": "Unknown",
                "region": "Unknown",
                "regionCode": "Unknown",
                "city": "Unknown"
            }
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    async def print_timer(self, min_delay, max_delay):
        for remaining in range(random.randint(min_delay, max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Prepare Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

    def ensure_ok(self, response):
        if response.status_code >= 400:
            error_text = response.text
            raise Exception(f"HTTP {response.status_code}: {error_text}")
    
    async def check_connection(self, proxy_url=None):
        url = "https://api.ipify.org?format=json"

        proxies = {
            "http": proxy_url, "https": proxy_url
        } if proxy_url else None
        try:
            async with AsyncSession(proxies=proxies, timeout=30, impersonate="chrome120") as session:
                response = await session.get(url=url)
                self.ensure_ok(response)
                return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def connect_wallet(self, address: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['campaign']}/user/connect-wallet"
        
        for attempt in range(retries):
            proxies = {
                "http": proxy_url, "https": proxy_url
            } if proxy_url else None
            try:
                headers = self.initialize_headers(address)
                headers["Content-Type"] = "application/json"
                payload = self.generate_payload(address)

                async with AsyncSession(proxies=proxies, timeout=120, impersonate="chrome120") as session:
                    response = await session.post(url=url, headers=headers, json=payload)
                    self.ensure_ok(response)

                    raw_cookies = response.headers.get_list('Set-Cookie', [])
                    if raw_cookies:
                        cookie = SimpleCookie()
                        cookie.load("\n".join(raw_cookies))
                        cookie_string = "; ".join([f"{key}={morsel.value}" for key, morsel in cookie.items()])
                        self.accounts[address]["accessToken"] = cookie_string

                        return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def get_user_status(self, address: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['campaign']}/auth/get-user-status/{self.accounts[address]['userId']}"
        
        for attempt in range(retries):
            proxies = {
                "http": proxy_url, "https": proxy_url
            } if proxy_url else None
            try:
                headers = self.initialize_headers(address)
                headers["Cookie"] = self.accounts[address]["accessToken"]

                async with AsyncSession(proxies=proxies, timeout=120, impersonate="chrome120") as session:
                    response = await session.get(url=url, headers=headers)
                    self.ensure_ok(response)
                    return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Stats   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def fund_wallet(self, address: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['campaign']}/transaction/fund-wallet/{self.accounts[address]['userId']}"
        
        for attempt in range(retries):
            proxies = {
                "http": proxy_url, "https": proxy_url
            } if proxy_url else None
            try:
                headers = self.initialize_headers(address)
                headers["Cookie"] = self.accounts[address]["accessToken"]

                async with AsyncSession(proxies=proxies, timeout=120, impersonate="chrome120") as session:
                    response = await session.get(url=url, headers=headers)
                    self.ensure_ok(response)
                    return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Request Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def get_balance(self, address: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['campaign']}/transaction/get-balance/{self.accounts[address]['userId']}"
        
        for attempt in range(retries):
            proxies = {
                "http": proxy_url, "https": proxy_url
            } if proxy_url else None
            try:
                headers = self.initialize_headers(address)
                headers["Cookie"] = self.accounts[address]["accessToken"]

                async with AsyncSession(proxies=proxies, timeout=120, impersonate="chrome120") as session:
                    response = await session.get(url=url, headers=headers)
                    self.ensure_ok(response)
                    return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch DIAM Token Balance {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def perform_transfer(self, address: str, recipient: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['campaign']}/transaction/transfer"
        
        for attempt in range(retries):
            proxies = {
                "http": proxy_url, "https": proxy_url
            } if proxy_url else None
            try:
                headers = self.initialize_headers(address)
                headers["Content-Type"] = "application/json"
                headers["Cookie"] = self.accounts[address]["accessToken"]
                payload = {
                    "toAddress": recipient,
                    "amount": self.TRANSFER_AMOUNT,
                    "userId": self.accounts[address]["userId"]
                }

                async with AsyncSession(proxies=proxies, timeout=120, impersonate="chrome120") as session:
                    response = await session.post(url=url, headers=headers, json=payload)
                    self.ensure_ok(response)
                    return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Transfer Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, address: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(address)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.display_proxy(proxy_url)} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True

            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(address)
                await asyncio.sleep(1)
                continue

            return False
        
    async def process_connect_wallet(self, address: str, proxy_url=None):
        is_valid = await self.process_check_connection(address, proxy_url)
        if not is_valid: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(address)

        connect = await self.connect_wallet(address, proxy_url)
        if not connect: return False

        if not connect.get("success"):
            message = connect.get("message")

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {message} {Style.RESET_ALL}"
            )
            return False
        
        self.accounts[address]["userId"] = connect["data"]["userId"]

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
        )
        
        return True
        
    async def process_accounts(self, address: str, proxy_url=None):
        connected = await self.process_connect_wallet(address, proxy_url)
        if not connected: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(address)

        stats = await self.get_user_status(address, proxy_url)
        if stats:

            if not stats.get("success"):
                message = stats.get("message")
                
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Stats   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {message} {Style.RESET_ALL}"
                )
            else:
                testnet_address = stats.get("data", {}).get("testnetWalletAddress")
                txn_count = stats.get("data", {}).get("transactionCount")
                badge_count = stats.get("data", {}).get("badgeCount")

                self.log(f"{Fore.CYAN+Style.BRIGHT}Stats   :{Style.RESET_ALL}")
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}DIAM Address:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {testnet_address} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Txn Count   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {txn_count} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Badge Count :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {badge_count} {Style.RESET_ALL}"
                )
                
        fund = await self.fund_wallet(address, proxy_url)
        if fund:

            if not fund.get("success"):
                message = fund.get("message")

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Request Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {message} {Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Requested {Style.RESET_ALL}"
                )
            
            await self.print_timer(63, 65)

        self.log(f"{Fore.CYAN+Style.BRIGHT}Transfer:{Style.RESET_ALL}                           ")
        for i in range(self.TRANSFER_COUNT):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.TRANSFER_COUNT}{Style.RESET_ALL}                           "
            )

            recipient = self.generate_random_recipient()

            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Recipient:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {recipient} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.TRANSFER_AMOUNT} DIAM {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Tx Fee   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.TRANSFER_FEE} DIAM {Style.RESET_ALL}"
            )

            balance = await self.get_balance(address, proxy_url)
            if not balance: continue

            if not balance.get("success"):
                message = balance.get("message")

                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch DIAM Token Balance {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {message} {Style.RESET_ALL}"
                )
                continue

            diam_tokens = balance.get("data", {}).get("balance")

            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {diam_tokens} DIAM {Style.RESET_ALL}"
            )
            
            if diam_tokens < self.TRANSFER_AMOUNT + self.TRANSFER_FEE:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Insufficient DIAM Tokens Balance {Style.RESET_ALL}"
                )
                return
            
            transfer = await self.perform_transfer(address, recipient, proxy_url)
            if not transfer: continue

            if not transfer.get("success"):
                message = transfer.get("message")

                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Transfer Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {message} {Style.RESET_ALL}"
                )
            else:
                tx_hash = transfer.get("data", {}).get("transferData", {}).get("hash")
                tx_status = transfer.get("data", {}).get("transferData", {}).get("status")
                explorer = self.API_URL["explorer"]

                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} {tx_status} {Style.RESET_ALL}                           "
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Tx Hash  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Explorer :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {explorer}{tx_hash} {Style.RESET_ALL}"
                )

            await self.print_timer(63, 65)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                print(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return False
            
            self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )
                
                if self.USE_PROXY: self.load_proxies()

                separator = "=" * 25
                for idx, private_key in enumerate(accounts, start=1):
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    address = self.generate_address(private_key)
                    if not address: continue

                    if address not in self.accounts:
                        self.accounts[address] = {
                            "deviceId": self.generate_device_id()
                        }

                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Address :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                    )
                    
                    await self.process_accounts(address)
                    await asyncio.sleep(random.uniform(2.0, 3.0))

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)

                delay = 24 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except Exception as e:
            raise e
        except asyncio.CancelledError:
            raise

if __name__ == "__main__":
    bot = Diamante()
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Diamante - BOT{Style.RESET_ALL}                                       "                              
        )
    finally:
        sys.exit(0)