+# CDN test location
+
+- Author: Daniele Di Carlo and Simone Basso
+- Version: 1.0
+- Date: 2015-04-24
+- Documents: CDN test
+
+This document describes an idea for a test useful for locating
+hosts belonging to content delivery networks.
+
+A complementary problem is how to figure out which are the
+most frequently contacted host, but this is not addressed
+by this document.
+
+## High-level algorithm
+
+Here we describe the input and output of the algorithm, as well
+as the capabilities that the software must implement.
+
+- Input:
+  - List of domain names to be tested
+  - List of DNS servers
+- Output:
+  - For each domain name:
+    - The corresponding IPv4/IPv6 address
+    - The reverse lookup
+    - The route to reach such address
+    - The owner of this address
+- Capabilities:
+  - Library MUST allow to set a specific DNS
+  - Find out the default DNS of the user's ISP (?)
+  - Run traceroute or execute system-wide traceroute
+  - Run whois client or execute system-wide whois client (?)
+  - Resolve A and AAAA
+  - Reverse lookup
+
+The following is the algorithm:
+
+1. Find out the user's ISP default DNS
+2. Add this DNS to the list of DNS servers
+3. For each DNS server:
+  3.1. For each domain name:
+    3.1.1. ipv4_addr = Lookup(A, domain name)
+    3.1.2. ipv6_addr = Lookup(AAAA, domain name)
+    3.1.3. ReverseLookup(A, ipv4_addr)
+    3.1.4. ReverseLookup(AAAA, ipv6_addr)
+    3.1.5. Traceroute(ipv4_addr)
+    3.1.6. Traceroute6(ipv6_addr)
+    3.1.6. Whois(ipv4_addr)
+    3.1.7. Whois(ipv6_addr)

