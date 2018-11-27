import os
import sys
import subprocess
import json
import shlex
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import content.command.veri_flow as flow
from content.models import command
TEMPFILE = "content/command/temp.xml"
USERNAME = "admin"
PASSWORD = "admin"
ODL_HOST = "localhost"
INTERFACE = "ens33"
BRIDGE_NAME = "my-br"

def init():
    global USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME,INTERFACE
    if set(command.objects.all()) == set([]):
        return "no data"
    else:
        c = command.objects.all()[0]
        USERNAME = c.user
        PASSWORD = c.passwd
        ODL_HOST = c.address
        BRIDGE_NAME = c.bridge
        INTERFACE = c.interface
        return "correct"
        
def br_id_find():
    global USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME
    command = "curl -X GET --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operational/opendaylight-inventory:nodes/"
    output = subprocess.check_output(command, shell=True)
    output2 = subprocess.check_output(command , shell=True)
    j = json.loads(output.decode('utf-8'))
    x,y = 0,0
    name = ""
    for x in range(10000):
        for y in range(10000):
            try:
                name = j['nodes']['node'][x]['node-connector'][y]['flow-node-inventory:name']
            except IndexError:
                break
            else:
                if name == BRIDGE_NAME:
                    t = j['nodes']['node'][x]['id']
                    return t[t.find(":")+1:]
        try:
            name = j['nodes']['node'][x+1]['node-connector'][0]['flow-node-inventory:name']
        except IndexError:
            return "error"
        
   
def br_id_set():
    with open(TEMPFILE, "r+") as f:
        content = f.read()
        temp = content.find("openflow")
        t1 = content.find(":",temp)
        t2 = content.find("\"",temp)
        t = br_id_find()
        if t == "error":
            return "error"
        else:
            content = content[:t1+1] + t + content[t2:]
        f.seek(0,0)
        os.system("echo " + shlex.quote(content) + " > content/command/temp.xml")
        #print(content)
        #f.write(content)

def xml(filename, col, content):
    ET.register_namespace('',"urn:opendaylight:flow:service")
    tree = ET.ElementTree(file=filename)
    for elem in tree.iter():
        if elem.tag == "{urn:opendaylight:flow:service}node":
            elem.attrib={"xmlns:inv":"urn:opendaylight:inventory"}
        if elem.tag == "{urn:opendaylight:flow:service}" + col:
            elem.text = content
    global TEMPFILE
    tree.write(TEMPFILE)
    with open(TEMPFILE, "r+") as f:
        content = f.read()
        f.seek(0,0)
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n" + content)

def xml2(filename, col1, col2, content):  #col1 out col2 in
    ET.register_namespace('',"urn:opendaylight:flow:service")
    tree = ET.ElementTree(file=filename)
    bo = 0
    for elem in tree.iter():
        if elem.tag == "{urn:opendaylight:flow:service}node":
            elem.attrib={"xmlns:inv":"urn:opendaylight:inventory"}
        if bo == 1 and elem.tag == "{urn:opendaylight:flow:service}" + col2:
            elem.text = content
            bo = 0
        if elem.tag == "{urn:opendaylight:flow:service}" + col1:
            bo = 1
    global TEMPFILE
    tree.write(TEMPFILE)
    with open(TEMPFILE, "r+") as f:
        content = f.read()
        f.seek(0,0)
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n" + content)

def modifity(key,action):
    xml("content/command/add.xml", key, action)
    if br_id_set() == "error":
        return "xml file error"

    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows ' + BRIDGE_NAME)
    result = flow._verification(xdict, ftable, count)
    return result

def no_modifity(key,action):
    xml("content/command/add.xml", key, action)
    if br_id_set() == "error":
        return "xml file error"
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows ' + BRIDGE_NAME)
    if ftable == "":
        return "correct"
    result = "correct" if flow._verification(xdict, ftable, count) == "error" else "error"
    return result

