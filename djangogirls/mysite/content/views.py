from django.shortcuts import render,redirect
from django.views.decorators import csrf
import content.modsecurity.func as mod
import content.route.func as r
import content.command.func as c
from content.models import ovs1,ovs2,ns1,ns2
from content.models import command as com
import subprocess as sub
import os,time

# Create your views here.


def index(request):
    return render(request, 'index.html',{})

def route(request):
    ctx = {}
    if 't' in request.GET and request.GET['t'] == 'c':
        ctx['route'] = r.create() 
    if 't' in request.GET and request.GET['t'] == 'd':
        ctx['route'] = r.delete()


    if set(ovs1.objects.all()) == set([]):
        ctx['ovs1'] = 'noContent'
        ctx['ovs2'] = 'noContent'
        ctx['ns1'] = 'noContent'
        ctx['ns2'] = 'noContent'
        ctx['created'] = False
    else:
        ovs1_content = ovs1.objects.all()[0]
        ovs2_content = ovs2.objects.all()[0]
        ns1_content = ns1.objects.all()[0]
        ns2_content = ns2.objects.all()[0]

        if 't' in request.GET and request.GET['t'] == 's':
            result = r.content()
            ctx['send_o'] = result['send_o']
            ctx['rec_o'] = result['rec_o']
            ctx['ovs1_output'] = result['ovs1_output']
            ctx['ovs2_output'] = result['ovs2_output']
            ctx['ovs1_detail'] = result['ovs1_detail']
            ctx['ovs2_detail'] = result['ovs2_detail']
        ctx['created'] = r.created()
            
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

def command(request):
    result = ""
    if request.POST:
        if request.POST['c'].find(" ") == -1:
            result = "command error"
        elif c.init() == "no data":
            result = "not set environment variable"
        else:
            t = request.POST['c'].split(' ')
            if len(t) == 3:
                result = c.main(t[0] + " " + t[1], t[2])
            else:
                result = c.main(t[0], t[1])
    return render(request, 'command.html',{
                  'result': result,
                 })

def command_config(request):
    if request.POST:
        c = com.objects.all()
        c.delete()
        com.objects.create(address=request.POST['ip'], user=request.POST['user'], passwd=request.POST['passwd'], bridge=request.POST['bridge'], interface=request.POST['interface'])
    return render(request, 'command_config.html',{})

def sfc(request):
    if 't' in request.GET and request.GET['t'] == 's':
        pass
    return render(request, 'sfc.html',{})

def sfc_config(request):
    return redirect("http://127.0.0.1:8181/index.html")

