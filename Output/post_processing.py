""" Post processing of mydata"""
import pickle
import sqlite3
import task_runner

def get_ip(address):
    """return ip"""
    return str(address['payload']['address'])

def get_hop(ipaddr, runner):
    """return hop"""
    hop = len(runner.results["traceroute"][ipaddr].split('\n')[1:])
    if hop == 0:
        hop = "NULL"
    return hop

def get_asnum(ipaddr, runner):
    """return asnum"""
    for line in runner.results["whois"][ipaddr].split('\n'):
        if line[:7] == "origin:":
            return line[8:].split(' ')[-1]

def get_reverse_ipv4(ipaddr, runner, server):
    """return revA"""
    for result in runner.results[server]["ReverseA"][ipaddr]:
        if result:
            return result['payload']['name']

def get_reverse_ipv6(ipaddr, runner, server):
    """return revAAAA"""
    for result in runner.results[server]["ReverseAAAA"][ipaddr]:
        if result:
            return result['payload']['name']


def main():
    """ Main function """
    import glob
    con = sqlite3.connect('example.db')
    num = 0
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Mydata")
        cur.execute("CREATE TABLE Mydata(Id INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp TIMESTAMP, Server VARCHAR(30), Name VARCHAR(30), CName VARCHAR(30), IP VARCHAR(15),  Reverse VARCHAR(30),Num INT, ASN INT, Hop INT);")
        for filename in glob.glob('*.pkl'):
            with open(filename, 'rb') as input_data:
                runner = pickle.load(input_data)
            for server in runner.dns_servers:
                for name in runner.names:
                    ##IPV4
                    for address in runner.results[server]["A"][name]:
                        ipaddr = get_ip(address)
                        hop = get_hop(ipaddr, runner)
                        asnum = get_asnum(ipaddr, runner)
                        reverse = get_reverse_ipv4(ipaddr, runner, server)

                        cur.execute("INSERT INTO Mydata(Timestamp,Server,Name,CName,IP,Reverse,Num,ASN,Hop) VALUES(datetime('NOW','localtime'),'"+server+"','"+name+"','"+address['name']+"','"+ipaddr+"','"+reverse+"','"+str(num)+"','"+str(asnum)+"','"+str(hop)+"');")

                    ##IPV6
                    for address in runner.results[server]["AAAA"][name]:
                        ipaddr = get_ip(address)
                        hop = get_hop(ipaddr, runner)
                        asnum = get_asnum(ipaddr, runner)
                        reverse = get_reverse_ipv6(ipaddr, runner, server)

                        cur.execute("INSERT INTO Mydata(Timestamp,Server,Name,CName,IP,Reverse,Num,ASN,Hop) VALUES(datetime('NOW','localtime'),'"+server+"','"+name+"','"+address['name']+"','"+ipaddr+"','"+reverse+"','"+str(num)+"','"+str(asnum)+"','"+str(hop)+"');")


if __name__ == "__main__":
    main()
