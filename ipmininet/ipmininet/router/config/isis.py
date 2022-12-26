"""Base classes to configure an OSPF daemon"""
from ipaddress import ip_interface, IPv4Network
from typing import Sequence, List

from ipmininet.link import IPIntf
from ipmininet.overlay import Overlay
from ipmininet.utils import L3Router
from .utils import ConfigDict
from .zebra import QuaggaDaemon, Zebra

class ISIS(QuaggaDaemon):
    """This class enable an ISIS daemon."""

    NAME = 'isisd'
    DEPENDS = (Zebra,)
    KILL_PATTERNS = (NAME,)

    def __init__(self, node, *args, **kwargs):
        super().__init__(node=node, *args, **kwargs)

    def build(self):
        cfg = super().build()
        # cfg.redistribute = self.options.redistribute
        # interfaces = self._node.intfList()
        # cfg.interfaces = self._build_interfaces(interfaces)
        # cfg.networks = self._build_networks(interfaces)
        return cfg

    # @staticmethod
    # def _build_networks(interfaces: List[IPIntf]) -> List['OSPFNetwork']:
    #     """Return the list of OSPF networks to advertize from the list of
    #     active OSPF interfaces"""
    #     # Check that we have at least one IPv4 network on that interface ...
    #     return [OSPFNetwork(domain=ip_interface('%s/%s' % (i.ip, i.prefixLen)),
    #                         area=i.igp_area) for i in interfaces if i.ip]

    # def _build_interfaces(self, interfaces: List[IPIntf]) -> List[ConfigDict]:
    #     """Return the list of ISIS interface properties from the list of
    #     active interfaces"""
    #     return [ConfigDict(description=i.describe,
    #                        name=i.name,
    #                        # Is the interface between two routers?
    #                        active=self.is_active_interface(i),
    #                        priority=i.get('ospf_priority',
    #                                       self.options.priority),
    #                        dead_int=i.get('ospf_dead_int',
    #                                       self.options.dead_int),
    #                        hello_int=i.get('ospf_hello_int',
    #                                        self.options.hello_int),
    #                        cost=i.igp_metric,
    #                        # Is the interface forcefully disabled?
    #                        passive=i.get('igp_passive', False))
    #             for i in interfaces]