def modifity_2l(key1, key2, action):
    xml2("add.xml", key1, key2, action)
    if br_id_set() == "error":
        return "xml file error"
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows '+ BRIDGE_NAME)
    result = flow._verification(xdict, ftable, count)
    return result

def no_modifity_2l(key1, key2,action):
    xml2("add.xml", key1, key2, action)
    if br_id_set() == "error":
        return "xml file error"
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows ' + BRIDGE_NAME)
    if ftable == "":
        return "correct"
    result = "correct" if flow._verification(xdict, ftable, count) == "error" else "error"
    return result

def switch(arg):
    global BRIDGE_NAME,ODL_HOST
    os.system("ovs-vsctl add-br " + BRIDGE_NAME)
    os.system("ovs-vsctl add-port " + BRIDGE_NAME + " " + BRIDGE_NAME)
    os.system("ovs-vsctl set-controller " + BRIDGE_NAME + " tcp:" + ODL_HOST + ":6633")
    s = "ovs-vsctl set bridge " + BRIDGE_NAME +" other-config:datapath-id=" + str(arg)
    os.system(s)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "datapath-id=\"" + arg + "\"" in line:
            return "correct"
    return "error"

def no_switch(dpid):
    global BRIDGE_NAME 
    s = "ovs-vsctl del-br " + BRIDGE_NAME
    os.system(s)

    s = "ovs-vsctl show > temp"
    os.system(s)
    f = open('temp', 'r')
    for line in f:
        if line.find(BRIDGE_NAME) != -1:
            return "error"
    return "correct"

def active(act):
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST,BRIDGE_NAME
    if act == "True" or act == "true":
        command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
        os.system(command)

        xdict = flow._xml2dict(TEMPFILE)
        ftable,count = flow._flow_data('ovs-ofctl dump-flows '+ BRIDGE_NAME)
        result = flow._verification(xdict, ftable, count)
        return result

    elif act == "False" or act == "false":
        command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
        os.system(command)

        xdict = flow._xml2dict(TEMPFILE)
        ftable,count = flow._flow_data('ovs-ofctl dump-flows ' + BRIDGE_NAME)
        if ftable == "":
            return "correct"
        result = "correct" if flow._verification(xdict, ftable, count) == "error" else "error"
        return result
    else:
        return "parameter error"


def switchport_mode(interface):
    command = "ovs-vsctl set Interface " + interface + " type=external"
    os.system(command)

    command = "ovs-vsctl list Interface " + interface + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "type" in line and "external" in line:
            return "correct"
    return "error"

def no_switchport_mode(interface):
    command = "ovs-vsctl set Interface " + interface + " type=internal"
    os.system(command)

    command = "ovs-vsctl list Interface " + interface + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "type" in line and "internal" in line:
            return "correct"
    return "error"

def core_switch():
    global BRIDGE_NAME
    command = "ovs-vsctl set bridge "+ BRIDGE_NAME + " other-config:core-switch=true"
    os.system(command)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)

    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "core-switch=\"true\"" in line:
            return "correct"
    return "error"

def no_core_switch():
    global BRIDGE_NAME
    command = "ovs-vsctl remove bridge " + BRIDGE_NAME + " other-config core-switch"
    os.system(command)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "core-switch" in line:
            return "error"
    return "correct"

def interface(interface):
    global BRIDGE_NAME
    command = "ovs-vsctl add-port " + BRIDGE_NAME + " " + interface
    os.system(command)

    command = "ovs-vsctl list-ports " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if interface in line:
            return "correct"
    return "error"

def no_interface(interface):
    global BRIDGE_NAME
    command = "ovs-vsctl del-port " + BRIDGE_NAME + " " + interface
    os.system(command)

    command = "ovs-vsctl list-ports " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if interface in line:
            return "error"
    return "correct"

def interface_alias(name):
    global INTERFACE
    command = "ovs-vsctl set Interface " + INTERFACE + " other-config:alias=" + name
    os.system(command)

    command = "ovs-vsctl list Interface "+ INTERFACE + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "alias=\"" + name + "\"" in line:
            return "correct"
    return "error"

