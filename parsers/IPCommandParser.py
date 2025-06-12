import subprocess
import re
from datetime import datetime, timedelta
from IPInfo import IPv4Info, IPv6Info

class IPCommandParser:
    def __init__(self, config):
        self.interface = config["interface"]
        self.scope = config.get("scope", "global")
        self.timeout = config.get("command_timeout", 5)
        self.fetch_ipv4 = config.get("fetch_ipv4", True)
        self.fetch_ipv6 = config.get("fetch_ipv6", True)
        self.ipv4_index = config.get("ipv4_index", None)
        self.ipv6_index = config.get("ipv6_index", None)

    def _get_ip_infos(self):
        # Use a single command for both families
        cmd = [
            "ip", "addr", "show", "dev", self.interface, "scope", self.scope
        ]
        output = subprocess.check_output(cmd, timeout=self.timeout).decode()
        
        print(output)

        # Multiline regex to match inet/inet6 and the following valid_lft
        pattern = re.compile(
            r'^\s+(?P<inet>inet6?) (?P<ip>[\da-fA-F\.:]+)/\d+.*\n\s+valid_lft (?P<lft>\w+)',
            re.MULTILINE
        )

        ips = []
        for match in pattern.finditer(output):
            # Lifetime
            try:
                lifetime = int(match.group("lft").replace("sec", ""))
            except Exception:
                # either error or lifetime = "forever"
                lifetime = None
            
            # Return the IP info based on inet/inet6
            if match.group("inet") == "inet":
                ips.append(IPv4Info(match.group("ip"), lifetime))
            else:
                ips.append(IPv6Info(match.group("ip"), lifetime))
        return ips

    def get_ips(self):
        all_ips = self._get_ip_infos()
        ipv4s = [ip for ip in all_ips if isinstance(ip, IPv4Info)]
        ipv6s = [ip for ip in all_ips if isinstance(ip, IPv6Info)]
        
        print(all_ips)

        ips = []
        if self.fetch_ipv4:
            if self.ipv4_index is not None:
                if 0 <= self.ipv4_index < len(ipv4s):
                    ips.append(ipv4s[self.ipv4_index])
                else:
                    raise IndexError(f"IPv4 index {self.ipv4_index} is out of range for available IPv4 addresses.")
            else:
                ips.extend(ipv4s)
                
        if self.fetch_ipv6:
            if self.ipv6_index is not None:
                if 0 <= self.ipv6_index < len(ipv6s):
                    ips.append(ipv6s[self.ipv6_index])
                else:
                    raise IndexError(f"IPv6 index {self.ipv6_index} is out of range for available IPv6 addresses.")
            else:
                ips.extend(ipv6s)

        lifetime = min([ip.valid_lifetime for ip in ips if ip.valid_lifetime is not None], default=24 * 60 * 60)
        return ips, lifetime