import requests
import logging

class StratoUpdater():
    def __init__(self, config):
        self.username = config["username"]
        self.password = config["password"]
        self.domain = config["domain"]
        self.last_ips = set() 

    def update(self, ips):
        all_ips = {ip.address for ip in ips}

        if self.last_ips == all_ips:
            logging.info("StratoUpdater: No IP change detected, skipping update.")
            return True

        ip_string = ','.join(all_ips)
        full_url = f"https://{self.username}:{self.password}@dyndns.strato.com/nic/update?hostname={self.domain}&myip={ip_string}"

        logging.info(f"StratoUpdater: Sending update for IPs: {ip_string}")
        
        
        try:
            resp = requests.get(full_url)
            body = resp.text.strip()
            
            self.last_ips = set(all_ips.copy())

            if body.startswith("good"):
                # Update successful
                logging.info("StratoUpdater: IPs updated successfully.")
                return True 
            elif body.startswith("nochg"):
                # No change in IPs, already up-to-date
                logging.info("StratoUpdater: IPs were already up-to-date.")
                self.last_ips = all_ips.copy()
                return False 
            elif body.startswith("badauth") or body.startswith("nohost"):
                # Authentication failed or domain does not exist   
                logging.error("StratoUpdater: Authentication failed or domain does not exist.")
                raise ValueError("StratoUpdater: Authentication failed or domain does not exist.")
            else:
                # Unexpected response
                logging.error(f"StratoUpdater: Unexpected response: {body}")
                raise ValueError(f"StratoUpdater: Unexpected response: {body}")
            
        except Exception as e:
            logging.error(f"StratoUpdater: DNS update failed: {e}")
            raise e