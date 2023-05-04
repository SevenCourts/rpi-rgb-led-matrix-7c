POST {{tableau_server_url}}/panels/
{
    "code": "hostname"
}

POST {{tableau_server_url}}/panels/
{
    "code": "hostname-ip",
    "ip": "192.168.113.200"
}

POST {{tableau_server_url}}/panels/
{
    "code": "hostname-ip-fwversion",
    "ip": "192.168.113.200",
    "firmware_version": "deadbeaf"
}
