""" Test program for multi-interface host, static routing

         Destination host (10.20.1.2)
                 |
                 | 10.20.1.0/24
              DSTRTR
  10.10.1.0/24 /   \  10.10.2.0/24
              / \
           Rtr1    Rtr2
 10.1.1.0/24 |      | 10.1.2.0/24
             |      /
              \    /
             Source
"""

from core.ns3.Experiment import *
from ns3 import *
from core.ns3.Node import *

class ImalseSimExperiment(ImalseExperiment):
    """This is a small ns-3 Experiment with only simulated node"""

    def initparser(self, parser):
        super(ImalseSimExperiment, self).initparser(parser)
        scenario_ops = get_scenario_option()
        parser.add_option('-s', '--scenario', dest="scenario",
                default='ddos_ping_flooding',
                help='specify the scenario you want to execute. Scenearios availiable are: %s'%(scenario_ops),
                )

    def get_node(self, i):
        return self.nodes[i]
    @property
    def node_num(self):
        return len(self.nodes)

    def create_sim(self):
        # nSrc = Node(); nDst = Node(); nRtr1 = Node(); nRtr2 = Node(); nDstRtr = Node()
        self.nodes = [ImalseNetnsSimNode() for i in xrange(5)]
        nSrc, nDst, nRtr1, nRtr2, nDstRtr = self.nodes

        # install Internet Stack
        c = NodeContainer()
        for node in self.nodes:
            c.Add(node)
        internet = InternetStackHelper()
        internet.Install(c)

        # Point to Point Links
        nSrcnRtr1 = NodeContainer(NodeContainer(nSrc), NodeContainer(nRtr1))
        nSrcnRtr2 = NodeContainer(NodeContainer(nSrc), NodeContainer(nRtr2))
        nRtr1nDstRtr = NodeContainer(NodeContainer(nRtr1), NodeContainer(nDstRtr))
        nRtr2nDstRtr = NodeContainer(NodeContainer(nRtr2), NodeContainer(nDstRtr))
        nDstRtrnDst = NodeContainer(NodeContainer(nDstRtr), NodeContainer(nDst))

        p2p = PointToPointHelper()
        p2p.SetDeviceAttribute("DataRate", StringValue("5Mbps"))
        p2p.SetChannelAttribute("Delay", StringValue("2ms"))
        dSrcdRtr1 = p2p.Install (nSrcnRtr1)
        dSrcdRtr2 = p2p.Install (nSrcnRtr2)
        dRtr1dDstRtr = p2p.Install (nRtr1nDstRtr)
        dRtr2dDstRtr = p2p.Install (nRtr2nDstRtr)
        dDstRtrdDst = p2p.Install (nDstRtrnDst)

        SrcToRtr1=dSrcdRtr1.Get (0);
        SrcToRtr2=dSrcdRtr2.Get (0);

        #Later, we add IP addresses.
        ipv4 = Ipv4AddressHelper()
        ipv4.SetBase (Ipv4Address("10.1.1.0"), Ipv4Mask("255.255.255.0"));
        iSrciRtr1 = ipv4.Assign (dSrcdRtr1);
        ipv4.SetBase (Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"));
        iSrciRtr2 = ipv4.Assign (dSrcdRtr2);
        ipv4.SetBase (Ipv4Address("10.10.1.0"), Ipv4Mask("255.255.255.0"));
        iRtr1iDstRtr = ipv4.Assign (dRtr1dDstRtr);
        ipv4.SetBase (Ipv4Address("10.10.2.0"), Ipv4Mask("255.255.255.0"));
        iRtr2iDstRtr = ipv4.Assign (dRtr2dDstRtr);
        ipv4.SetBase (Ipv4Address("10.20.1.0"), Ipv4Mask("255.255.255.0"));
        iDstRtrDst = ipv4.Assign (dDstRtrdDst);

        def print_member(cls):
            from inspect import getmembers
            vm = getmembers(cls)
            for m in vm: print 'method, ', m

        ipv4Src = nSrc.GetObject(Ipv4.GetTypeId())
        ipv4Rtr1 = nRtr1.GetObject(Ipv4.GetTypeId())
        ipv4Rtr2 = nRtr2.GetObject(Ipv4.GetTypeId())
        ipv4DstRtr = nDstRtr.GetObject(Ipv4.GetTypeId())
        ipv4Dst = nDst.GetObject(Ipv4.GetTypeId())

        ipv4RoutingHelper = Ipv4StaticRoutingHelper()
        staticRoutingSrc = ipv4RoutingHelper.GetStaticRouting (ipv4Src);
        staticRoutingRtr1 = ipv4RoutingHelper.GetStaticRouting (ipv4Rtr1);
        staticRoutingRtr2 = ipv4RoutingHelper.GetStaticRouting (ipv4Rtr2);
        staticRoutingDstRtr = ipv4RoutingHelper.GetStaticRouting (ipv4DstRtr);
        staticRoutingDst = ipv4RoutingHelper.GetStaticRouting (ipv4Dst);

        # Create static routes from Src to Dst
        staticRoutingRtr1.AddHostRouteTo (Ipv4Address ("10.20.1.2"), Ipv4Address ("10.10.1.2"), 2);
        staticRoutingRtr2.AddHostRouteTo (Ipv4Address ("10.20.1.2"), Ipv4Address ("10.10.2.2"), 2);

        #Two routes to same destination - setting separate metrics.
        #You can switch these to see how traffic gets diverted via different routes
        staticRoutingSrc.AddHostRouteTo (Ipv4Address ("10.20.1.2"), Ipv4Address ("10.1.1.2"), 1,5);
        staticRoutingSrc.AddHostRouteTo (Ipv4Address ("10.20.1.2"), Ipv4Address ("10.1.2.2"), 2,10);

        # Creating static routes from DST to Source pointing to Rtr1 VIA Rtr2(!)
        staticRoutingDst.AddHostRouteTo (Ipv4Address ("10.1.1.1"), Ipv4Address ("10.20.1.1"), 1);
        staticRoutingDstRtr.AddHostRouteTo (Ipv4Address ("10.1.1.1"), Ipv4Address ("10.10.2.1"), 2);
        staticRoutingRtr2.AddHostRouteTo (Ipv4Address ("10.1.1.1"), Ipv4Address ("10.1.2.1"), 1);

    def setup(self):
        print 'setup'
        self.create_sim()
        self._install_cmds()
        self._set_server_info()

        # start servers
        for i in self.server_id_set:
            self.event(0, self.node_run, self.get_node(i), 'start')

        # start clients
        t = 0
        for i in self.client_id_set:
            t += 1
            self.event(t, self.node_run, self.get_node(i), 'start')

        # start botmaster
        for i in self.botmaster_id_set:
            self.event(t+1, self.node_run, self.get_node(i), 'start')
