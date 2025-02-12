import socks

s = socks.socksocket() # Same API as socket.socket in the standard lib

s.set_proxy(socks.SOCKS5, "localhost", 8000) # SOCKS4 and SOCKS5 use port 1080 by default
# Or
# s.set_proxy(socks.SOCKS4, "localhost", 8000)
# Or
# s.set_proxy(socks.HTTP, "5.5.5.5", 8888)

# Can be treated identical to a regular socket object
s.connect(("leetcode.com", 80))
s.sendall(b"GET / HTTP/1.1\r\nHost: leetcode.com\r\n\r\n")
print(s.recv(4096))
