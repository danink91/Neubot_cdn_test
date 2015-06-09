import pickle
import pprint
import sqlite3


class State(object):

    # TODO: do the iterator the Pythonic way

    def __init__(self):
        self.names = []
        self.dns_servers = []
        self.results = {}
        self._code = []

    def get_next_operations(self):
        """ Return some operations to run next """
        # TODO: use deque for efficiency
        retval = self._code[:1]
        self._code = self._code[1:]
        return retval

    def no_more_operations(self):
        return len(self._code) == 0

    def add_operation(self, function, args):
        self._code.append((function, args))

def get_ip(address):
    return str(address['payload']['address'])

def get_hop(ip,state):
    hop= len(state.results["traceroute"][ip].split('\n')[1:])
    if hop == 0:
        hop = "NULL"
    return hop

def get_asnum(ip,state):
    for x in state.results["whois"][ip].split('\n'):
        if x[:7] == "origin:":
            return x[8:].split(' ')[-1]
def get_reverseA(ip,state,server):
    for y in state.results[server]["ReverseA"][ip]:
        if y:
            return y['payload']['name']
def get_reverseAAAA(ip,state,server):
    for y in state.results[server]["ReverseAAAA"][ip]:
        if y:
            return y['payload']['name']


def main():
    """ Main function """
    con = sqlite3.connect('example.db')
    num = 0
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Mydata")
        cur.execute("CREATE TABLE Mydata(Id INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp TIMESTAMP, Server VARCHAR(30), Name VARCHAR(30), CName VARCHAR(30), IP VARCHAR(15),  Reverse VARCHAR(30),Num INT, ASN INT, Hop INT);")
        with open('data.pkl', 'rb') as input:
            state = pickle.load(input)
        for server in state.dns_servers:
            for name in state.names:
                ##IPV4
                for address in state.results[server]["A"][name]:
                    ip=get_ip(address)
                    hop=get_hop(ip,state)
                    asnum =get_asnum(ip,state)
                    reverse=get_reverseA(ip,state,server)

                    cur.execute("INSERT INTO Mydata(Timestamp,Server,Name,CName,IP,Reverse,Num,ASN,Hop) VALUES(datetime('NOW','localtime'),'"+server+"','"+name+"','"+address['name']+"','"+ip+"','"+reverse+"','"+str(num)+"','"+str(asnum)+"','"+str(hop)+"');" )

                ##IPV6
                for address in state.results[server]["AAAA"][name]:
                    ip=get_ip(address)
                    hop=get_hop(ip,state)
                    asnum =get_asnum(ip,state)
                    reverse=get_reverseAAAA(ip,state,server)

                    cur.execute("INSERT INTO Mydata(Timestamp,Server,Name,CName,IP,Reverse,Num,ASN,Hop) VALUES(datetime('NOW','localtime'),'"+server+"','"+name+"','"+address['name']+"','"+ip+"','"+reverse+"','"+str(num)+"','"+str(asnum)+"','"+str(hop)+"');" )


if __name__ == "__main__":
    main()  
     