def no_interface_alias(name):
    global INTERFACE
    command = "ovs-vsctl remove Interface " + INTERFACE + " other-config alias"
    os.system(command)

    command = "ovs-vsctl list Interface "+ INTERFACE + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "alias" in line:
            return "error"
    return "correct"

def switch_alias(name):
    global BRIDGE_NAME
    command = "ovs-vsctl set bridge " + BRIDGE_NAME + " other-config:alias=" + name
    os.system(command)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "alias=\"" + name + "\"" in line:
            return "correct"
    return "error"

def no_switch_alias(name):
    global BRIDGE_NAME
    command = "ovs-vsctl remove bridge " + BRIDGE_NAME + " other-config alias"
    os.system(command)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "alias" in line:
            return "error"
    return "correct"

def tunnel_termination(arg):
    global BRIDGE_NAME
    command = "ovs-vsctl set bridge " + BRIDGE_NAME + " other-config:tunnel=" + arg
    os.system(command)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "tunnel=\"" + arg + "\"" in line:
            return "correct"
    return "error"

def no_tunnel_termination():
    global BRIDGE_NAME
    command = "ovs-vsctl remove bridge " + BRIDGE_NAME + " other-config tunnel"
    os.system(command)

    command = "ovs-vsctl list bridge " + BRIDGE_NAME + " > temp"
    os.system(command)
    f = open('temp', 'r')
    for line in f:
        if "other_config" in line and "tunnel" in line:
            return "error"
    return "correct"




