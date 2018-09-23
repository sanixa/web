from django.shortcuts import render
from django.views.decorators import csrf
import content.modsecurity.func as mod
import content.route.func as r
from content.models import ovs1,ovs2,ns1,ns2
import subprocess as sub
import os,time
import queue
from threading import Thread
# Create your views here.

def modsecurity(request):
    #status = mod.nginx()
    return render(request, 'modsecurity.html', {
        'nginx_status': str(mod.nginx()),
    })

def index(request):
    return render(request, 'index.html',{})
def mod_l(request):
    return render(request, 'mod_l.html',{
        'nginx_status': str(mod.nginx()),
        'mod_status': str(mod.nginx_modsecurity())
    })
def mod_m(request):
    ctx ={}
    if request.POST:
        rlt = mod.mod_custom_rule(request.POST['q'])
        ctx['rlt'] = "ADD" + request.POST['q'] + " " + rlt
    return render(request, "mod_m.html", ctx)

def mod_m_re(request):
    mod.restart_nginx()
    return render(request, 'mod_m_re.html',{})
def receive(p,q):
    output = sub.check_output('sudo ip netns exec ns12 tcpdump -i p02 -c 1 icmp', shell=True)
    q.put(output)
def send(p,q):
    output = sub.check_output('sudo ip netns exec ns11 ping -c 1 192.168.1.101', shell=True)
    q.put(output)
def route(request):
    ctx = {}
    if 't' in request.GET and request.GET['t'] == 'c':
        ctx['route'] = r.create() 
    if 't' in request.GET and request.GET['t'] == 'd':
        ctx['route'] = r.delete()
    if 't' in request.GET and request.GET['t'] == 's':
       que = queue.Queue()
       t1 = Thread(target=receive, args=(1,que))
       t1.start()
       
       t2 = Thread(target=send, args=(1,que))
       t2.start()
       
       t2.join()
       t1.join()
       ctx['send_o'] = que.get()
       ctx['rec_o'] = que.get()

       output = sub.check_output('sudo ovs-appctl ofproto/trace br01 in_port=100,dl_dst=22:03:81:9d:7f:a0 -generate', shell=True)
       ctx['ovs1_output'] = output
       output = sub.check_output('sudo ovs-appctl ofproto/trace br02 in_port=1,dl_dst=22:03:81:9d:7f:a0 -generate', shell=True)
       ctx['ovs2_output'] = output
       
    if set(ovs1.objects.all()) == set([]):
        ctx['ovs1'] = 'noContent'
        ctx['ovs2'] = 'noContent'
        ctx['ns1'] = 'noContent'
        ctx['ns2'] = 'noContent'
    else:
        ovs1_content = ovs1.objects.all()[0]
        ovs2_content = ovs2.objects.all()[0]
        ns1_content = ns1.objects.all()[0]
        ns2_content = ns2.objects.all()[0]
        ctx['ovs1'] = str('openvSwitchName:') + ovs1_content.name + '<br>' + str('openvSwitchInterfaceName:') + ovs1_content.port + '<br>' + str('openvSwitchOpenflowNumber:') + ovs1_content.number             
        ctx['ovs2'] = str('openvSwitchName:') + ovs2_content.name + '<br>' + str('openvSwitchInterfaceName:') + ovs2_content.port + '<br>' + str('openvSwitchOpenflowNumber:') + ovs2_content.number              
        ctx['ns1'] = str('nameSpaceName:') + ns1_content.name + '<br>' + str('nameSpaceInterfaceName:') + ovs1_content.port + '<br>' + str('nameSpaceAddress:') + ns1_content.address             
        ctx['ns2'] = str('nameSpaceName:') + ns2_content.name + '<br>' + str('nameSpaceInterfaceName:') + ovs2_content.port + '<br>' + str('nameSpaceAddress:') + ns2_content.address            
    return render(request, 'route.html',ctx)
def route_config(request):
    if request.POST:
        ovs = ovs1.objects.all()
        ovs.delete()
        ovs1.objects.create(name=request.POST['ovs-name1'], port=request.POST['ovs-port-name1'], number=request.POST['openflow-port-number1'])
        ovs = ovs2.objects.all()
        ovs.delete()
        ovs2.objects.create(name=request.POST['ovs-name2'], port=request.POST['ovs-port-name2'], number=request.POST['openflow-port-number2'])
        ns = ns1.objects.all()
        ns.delete()
        ns1.objects.create(name=request.POST['ns-name1'], address=request.POST['ns-port-address1'])
        ns = ns2.objects.all()
        ns.delete()
        ns2.objects.create(name=request.POST['ns-name2'], address=request.POST['ns-port-address2'])
    return render(request, 'route_config.html',{})
def temp(request):
    
    p = sub.Popen(['ping', '-c 4 8.8.8.8'], stdout = sub.PIPE, stderr = sub.PIPE)
    output, errors = p.communicate()
    return render(request, 'temp.html',{'aaa': output, 'bbb': errors})
