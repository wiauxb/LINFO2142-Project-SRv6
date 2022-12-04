from ipmininet.iptopo import IPTopo
from ipmininet.router.config import SSHd, BGP, AF_INET6, ebgp_session, CLIENT_PROVIDER, SHARE,  BorderRouterConfig
from ipmininet.host.config import Named
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet import DEBUG_FLAG
from ipmininet.srv6 import enable_srv6
from ipmininet.srv6 import SRv6Encap
from time import sleep

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        as1r1 = self.bgp('as1r1')
        as1r2 = self.bgp('as1r2', family=AF_INET6(redistribute=('ospf6', 'connected')))
        as2r1 = self.bgp('as2r1', family=AF_INET6(redistribute=('ospf6', 'connected')))
        as2r2 = self.bgp('as2r2')
        as2r3 = self.bgp('as2r3')

        as1h1 = self.addHost('as1h1')
        as2h1 = self.addHost('as2h1')
        
        self.addLinks((as1r1, as1r2), (as1r2, as2r1), (as2r1, as2r2), (as2r1, as2r3), (as1r1, as1h1), (as2r3, as2h1))
    

        # Set AS-ownerships
        self.addiBGPFullMesh(1, (as1r1, as1r2))
        self.addiBGPFullMesh(2, (as2r1, as2r2, as2r3))

        # Add eBGP peering
        ebgp_session(self, as1r2, as2r1)
            
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
        # result = net.get("has1r1").cmd("ip -6 route add fc00:0:7::2 encap seg6 mode inline segs fc00:0:d::1 dev has1r1-eth0")
        super().post_build(net)
        #print(result)
    
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

def rtt_measurement(net):
    h1 = net.get('as1h1')
    h2 = net.get('as2h1')    
    rtt_mean=[]
    rtt=[]
    for x in range(5) :
        result = net.ping(hosts=[h1, h2], timeout="3", use_v4=False)
        print(result)
        if(result!=0):
            rtt.append(float(result))
    rtt_mean=(sum(rtt)/len(rtt))
    print(rtt_mean)
    return rtt_mean

def perfTest(net):
    h1, h4 = net.get( 'as1h1', 'as2h1' )
    # h1.setIP('fc00:0:1::2')
    # print(h1.cmd("ifconfig"))
    result = h1.cmd("iperf3 -s &")
    # print(result)
    sleep(10)
    result = h4.cmd("iperf3 -c fc00:0:1::2 >> doubleAsPerf_srv6.txt")
    # print(result)

if __name__ == "__main__":
    
    net = IPNet(topo=MyTopology(), use_v4=False)
    # DEBUG_FLAG = True
    try:
        net.start()
        # sleep(10)
        # for i in range(10):
        #     perfTest(net)
        IPCLI(net)
    finally:
        net.stop()

    #sudo python -m ipmininet.clean --> si ça crash ou qu'on oublie de net.stop()