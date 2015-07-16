""" Post processing of mydata"""
import pickle
import sqlite3
import task_runner
import ipaddress
import os

def get_time(address):
    """return time"""
    if 'time' in address:
        return str(address['time'])

def get_utime(address):
    """return unixtime"""
    if 'utime' in address:
        return str(address['utime'])
def get_ip(address):
    """return ip"""
    if 'payload' in address:
        return str(address['payload']['address'])
    else:
        return "None"

def get_hop(ipaddr, runner):
    """return hop"""
    hop = len(runner.results["traceroute"][ipaddr].split('\n')[1:])
    if hop == 0:
        hop = "NULL"
    return hop

def get_RTT(ipaddr, runner):
    """return RTT"""
    if get_hop(ipaddr, runner)=="NULL":
        return "None"
    else: 
        return runner.results["traceroute"][ipaddr].split('\n')[-2].split('ms')[0].split(' ')[-2]

def get_asnum(ipaddr, runner):
    """return asnum"""
    if runner.results["whois"][ipaddr]:
        return runner.results["whois"][ipaddr].split('\n')[-2].split('|')[0]
    else:
        return "None"

def get_reverse(ipaddr, runner, server):
    """return revA"""
    for result in runner.results["reverse"][ipaddr]:
        if 'payload' in result:
            return result['payload']['name']
        if 'rCode' in result:
            return "Err"
    return "None"


def main():
    """ Main function """
    import glob
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser('Output'))
    con = sqlite3.connect('example.db')
    num = 0
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Mydata")
        cur.execute("CREATE TABLE Mydata(Id INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp TIMESTAMP, UnixTime INT, Server VARCHAR(30), Name VARCHAR(30), CName VARCHAR(30), IP VARCHAR(15), IP_range VARCHAR(15), IP_int INT, Reverse VARCHAR(30), ASN INT, Hop INT, RTT FLOAT);")

        for filename in glob.glob('*.pkl'):
            with open(filename, 'rb') as input_data:
                runner = pickle.load(input_data)
            for server in runner.dns_servers:
                for name in runner.names:
                    ##IPV4
                    for address in runner.results[server]["A"][name]:
                        ipaddr = get_ip(address)
                        if ipaddr != "None":
                            #ipaddr_int = int(ipaddress.ip_address(ipaddr.decode('unicode-escape')))
                            ipaddr_int = int(ipaddress.ip_address(ipaddr))
                            hop = get_hop(ipaddr, runner)
                            asnum = get_asnum(ipaddr, runner)
                            reverse = get_reverse(ipaddr, runner, server)
                            time = get_time(address)
                            utime = get_utime(address)
                            RTT = get_RTT(ipaddr, runner)
                            ip_range = ipaddress.ip_network(ipaddr+'/24', strict=False).network_address.compressed                                                 

                            cur.execute("INSERT INTO Mydata(Timestamp,UnixTime,Server,Name,CName,IP,IP_range,IP_int,Reverse,ASN,Hop,RTT) VALUES('"+time+"','"+utime+"','"+server+"','"+name+"','"+address['name']+"','"+ipaddr+"','"+ip_range+"','"+str(ipaddr_int)+"','"+reverse+"','"+str(asnum)+"','"+str(hop)+"','"+RTT+"');")

                    ##IPV6
                    for address in runner.results[server]["AAAA"][name]:
                        ipaddr = get_ip(address)
                        if ipaddr != "None":
                            #ipaddr_int = int(ipaddress.ip_address(ipaddr.decode('unicode-escape')))
                            ipaddr_int = int(ipaddress.ip_address(ipaddr))                            
                            hop = get_hop(ipaddr, runner)
                            asnum = get_asnum(ipaddr, runner)
                            reverse = get_reverse(ipaddr, runner, server)
                            time = get_time(address)  
                            utime = get_utime(address)
                            RTT = get_RTT(ipaddr, runner)
                            ip_range = ipaddress.ip_network(ipaddr+'/96', strict=False).network_address.compressed

                            cur.execute("INSERT INTO Mydata(Timestamp,UnixTime,Server,Name,CName,IP,IP_range,IP_int,Reverse,ASN,Hop,RTT) VALUES('"+time+"','"+utime+"','"+server+"','"+name+"','"+address['name']+"','"+ipaddr+"','"+ip_range+"','"+str(ipaddr_int)+"','"+reverse+"','"+str(asnum)+"','"+str(hop)+"','"+RTT+"');")


if __name__ == "__main__":
    main()
