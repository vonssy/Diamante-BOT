from curl_cffi import requests
from fake_useragent import FakeUserAgent
from http.cookies import SimpleCookie
from eth_account import Account
from datetime import datetime
from colorama import *
import asyncio, random, string, secrets, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Diamante:
    def __init__(self) -> None:
        self.BASE_API = "https://campapi.diamante.io/api/v1"
        self.EXPLORER = "https://sentinel.diamante.io/#/tx/"
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.cookie_headers = {}
        self.device_id = {}
        self.user_id = {}
        self.tf_count = 0
        self.tf_amount = 0

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
        {Fore.GREEN + Style.BRIGHT}Diam Testnet {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
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
        
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address

            return address
        except Exception as e:
            return None
        
    def generate_random_recepient(self):
        return "0x" + secrets.token_hex(20)
        
    def generate_device_id(self):
        hex_chars = string.hexdigits.lower()[:16]
        random_hex = ''.join(secrets.choice(hex_chars) for _ in range(4))
        return f"DEV{random_hex.upper()}"
    
    def generate_payload(self, address: str):
        try:
            return {
                "address": address,
                "deviceId": self.device_id[address],
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
                tf_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Transfer Count -> {Style.RESET_ALL}").strip())
                if tf_count > 0:
                    self.tf_count = tf_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                tf_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Transfer Amount [Min. 1] -> {Style.RESET_ALL}").strip())
                if tf_amount >= 1:
                    self.tf_amount = tf_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be >= 1 DIAM.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

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
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
        try:
            response = await asyncio.to_thread(requests.get, url="https://api.ipify.org?format=json", proxies=proxies, timeout=120, impersonate="chrome120")
            response.raise_for_status()
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
        url = f"{self.BASE_API}/user/connect-wallet"
        data = json.dumps(self.generate_payload(address))
        headers = {
            **self.HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": self.cookie_headers[address]
        }
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=120, impersonate="chrome120")
                response.raise_for_status()
                result = response.json()

                raw_cookies = response.headers.get_list('Set-Cookie', [])
                if raw_cookies:
                    cookie = SimpleCookie()
                    cookie.load("\n".join(raw_cookies))
                    cookie_string = "; ".join([f"{key}={morsel.value}" for key, morsel in cookie.items()])
                    self.cookie_headers[address] = cookie_string

                    return result
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def get_user_status(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/auth/get-user-status/{self.user_id[address]}"
        headers = {
            **self.HEADERS[address],
            "Cookie": self.cookie_headers[address]
        }
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=120, impersonate="chrome120")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Stats   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Stats Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def fund_wallet(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/transaction/fund-wallet/{self.user_id[address]}"
        headers = {
            **self.HEADERS[address],
            "Cookie": self.cookie_headers[address]
        }
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=120, impersonate="chrome120")
                response.raise_for_status()
                result = response.json()
                if "status" in result and result.get("status") == 429 or result.get("message") == "Something went wrong":
                    if attempt < retries - 1:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}/{retries}] Request Failed: {result['message']} {Style.RESET_ALL}"
                        )
                        await asyncio.sleep(60)
                        continue
                return result
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
        url = f"{self.BASE_API}/transaction/get-balance/{self.user_id[address]}"
        headers = {
            **self.HEADERS[address],
            "Cookie": self.cookie_headers[address]
        }
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=120, impersonate="chrome120")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch DIAM Tokens Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def perform_transfer(self, address: str, recepient: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/transaction/transfer"
        data = json.dumps({
            "toAddress": recepient,
            "amount": self.tf_amount,
            "userId": self.user_id[address]
        })
        headers = {
            **self.HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": self.cookie_headers[address]
        }
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=120, impersonate="chrome120")
                response.raise_for_status()
                result = response.json()
                if "status" in result and result.get("status") == 429:
                    if attempt < retries - 1:
                        self.log(
                            f"{Fore.BLUE + Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}/{retries}] Txn Error: {result['message']} {Style.RESET_ALL}"
                        )
                        await asyncio.sleep(15)
                        continue
                return result
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
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False

            return True
    
    async def process_connect_wallet(self, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            connect = await self.connect_wallet(address, proxy)
            if not connect: return

            if connect.get("message") == "Success":
                self.user_id[address] = connect["data"]["userId"]
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )
                return True
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {connect['message']} {Style.RESET_ALL}"
            )
            return False

    async def process_accounts(self, address: str, use_proxy: bool, rotate_proxy: bool):
        connected = await self.process_connect_wallet(address, use_proxy, rotate_proxy)
        if connected:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            stats = await self.get_user_status(address, proxy)
            if stats:

                if stats.get("message") == "Success":
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

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Stats   :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch Stats Failed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} {stats['message']} {Style.RESET_ALL}"
                    )

            fund = await self.fund_wallet(address, proxy)
            if fund:

                if fund.get("message") == "Success":
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Requested {Style.RESET_ALL}"
                    )

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Request Failed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} {fund['message']} {Style.RESET_ALL}"
                    )

            self.log(f"{Fore.CYAN+Style.BRIGHT}Transfer:{Style.RESET_ALL}")
            for i in range(self.tf_count):
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.tf_count}{Style.RESET_ALL}                           "
                )

                recepient = self.generate_random_recepient()
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Recepient:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {recepient} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Amount   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.tf_amount} DIAM {Style.RESET_ALL}"
                )

                balance = await self.get_balance(address, proxy)
                if not balance: continue

                if balance.get("message") == "Success":
                    diam_tokens = balance.get("data", {}).get("balance")

                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {diam_tokens} DIAM {Style.RESET_ALL}"
                    )

                else:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch DIAM Tokens Failed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} {balance['message']} {Style.RESET_ALL}"
                    )
                    continue
                
                if diam_tokens <= self.tf_amount:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Insufficient DIAM Tokens Balance {Style.RESET_ALL}"
                    )
                    return
                
                await self.print_timer(63, 65)
                
                transfer = await self.perform_transfer(address, recepient, proxy)
                if transfer:

                    if transfer.get("message") == "Success":
                        tx_hash = transfer.get("data", {}).get("transferData", {}).get("hash")
                        tx_status = transfer.get("data", {}).get("transferData", {}).get("status")

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
                            f"{Fore.WHITE+Style.BRIGHT} {self.EXPLORER}{tx_hash} {Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.BLUE+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Transfer Failed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} {transfer['message']} {Style.RESET_ALL}"
                        )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = True if proxy_choice == 1 else False

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies()

                separator = "=" * 25
                for idx, account in enumerate(accounts, start=1):
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue

                        self.cookie_headers[address] = "access_token="
                        self.device_id[address] = self.generate_device_id()
                        user_agent = FakeUserAgent(browsers=["chrome"], os="windows").random

                        self.HEADERS[address] = {
                            "Accept": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Access-Token": "key",
                            "Origin": "https://campaign.diamante.io",
                            "Referer": "https://campaign.diamante.io/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": user_agent
                        }
                        
                        await self.process_accounts(address, use_proxy, rotate_proxy)

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

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Diamante()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Diam Testnet - BOT{Style.RESET_ALL}                                       "                              
        )