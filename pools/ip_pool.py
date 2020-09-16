from urllib.parse import urlparse
MAX_IP_NUM_LIMIT = 1000


class IPPool:

    def __init__(self):
        self.ips = set()
        self.max_ip_num_limit = MAX_IP_NUM_LIMIT
        # todo: check ip
        self._ip_rule = None

    def get_all_ips(self):
        ips_in_str = ''
        for ip in self.ips:
            ips_in_str += str(ip) + ';'
        return ips_in_str

    @property
    def ip_num(self):
        return len(self.ips)

    def add_ip(self, ip: str):
        parsed_url = urlparse(ip)
        if parsed_url.netloc:
            self.ips.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.ips.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def submit_ip(self, ip: str):
        if self.ip_num < self.max_ip_num_limit:
            self.add_ip(ip)
            return True

        return False

    @property
    def sorted_ips(self):
        return sorted(self.ips)



