#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/app/.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dns_update.log'),
        logging.StreamHandler()
    ]
)

class CloudflareDNSUpdater:
    def __init__(self, api_key, email, zone_id, record_name):
        self.api_key = api_key
        self.email = email
        self.zone_id = zone_id
        self.record_name = record_name
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }

    def get_current_ip(self):
        """Get current public IP address"""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json()['ip']
        except Exception as e:
            logging.error(f"Failed to get current IP: {e}")
            return None

    def get_record_id(self):
        """Get the DNS record ID for the specified record name"""
        try:
            url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            records = response.json()['result']
            for record in records:
                if record['name'] == self.record_name:
                    return record['id']
            return None
        except Exception as e:
            logging.error(f"Failed to get record ID: {e}")
            return None

    def update_dns_record(self, ip):
        """Update the DNS record with the new IP address"""
        try:
            record_id = self.get_record_id()
            if not record_id:
                logging.error(f"Record ID not found for {self.record_name}")
                return False

            url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
            data = {
                "type": "A",
                "name": self.record_name,
                "content": ip,
                "proxied": True
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logging.info(f"Successfully updated DNS record for {self.record_name} to IP {ip}")
            return True
        except Exception as e:
            logging.error(f"Failed to update DNS record: {e}")
            return False

def main():
    # Configuration for multiple domains
    domains = [
        {
            'zone_id': os.getenv('POCKETFUSION_ZONE_ID'),
            'record_name': os.getenv('POCKETFUSION_RECORD')
        },
        {
            'zone_id': os.getenv('GEEKYNAVIGATOR_ZONE_ID'),
            'record_name': os.getenv('GEEKYNAVIGATOR_RECORD')
        }
    ]
    
    api_key = os.getenv('CLOUDFLARE_API_KEY')
    email = os.getenv('CLOUDFLARE_EMAIL')

    if not all([api_key, email]):
        logging.error("Missing required API key or email")
        return

    # Get current IP once
    current_ip = None
    for domain in domains:
        if not domain['zone_id']:
            logging.error(f"Missing zone ID for {domain['record_name']}")
            continue
            
        updater = CloudflareDNSUpdater(
            api_key, 
            email, 
            domain['zone_id'],
            domain['record_name']
        )
        
        if not current_ip:
            current_ip = updater.get_current_ip()
            if not current_ip:
                logging.error("Failed to get current IP address")
                return
                
        updater.update_dns_record(current_ip)

if __name__ == "__main__":
    main() 