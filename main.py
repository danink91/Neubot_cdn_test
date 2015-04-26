import subprocess

hostnames=["i.dailymail.co.uk", "g-ecx.images-amazon.com", "ecx.images-amazon.com","images-na.ssl-images-amazon.com"]
dnsservers=["8.8.8.8","208.67.222.222"]
ip = open("ip.txt", "wb")
rev =open("rev.txt","wb")
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
		#get whois
                
ip.close()
rev.close()
