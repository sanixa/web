from content.models import ovs1,ovs2,ns1,ns2
import os

def create():
    if set(ovs1.objects.all()) == set([]) or set(ovs2.objects.all()) == set([]) or set(ns1.objects.all()) == set([]) or set(ns2.objects.all()) == set([]):
        return "no data"
    else:
        ovs1_content = ovs1.objects.all()[0]
        ovs2_content = ovs2.objects.all()[0]
        ns1_content = ns1.objects.all()[0]
        ns2_content = ns2.objects.all()[0]
        c = "sudo ovs-vsctl add-br " + ovs1_content.name
        os.system(c)
        c = "sudo ovs-vsctl add-port " + ovs1_content.name + " " + ovs1_content.port
        os.system(c)
        c = "sudo ovs-vsctl set Interface " + ovs1_content.port + " type=internal ofport_request=" + ovs1_content.number
        os.system(c)
        c = "sudo ip netns add " + ns1_content.name
        os.system(c)
        c = "sudo ip link set " + ovs1_content.port + " netns " + ns1_content.name
        os.system(c)
        c = "sudo ip netns exec " + ns1_content.name + " ip addr add " + ns1_content.address + " dev " + ovs1_content.port
        os.system(c)
        c = "sudo ip netns exec " + ns1_content.name + " ifconfig " + ovs1_content.port + " promisc up"
        os.system(c)


        c = "sudo ovs-vsctl add-br " + ovs2_content.name
        os.system(c)
        c = "sudo ovs-vsctl add-port " + ovs2_content.name + " " + ovs2_content.port
        os.system(c)
        c = "sudo ovs-vsctl set Interface " + ovs2_content.port + " type=internal ofport_request=" + ovs2_content.number
        os.system(c)
        c = "sudo ip netns add " + ns2_content.name
        os.system(c)
        c = "sudo ip link set " + ovs2_content.port + " netns " + ns2_content.name
        os.system(c)
        c = "sudo ip netns exec " + ns2_content.name + " ip addr add " + ns2_content.address + " dev " + ovs2_content.port
        os.system(c)
        c = "sudo ip netns exec " + ns2_content.name + " ifconfig " + ovs2_content.port + " promisc up"
        os.system(c)


        c = "sudo ovs-vsctl add-port " + ovs1_content.name + " patch1"
        os.system(c)
        c = "sudo ovs-vsctl set interface patch1 type=patch"
        os.system(c)
        c = "sudo ovs-vsctl add-port " + ovs2_content.name + " patch2"
        os.system(c)
        c = "sudo ovs-vsctl set interface patch2 type=patch"
        os.system(c)
        c = "ovs-vsctl set interface patch1 options:peer=patch2"
        os.system(c)
        c = "ovs-vsctl set interface patch2 options:peer=patch1"
        os.system(c)

        return "success"

def delete():
    if set(ovs1.objects.all()) == set([]) or set(ovs2.objects.all()) == set([]) or set(ns1.objects.all()) == set([]) or set(ns2.objects.all()) == set([]):
        return "no data"
    else:
        ovs1_content = ovs1.objects.all()[0]
        ovs2_content = ovs2.objects.all()[0]
        ns1_content = ns1.objects.all()[0]
        ns2_content = ns2.objects.all()[0]
        c = "sudo ovs-vsctl del-br " + ovs1_content.name
        os.system(c)
        c = "sudo ovs-vsctl del-br " + ovs2_content.name
        os.system(c)
        c = "sudo ip netns del " + ns1_content.name
        os.system(c)
        c = "sudo ip netns del " + ns2_content.name
        os.system(c)

        return "success"

