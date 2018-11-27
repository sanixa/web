from content.models import ovs1,ovs2,ns1,ns2
import os
import queue
from threading import Thread,Semaphore
import multiprocessing as mp
import subprocess as sub
s1=None
s2=None

def create():
    if set(ovs1.objects.all()) == set([]) or set(ovs2.objects.all()) == set([]) or set(ns1.objects.all()) == set([]) or set(ns2.objects.all()) == set([]):
        return "no data"
    else:
        ovs1_content = ovs1.objects.all()[0]
        ovs2_content = ovs2.objects.all()[0]
        ns1_content = ns1.objects.all()[0]
        ns2_content = ns2.objects.all()[0]
        c = "sudo ovs-vsctl --may-exist add-br " + ovs1_content.name
        os.system(c)
        c = "sudo ovs-vsctl --may-exist add-port " + ovs1_content.name + " " + ovs1_content.port
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
        c = "sudo ip netns exec " + ns1_content.name + " ifconfig " + ovs1_content.port + " netmask 255.255.255.0"
        os.system(c)


        c = "sudo ovs-vsctl --may-exist add-br " + ovs2_content.name
        os.system(c)
        c = "sudo ovs-vsctl --may-exist add-port " + ovs2_content.name + " " + ovs2_content.port
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
        c = "sudo ip netns exec " + ns2_content.name + " ifconfig " + ovs2_content.port + " netmask 255.255.255.0"
        os.system(c)


        c = "sudo ovs-vsctl --may-exist add-port " + ovs1_content.name + " patch1"
        os.system(c)
        c = "sudo ovs-vsctl set interface patch1 type=patch"
        os.system(c)
        c = "sudo ovs-vsctl --may-exist add-port " + ovs2_content.name + " patch2"
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
        c = "sudo ovs-vsctl --if-exist del-br " + ovs1_content.name
        os.system(c)
        c = "sudo ovs-vsctl --if-exist del-br " + ovs2_content.name
        os.system(c)
        c = "sudo ip netns del " + ns1_content.name
        os.system(c)
        c = "sudo ip netns del " + ns2_content.name
        os.system(c)

        return "success"

def content():
    #q = queue.Queue()
    #s1 = Semaphore(0)
    #s2 = Semaphore(1)
    t1 = Thread(target=_receive)
    t2 = Thread(target=_send)
    t1.start()
    t2.start()
    #output = sub.check_output('sudo ip netns exec ns11 ping -c 1 192.168.1.101', shell=True)
    t2.join()
    t1.join()
    ctx = { }
    global s1,s2
    ctx['send_o'] = s1
    ctx['rec_o'] = s2
    
    ovs1_content = ovs1.objects.all()[0]
    ovs2_content = ovs2.objects.all()[0]
    ns1_content = ns1.objects.all()[0]
    ns2_content = ns2.objects.all()[0]
    c = 'sudo ovs-appctl ofproto/trace ' + ovs1_content.name + ' in_port=' + ovs1_content.number + ' -generate'
    output = sub.check_output(c, shell=True)
    str1 = "actions"
    output = output.decode()
    output = output.replace(' ', '')
    ctx['ovs1_detail'] = output.replace('\n', '<br>')
    output = output[output.find(str1) - 9:output.find('\n',output.find(str1))]
    ctx['ovs1_output'] = output
    c = 'sudo ip netns exec ' + ns2_content.name + ' ifconfig | grep HWaddr'
    temp = sub.check_output(c, shell=True)
    temp = temp[len(temp)-20:len(temp)-3]
    c = 'sudo ovs-appctl ofproto/trace ' + ovs2_content.name + ' in_port=1,dl_dst=' + temp.decode() + ' -generate'
    output = sub.check_output(c, shell=True)
    output = output.decode()
    output = output.replace(' ', '')
    ctx['ovs2_detail'] = output.replace('\n', '<br>')
    output = output[output.find(str1) - 9:output.find('\n',output.find(str1))]
    ctx['ovs2_output'] = output

    return ctx

def created():
    ovs1_content = ovs1.objects.all()[0]
    ovs2_content = ovs2.objects.all()[0]
    ns1_content = ns1.objects.all()[0]
    ns2_content = ns2.objects.all()[0]
    output1 = sub.check_output('sudo ovs-vsctl show' , shell=True)
    output2 = sub.check_output('sudo ip netns' , shell=True)
    output1 = output1.decode()
    output2 = output2.decode()
    if output1.find("Bridge \"" + ovs1_content.name + "\"") == -1 or output1.find("Bridge \"" + ovs2_content.name + "\"") == -1:
        return False
    elif output2.find(ns1_content.name) == -1 or output2.find(ns2_content.name):
        return False
    else:
        return True

def _send():
    global s1
    ns1_content = ns1.objects.all()[0]
    ns2_content = ns2.objects.all()[0]
    if ns2_content.address.find('/') != -1:
        ns2_content.address = ns2_content.address[:ns2_content.address.find('/')]
    c = 'sudo ip netns exec ' + ns1_content.name + ' ping -c 1 ' + ns2_content.address
    s1 = sub.check_output(c , shell=True)
   

def _receive():
    global s2
    ovs2_content = ovs2.objects.all()[0]
    ns2_content = ns2.objects.all()[0]
    c = 'sudo ip netns exec ' + ns2_content.name + ' tcpdump -i ' + ovs2_content.port + ' -c 1 icmp'
    s2 = sub.check_output(c, shell=True)
    


