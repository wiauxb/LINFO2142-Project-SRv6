from ipmininet.iptopo import IPTopo
from ipmininet.router.config import SSHd, BGP, AF_INET6, ebgp_session, CLIENT_PROVIDER, SHARE,  BorderRouterConfig, set_rr
from ipmininet.host.config import Named
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet import DEBUG_FLAG
from ipmininet.srv6 import enable_srv6
from ipmininet.srv6 import SRv6Encap
from ipmininet.utils import realIntfList
from time import sleep

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        as1r1 = self.bgp('as1r1')
        as1r2 = self.bgp('as1r2', family=AF_INET6(redistribute=('ospf6', 'connected')))
        as1r3 = self.bgp('as1r3')
        as1r4 = self.bgp('as1r4', family=AF_INET6(redistribute=('ospf6', 'connected')))
        as2r1 = self.bgp('as2r1', family=AF_INET6(redistribute=('ospf6', 'connected'), networks=('dead:beef::/32',)))
        as2r2 = self.bgp('as2r2', family=AF_INET6(redistribute=('ospf6', 'connected'), networks=('dead:beef::/32',)))

        as1h1 = self.addHost('as1h1')
        as2h1 = self.addHost('as2h1')
        switch = self.addSwitch('s2')
        
        self.addLinks((as1r1, as1r2), (as1r2, as1r4), (as1r3, as1r4), (as1r3, as1h1))
        self.addLink(as1r1, as1r3, igp_metric=10)
        self.addLinks((as1r2, as2r1), (as1r4, as2r2))
        self.addLinks((as2r1, as2r2), (as2r1, switch), (as2r2, switch), (switch, as2h1))
        self.addSubnet((as2r1, as2r2, as2h1), subnets=('dead:beef::/32',))
    

        # Set AS-ownerships
        self.addAS(1, (as1r1, as1r2, as1r3, as1r4))
        self.addAS(2, (as2r1, as2r2))
        set_rr(self, rr=as1r1, peers=(as1r2, as1r3, as1r4))

        # Add eBGP peering
        ebgp_session(self, as1r2, as2r1)
        ebgp_session(self, as1r4, as2r2)
            
        super().build(*args, **kwargs)

    def bgp(self, name, family=AF_INET6()):
        r = self.addRouter(name)
        r.addDaemon(BGP, address_families=(family,))
        return r
    
    def post_build(self, net):
        for n in net.hosts + net.routers:
            
            result = n.cmd("sysctl net.vrf.strict_mode = 1")
            result = n.cmd("sysctl net.ipv4.conf.all.rp_filter = 0")
            result = n.cmd("sysctl net.ipv6.seg6_flowlabel = 1")
            
            n.cmd("sysctl net.ipv6.conf.all.seg6_enabled=1")
            n.cmd("sysctl net.ipv6.conf.default.seg6_enabled=1")
            for intf in realIntfList(n):
                n.cmd("sysctl net.ipv6.conf.%s.seg6_enabled=1" % intf.name)

        for r in net.routers:
            r.cmd("python3 lookup_bgp_table.py &")
            
        super().post_build(net)

if __name__ == "__main__":
    
    net = IPNet(topo=MyTopology(), use_v4=False)
    # DEBUG_FLAG = True
    try:
        net.start()
        IPCLI(net)
    finally:
        net.stop()

    #sudo python -m ipmininet.clean --> si ça crash ou qu'on oublie de net.stop()