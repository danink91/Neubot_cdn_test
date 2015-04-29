import subprocess

##INPUT
#hostnames=["i.dailymail.co.uk", "g-ecx.images-amazon.com", "ecx.images-amazon.com","images-na.ssl-images-amazon.com"]
with open("Input/hostnames") as f:
	hostnames = f.read().splitlines()
#dnsservers=["8.8.8.8","208.67.222.222"]
with open("Input/dnsservers") as f:
	dnsservers = f.read().splitlines()
########################################

##OUTPUT
ip = open("Output/ip.txt", "wb")
rev =open("Output/rev.txt","wb")
trace =open("Output/trace.txt","wb")
who = open("Output/who.txt","wb")
########################################
for dns in dnsservers:
        #f.write("RESULTS for DNS server:"+dns+"\n")
        for host in hostnames:              
                
                #get the corresponding IP
                cmd="python gethost.py "+ host + " "+ dns
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                p = proc.communicate()[0]
                ip.write(p)
                #get the reverse lookup
                cmd="python reverse_lookup.py "+ p
                proc =subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                p = proc.communicate()[0]
                rev.write(p)
                #get the route
                cmd="traceroute "+ p
                proc =subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                q = proc.communicate()[0]        
                trace.write(q)
		trace.write("\n\n")
                #get whois
		cmd="whois "+ p
                proc =subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                p = proc.communicate()[0]
		who.write(p)
		who.write("\n\n")
                
ip.close()
rev.close()
trace.close()
who.close()
