import telnetlib
import re
import subprocess
from time import sleep

def load_bgp_table():
    tn = telnetlib.Telnet("localhost", 2605)

    tn.read_until(b"Password: ")
    tn.write("zebra".encode('ascii') + b"\n")
    tn.write(b"sh bgp\n")
    tn.write(b"exit\n")

    return tn.read_all().decode('ascii')


def load_ip_route_table():
    tn = telnetlib.Telnet("localhost", 2601)

    tn.read_until(b"Password: ")
    tn.write("zebra".encode('ascii') + b"\n")

    tn.write(b"sh ipv6 route\n")
    tn.write(b"exit\n")

    return tn.read_all().decode('ascii')

############################################################
#
# https://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
#
############################################################
#
# IPV6SEG  = [0-9a-fA-F]{1,4}
# IPV6ADDR =  (
#         (IPV6SEG:){7,7}IPV6SEG|                # 1:2:3:4:5:6:7:8
#         (IPV6SEG:){1,7}:|                      # 1::                                 1:2:3:4:5:6:7::
#         (IPV6SEG:){1,6}:IPV6SEG|               # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
#         (IPV6SEG:){1,5}(:IPV6SEG){1,2}|        # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
#         (IPV6SEG:){1,4}(:IPV6SEG){1,3}|        # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
#         (IPV6SEG:){1,3}(:IPV6SEG){1,4}|        # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
#         (IPV6SEG:){1,2}(:IPV6SEG){1,5}|        # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
#         IPV6SEG:((:IPV6SEG){1,6})|             # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
#         :((:IPV6SEG){1,7}|:)|                  # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::       
#         fe80:(:IPV6SEG){0,4}%[0-9a-zA-Z]{1,}|  # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
#         ::(ffff(:0{1,4}){0,1}:){0,1}IPV4ADDR|  # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
#         (IPV6SEG:){1,4}:IPV4ADDR               # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
#         )

def parse_bgp_table(table):
    IPV6ADDR = r"((([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|([0-9a-fA-F]{1,4}:){1,7}:|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(/[0-9]{1,3})?)"


    lines = re.findall(r"\*>.*\n", table)

    matches = map(lambda line: re.findall(IPV6ADDR, line), lines)
    addresses = map(lambda pair: (pair[0][0], pair[1][0]), matches)

    return list(addresses)


def parse_ip_route_table(table):
    IPV6ADDR = r"((([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|([0-9a-fA-F]{1,4}:){1,7}:|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(/[0-9]{1,3})?)"
    NEXTHOP = IPV6ADDR + r", (.*), weight"

    lines = re.findall(r"(B>(.|\n)*?(?=\n[a-zA-Z]))", table)


    match_nexthop = map(lambda line: re.findall(NEXTHOP, line[0]), lines)
    match_addr = map(lambda line: re.findall(IPV6ADDR, line[0]), lines)
    addresses = map(lambda pair: (pair[0][0][0], pair[0][1][0], pair[1][0][-1]), zip(match_addr, match_nexthop))

    return list(addresses)


def get_existing_config():
    # source: https://www.cyberciti.biz/faq/python-run-external-command-and-get-output/
    p = subprocess.Popen("ip -6 route | grep seg6 | cut -f1 -d ' '", stdout=subprocess.PIPE, shell=True)
 
    ## Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
    ## Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.  ##
    ## Wait for process to terminate. The optional input argument should be a string to be sent to the child process, ##
    ## or None, if no data should be sent to the child.
    (output, err) = p.communicate()
     
    ## Wait for date to terminate. Get return returncode ##
    p_status = p.wait()
    return output.decode().strip().split("\n")


if __name__ == "__main__":
    while True:
        sleep(15)
        existing = get_existing_config()
        for addr in existing:
            subprocess.call(["ip", "-6", "route", "del", addr])
        sleep(.1)
        table = load_ip_route_table()
        # print(table)
        nexthops = parse_ip_route_table(table)
        for addr, nexthop, dev in nexthops:
            # print(addr, nexthop, dev)
            if "fe80" not in nexthop:
                subprocess.call(["ip", "-6", "route", "replace", addr, "encap", "seg6", "mode", "inline", "segs", nexthop, "dev", dev])
        # break