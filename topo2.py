from ipmininet.iptopo import IPTopo
from ipmininet.router.config import SSHd, BGP
from ipmininet.host.config import Named
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet import DEBUG_FLAG
from ipmininet.srv6 import enable_srv6
from ipmininet.srv6 import SRv6Encap

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        r1, r2, r3, r4, r5 = self.addRouters("r1", "r2", "r3", "r4", "r5")
        r1.addDaemon(BGP)
        r2.addDaemon(BGP)
        r3.addDaemon(BGP)
        r4.addDaemon(BGP)
        r5.addDaemon(BGP)

        h1 = self.addHost("h1")

        h2 = self.addHost("h2")

        self.addLink(r1, r2)
        # Helper to create several links in one function call
        self.addLinks((h1, r1), (h2, r2), (r2, r3),
                      (r3, r4), (r4, r5))

        self.addiBGPFullMesh(1, routers=[r1, r2, r3, r4, r5])

        super().build(*args, **kwargs)
    
    def post_build(self, net):
        for n in net.hosts + net.routers:
            interfaces = ["all", "lo", "default", str(n)+"-eth0"]
            # enable_srv6(n)
            for i in interfaces:
                result = n.cmd("sysctl net.ipv6.conf."+i+".seg6_enabled=1")
                print(result)
                result = n.cmd("sysctl net.ipv6.conf."+i+".seg6_require_hmac=-1")
                print(result)
        result = net.get("h1").cmd("ip -6 route add fc00:0:2::1 encap seg6 mode inline segs fc00:0:5::1 dev h1-eth0")
        print(result)
    
    # # No need to enable SRv6 because the call to the abstraction
    # # triggers it

    # # This adds an SRH encapsulation route on h1 for packets to h2
    #     SRv6Encap(net=net, node="h1", to="h2",
    #                 # You can specify the intermediate point with any
    #                 # of the host, its name, an interface or the address
    #                 # itself
    #                 # through=[net["r1"], "r1", net["r1"].intf("lo"),
    #                 #         net["r1"].intf("lo").ip6],
    #                 through=[net["r5"]],
    #                 # Either insertion (INLINE) or encapsulation (ENCAP)
    #                 mode=SRv6Encap.INLINE)
    #     super().post_build(net)


if __name__ == "__main__":
    
    net = IPNet(topo=MyTopology(), use_v4=False)
    # DEBUG_FLAG = True
    try:
        net.start()
        IPCLI(net)
    finally:
        net.stop()

    #sudo python -m ipmininet.clean --> si ça crash ou qu'on oublie de net.stop()