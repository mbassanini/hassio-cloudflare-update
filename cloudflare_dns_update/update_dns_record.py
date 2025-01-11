import http.client
import json
import time
import sys

API_Token = sys.argv[1]
zone_ID = sys.argv[2]
domain = sys.argv[3]
sleepTime = int(sys.argv[4])

connCloudflare = http.client.HTTPSConnection("api.cloudflare.com")
headers = {
    'authorization': f"Bearer {API_Token}",
    'content-type': "application/json"
}

def get_Public_IP():
    conn = http.client.HTTPSConnection("api.ipify.org")
    conn.request("GET","/")
    res = conn.getresponse()
    return res.read().decode("utf-8")
    
def get_DNS_Record():
    print("INFO: Retrieving DNS records from Cloudlare")
    connCloudflare.request("GET", "/client/v4/zones/{zone_ID}/dns_records", headers=headers)
    res = connCloudflare.getresponse()
    response = json.load(res)
    print(response)
    #find the DNS record
    for res in response["result"]:
        if res["name"] == domain:
            return res["id"], res["content"]
    return None, None

def update_DNS_Record(DNS_record_ID, public_IP):
    print("INFO: Updating DNS record")
    payload = f"{{\"content\":\"{public_IP}\",\"type\":\"A\"}}"
    connCloudflare.request("PATCH", f"/client/v4/zones/{zone_ID}/dns_records/{DNS_record_ID}", payload, headers)
    res = connCloudflare.getresponse()
    response = json.load(res)
    print(response)

old_Public_IP = None

while True:
    public_IP =  get_Public_IP()

    if old_Public_IP == public_IP:
        print("INFO: Publc IP address has not changed!")
    else:
        #Get list of DNS records, to find the DNS record ID
        DNS_record_ID, DNS_Content = get_DNS_Record()
        if not DNS_record_ID or not DNS_Content:
            print("ERROR: DNS Record not found! Check config file and/or Cloudlare domain configuration")
            exit()

        #Update the DNS Record?
        if DNS_Content == public_IP:
            print("INFO: DNS Record matches already your public IP - No update needed")
        else:
            update_DNS_Record(DNS_record_ID, public_IP)

    time.sleep(sleepTime)
    old_Public_IP = public_IP