def main(p1, p2):
    ##if set src-port or dst-port ,ip protocol must be 6
    ## ipv4-source and ipv4-destination must be x.x.x.x/32
    cmd = p1
    arg = p2
    result = ""
    if cmd == "switch":
        result = switch(arg)
    elif cmd == "no switch":
        result = no_switch(arg)
    elif cmd == "action":
        result = modifity("output-node-connector",arg)
    elif cmd == "no action":
        result = no_modifity("output-node-connector",arg)
    elif cmd == "active":
        result = active(arg)
    elif cmd == "cookie":
        result = modifity("cookie",arg)
    elif cmd == "no cookie":
        result = no_modifity("cookie",arg)
    elif cmd == "dst-ip":
        result = modifity("ipv4-destination",arg)
    elif cmd == "no dst-ip":
        result = no_modifity("ipv4-destination",arg)
    elif cmd == "dst-mac":
        result = modifity_2l("ethernet-destination", "address",arg)
    elif cmd == "no dst-mac":
        result = no_modifity_2l("ethernet-destination", "address",arg)
    elif cmd == "dst-port":  
        if arg == "http":
            arg = "80"
        elif arg == "dns":
            arg = "53"
        elif arg == "https":
            arg = "443"
        elif arg == "ssh":
            arg = "22"
        result = modifity("tcp-destination-port",arg) 
    elif cmd == "no dst-port":
        if arg == "http":
            arg = "80"
        elif arg == "dns":
            arg = "53"
        elif arg == "https":
            arg = "443"
        elif arg == "ssh":
            arg = "22"
        result = no_modifity("tcp-destination-port",arg)
    elif cmd == "ether-type":
        if arg == "arp":
            arg = "2054"
        elif arg == "lldp":
            arg = "35020"
        elif arg == "802.1Q":
            arg = "33024"
        elif arg == "ip":
            arg = "2048"
        elif arg == "mpls":
            arg = "34887"
        elif arg == "rarp":
            arg = "32821"
        elif arg == "mpls-mc":
            arg = "34888"
        elif arg == "appletalk-aarp":
            arg = "33011"
        elif arg == "ipv6":
            arg = "34525"
        elif arg == "novell":
            arg = "33080"
        elif arg == "ipx":
            arg = "33079"
        result = modifity_2l("ethernet-type", "type",arg)
    elif cmd == "no ether-type":
        if arg == "arp":
            arg = "2054"
        elif arg == "lldp":
            arg = "35020"
        elif arg == "802.1Q":
            arg = "33024"
        elif arg == "ip":
            arg = "2048"
        elif arg == "mpls":
            arg = "34887"
        elif arg == "rarp":
            arg = "32821"
        elif arg == "mpls-mc":
            arg = "34888"
        elif arg == "appletalk-aarp":
            arg = "33011"
        elif arg == "ipv6":
            arg = "34525"
        elif arg == "novell":
            arg = "33080"
        elif arg == "ipx":
            arg = "33079"
        result = no_modifity_2l("ethernet-type", "type",arg)
    elif cmd == "hard-timeout":
        result = modifity("hard-timeout",arg)
    elif cmd == "no hard-timeout":
        result = no_modifity("hard-timeout",arg)
    elif cmd == "idle-timeout":
        result = modifity("idle-timeout",arg)
    elif cmd == "no idle-timeout":
        result = no_modifity("idle-timeout",arg)
    elif cmd == "ingress-port":
        result = modifity("in-port",arg)
    elif cmd == "no ingress-port":
        result = no_modifity("in-port",arg)
    elif cmd == "priority":
        result = modifity("priority",arg)
    elif cmd == "no priority":
        result = no_modifity("priority",arg)
    elif cmd == "protocol":
        result = modifity("ip-protocol",arg)
    elif cmd == "no protocol":
        result = no_modifity("ip-protocol",arg)
    elif cmd == "src-ip":
        result = modifity("ipv4-source",arg)
    elif cmd == "no src-ip":
        result = no_modifity("ipv4-source",arg)
    elif cmd == "src-mac":
        result = modifity_2l("ethernet-source", "address",arg)
    elif cmd == "no src-mac":
        result = no_modifity_2l("ethernet-source", "address",arg)
    elif cmd == "src-port":
        if arg == "http":
            arg = "80"
        elif arg == "dns":
            arg = "53"
        elif arg == "https":
            arg = "443"
        elif arg == "ssh":
            arg = "22"
        result = modifity("tcp-source-port",arg)
    elif cmd == "no src-port":
        if arg == "http":
            arg = "80"
        elif arg == "dns":
            arg = "53"
        elif arg == "https":
            arg = "443"
        elif arg == "ssh":
            arg = "22"
        result = no_modifity("tcp-source-port",arg)
    elif cmd == "tos-bits":
        result = modifity("ip-dscp",arg)
    elif cmd == "no tos-bits":
        result = no_modifity("ip-dscp",arg)
    elif cmd == "vlan-id":
        result = modifity_2l("vlan-id", "vlan-id",arg)
    elif cmd == "no vlan-id":
        result = no_modifity_2l("vlan-id", "vlan-id",arg)
    elif cmd == "vlan-priority":
        result = modifity("vlan-pcp",arg)
    elif cmd == "no vlan-priority":
        result = no_modifity("vlan-pcp",arg)
    elif cmd == "wildcards":  
        result = "correct"
    elif cmd == "no wildcards":
        result = "correct"
    elif cmd == "flow-entry":
        result = modifity("flow-name",arg)
    elif cmd == "no flow-entry":
        result = no_modifity("flow-name",arg)
    elif cmd == "switchport mode":
        result = switchport_mode(arg)
    elif cmd == "no switchport mode":
        result = no_switchport_mode(arg)
    elif cmd == "core-switch":
        result = core_switch()
    elif cmd == "no core-switch":
        result = no_core_switch()
    elif cmd == "interface":
        result = interface(arg)
    elif cmd == "no interface":
        result = no_interface(arg)
    elif cmd == "interface-alias":
        result = interface_alias(arg)
    elif cmd == "no interface-alias":
        result = no_interface_alias(arg)
    elif cmd == "switch-alias":
        result = switch_alias(arg)
    elif cmd == "no switch-alias":
        result = no_switch_alias(arg)
    elif cmd == "tunnel termination":
        result = tunnel_termination(arg)
    elif cmd == "no tunnel termination":
        result = no_tunnel_termination()
    else:
        return "no such command or syntax error"
    return result
#if __name__ == "__main__":
   # br_id_set()
