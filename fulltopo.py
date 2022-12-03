from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet.router.config import BGP, ebgp_session, set_rr, AccessList, \
    AF_INET6



class MyTopology(IPTopo):
    """This topology is composed of two AS connected in dual homing
     with different local pref and MED. AS1 has one route reflector: as1r3."""

    def build(self, *args, **kwargs):
        """
                                 +
                           AS1   |   AS4
        +-------+                |
        | as1r1 +--------+       |
        +---+---+        |       |
          2 |            |       |
        +---+---+    +---+---+   |   +-------+
        | as1r3 +----+ as1r6 +-------+ as4r1 +--------+
        +---+---+    +---+---+   |   +-------+        |
            |            |       |                    |
        +---+---+        |       |                 +--+--+     +-------+
        | as1r2 |        |       |                 | s4  +-----+ as4h1 |
        +---+---+        |       |                 +--+--+     +-------+
          4 |            |       |                    |
        +---+---+    +---+---+   |   +-------+        |
        | as1r4 +----+ as1r5 +-------+ as4r2 +--------+
        +-------+    +-------+   |   +-------+
                                 |
                                 +
        """

        # Add all routers
        as1r1 = self.bgp('as1r1')
        as1r2 = self.bgp('as1r2')
        as1r3 = self.bgp('as1r3')
        as1r4 = self.bgp('as1r4')
        as1r5 = self.bgp('as1r5',
                         family=AF_INET6(redistribute=('ospf6', 'connected')))
        as1r6 = self.bgp('as1r6',
                         family=AF_INET6(redistribute=('ospf6', 'connected')))
        as4r1 = self.bgp('as4r1', family=AF_INET6(networks=('dead:beef::/32',)))
        as4r2 = self.bgp('as4r2', family=AF_INET6(networks=('dead:beef::/32',)))

        # Add the host and the switch
        as1h1 = self.addHost('as1h1')
        as4h1 = self.addHost('as4h1')
        switch = self.addSwitch('s4')

        # Add Links
        self.addLink(as1r1, as1r6)
        self.addLink(as1r1, as1h1)
        self.addLink(as1r1, as1r3, igp_metric=2)
        self.addLinks((as1r3, as1r2), (as1r3, as1r6))
        self.addLink(as1r2, as1r4, igp_metric=4)
        self.addLinks((as1r4, as1r5), (as1r5, as1r6), (as4r1, as1r6),
                      (as4r2, as1r5), (as4r1, switch), (as4r2, switch),
                      (switch, as4h1))
        self.addSubnet((as4r1, as4r2, as4h1), subnets=('dead:beef::/32',))

        """al4 = AccessList(name='all4', entries=('any',), family='ipv4')
        al6 = AccessList(name='all6', entries=('any',), family='ipv6')

        as1r6.get_config(BGP)\
            .set_local_pref(99, from_peer=as4r1, matching=(al4, al6))\
            .set_med(50, to_peer=as4r1, matching=(al4, al6))

        as4r1.get_config(BGP)\
            .set_community('1:80', from_peer=as1r6, matching=(al4, al6))\
            .set_med(50, to_peer=as1r6, matching=(al4, al6))

        as1r5.get_config(BGP).set_local_pref(50, from_peer=as4r2,
                                             matching=(al4, al6))"""

        # Add full mesh
        self.addAS(4, (as4r1, as4r2))
        self.addAS(1, (as1r1, as1r2, as1r3, as1r4, as1r5, as1r6))
        set_rr(self, rr=as1r3, peers=(as1r1, as1r2, as1r4, as1r5, as1r6))

        # Add eBGP session
        ebgp_session(self, as1r6, as4r1)
        ebgp_session(self, as1r5, as4r2)

        super().build(*args, **kwargs)

    def bgp(self, name, family=AF_INET6()):
        r = self.addRouter(name)
        r.addDaemon(BGP, address_families=(family,))
        return r
    
    def post_build(self, net):
        for n in net.hosts + net.routers:
            interfaces = ["all", "lo", "default", str(n)+"-eth0"]
            # enable_srv6(n)
            for i in interfaces:
                result = n.cmd("sysctl net.ipv6.conf."+i+".seg6_enabled=1")
                #print(result)
                result = n.cmd("sysctl net.ipv6.conf."+i+".seg6_require_hmac=-1")
                #print(result)
        for r in net.routers:
            r.cmd("python3 lookup_bgp_table.py &")
        # result = net.get("as1r1").cmd("ip -6 route add fc00:0:7::2 encap seg6 mode inline segs fc00:0:d::1 dev as1r1-eth0")
        # print(result)
    
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