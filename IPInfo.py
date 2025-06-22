class IPInfo:
    def __init__(self, address, valid_lifetime=None):
        self.address = address
        self.valid_lifetime = valid_lifetime
        
    def __repr__(self):
        return f"IPInfo(address={self.address}, valid_lifetime={self.valid_lifetime})"

class IPv4Info(IPInfo):
    def __init__(self, address, valid_lifetime=None):
        super().__init__(address, valid_lifetime)

class IPv6Info(IPInfo):
    def __init__(self, address, valid_lifetime=None):
        super().__init__(address, valid_lifetime)
    