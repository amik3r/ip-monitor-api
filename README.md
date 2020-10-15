# ip-monitor-api

## Usecase
This little app is intended to homelab builders, or even web developers who don't have static IP addresses at home or using DDNS is not suitable for them.


## Usage
Host the server on a VPS or EC2 that has static IP address.

Host the client on your home network.

When running, the client will request it's public IP and send it to the server. It can be later requested using the proper HTTP headers in the request.

If the headers don't match the config, the server will send a random IP address.


#### Installation (Server side)
```bash
# Clone repo
git clone https://github.com/amik3r/ip-monitor-api
cd ip-monitor-api
# Create and activate virtual env --- optional
mkdir venv && python3 -m venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 app.py
```

#### Installation (Client side)
```bash
# Clone repo
git clone https://github.com/amik3r/ip-monitor-api
cd ip-monitor-api
# Create and activate virtual env --- optional
mkdir venv && python3 -m venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 client.py
```
