from ipmininet.iptopo import IPTopo
from ipmininet.router.config import SSHd
from ipmininet.host.config import Named
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet import DEBUG_FLAG
from ipmininet.srv6 import enable_srv6

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        r1 = self.addRouter("r1")
        r1.addDaemon(SSHd)
        
        r2 = self.addRouter("r2")
        # Helper to create several routers in one function call
        r3, r4, r5 = self.addRouters("r3", "r4", "r5")

        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        h1 = self.addHost("h1")
        h1.addDaemon(Named)

        h2 = self.addHost("h2")

        self.addLink(r1, r2)
        # Helper to create several links in one function call
        self.addLinks((s1, r1), (h1, s1), (s2, r2), (h2, s2), (r2, r3),
                      (r3, r4), (r4, r5))

        super().build(*args, **kwargs)
    
    def post_build(self, net):
        for n in net.hosts + net.routers:
            enable_srv6(n)
        super().post_build(net)


if __name__ == "__main__":
    
    net = IPNet(topo=MyTopology())
    # DEBUG_FLAG = True
    try:
        net.start()
        IPCLI(net)
    finally:
        net.stop()