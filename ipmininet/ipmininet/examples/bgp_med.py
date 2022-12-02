from ipmininet.iptopo import IPTopo
from ipmininet.router.config import BGP, ebgp_session, AccessList, AF_INET6


class BGPTopoMed(IPTopo):
    """This topology is composed of two AS connected in dual homing
     with a higher MED for routes from as4r1 than from as4r2.
     Thus, all the traffic coming from AS1 will go through the link
     between as1r5 and as4r2."""

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
        as4h1 = self.addHost('as4h1')
        switch = self.addSwitch('s4')

        # Add Links
        self.addLink(as1r1, as1r6)
        self.addLink(as1r1, as1r3, igp_metric=2)
        self.addLinks((as1r3, as1r2), (as1r3, as1r6))
        self.addLink(as1r2, as1r4, igp_metric=4)
        self.addLinks((as1r4, as1r5), (as1r5, as1r6), (as4r1, as1r6),
                      (as4r2, as1r5), (as4r1, switch), (as4r2, switch),
                      (switch, as4h1))
        self.addSubnet((as4r1, as4r2, as4h1), subnets=('dead:beef::/32',))

        al4 = AccessList(name='all4', entries=('any',), family='ipv4')
        al6 = AccessList(name='all6', entries=('any',), family='ipv6')
        as4r1.get_config(BGP).set_med(99, to_peer=as1r6, matching=(al4, al6))
        as4r2.get_config(BGP).set_med(50, to_peer=as1r5, matching=(al4, al6))

        # Add full mesh
        self.addAS(4, (as4r1, as4r2))
        self.addiBGPFullMesh(1, (as1r1, as1r2, as1r3, as1r4, as1r5, as1r6))

        # Add eBGP session
        ebgp_session(self, as1r6, as4r1)
        ebgp_session(self, as1r5, as4r2)

        super().build(*args, **kwargs)

    def bgp(self, name, family=AF_INET6()):
        r = self.addRouter(name)
        r.addDaemon(BGP, address_families=(family,))
        return r
