""" Post processing of mydata"""
import pickle
import sqlite3

class State(object):
    """state of my test"""

    def __init__(self):
        self.names = []
        self.dns_servers = []
        self.results = {}
        self._code = []

    def get_next_operations(self):
        """ Return some operations to run next """
        retval = self._code[:4]
        self._code = self._code[4:]
        return retval

    def no_more_operations(self):
        """check if there are no more operation"""
        return len(self._code) == 0

    def add_operation(self, function, args):
        """Add an operation in _code"""
        self._code.append((function, args))

def get_ip(address):
    """return ip"""
    return str(address['payload']['address'])

def get_hop(ipaddr, state):
    """return hop"""
    hop = len(state.results["traceroute"][ipaddr].split('\n')[1:])
    if hop == 0:
        hop = "NULL"
    return hop

def get_asnum(ipaddr, state):
    """return asnum"""
    for line in state.results["whois"][ipaddr].split('\n'):
        if line[:7] == "origin:":
            return line[8:].split(' ')[-1]

def get_reverse_ipv4(ipaddr, state, server):
    """return revA"""
    for result in state.results[server]["ReverseA"][ipaddr]:
        if result:
            return result['payload']['name']

def get_reverse_ipv6(ipaddr, state, server):
    """return revAAAA"""
    for result in state.results[server]["ReverseAAAA"][ipaddr]:
        if result:
            return result['payload']['name']


def main():
    """ Main function """
    con = sqlite3.connect('example.db')
    num = 0
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Mydata")
        cur.execute("CREATE TABLE Mydata(Id INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp TIMESTAMP, Server VARCHAR(30), Name VARCHAR(30), CName VARCHAR(30), IP VARCHAR(15),  Reverse VARCHAR(30),Num INT, ASN INT, Hop INT);")
        with open('data.pkl', 'rb') as input_data:
            state = pickle.load(input_data)
        for server in state.dns_servers:
            for name in state.names:
                ##IPV4
                for address in state.results[server]["A"][name]:
                    ipaddr = get_ip(address)
                    hop = get_hop(ipaddr, state)
                    asnum = get_asnum(ipaddr, state)
                    reverse = get_reverse_ipv4(ipaddr, state, server)

                    cur.execute("INSERT INTO Mydata(Timestamp,Server,Name,CName,IP,Reverse,Num,ASN,Hop) VALUES(datetime('NOW','localtime'),'"+server+"','"+name+"','"+address['name']+"','"+ipaddr+"','"+reverse+"','"+str(num)+"','"+str(asnum)+"','"+str(hop)+"');")

                ##IPV6
                for address in state.results[server]["AAAA"][name]:
                    ipaddr = get_ip(address)
                    hop = get_hop(ipaddr, state)
                    asnum = get_asnum(ipaddr, state)
                    reverse = get_reverse_ipv6(ipaddr, state, server)

                    cur.execute("INSERT INTO Mydata(Timestamp,Server,Name,CName,IP,Reverse,Num,ASN,Hop) VALUES(datetime('NOW','localtime'),'"+server+"','"+name+"','"+address['name']+"','"+ipaddr+"','"+reverse+"','"+str(num)+"','"+str(asnum)+"','"+str(hop)+"');")


if __name__ == "__main__":
    main()
