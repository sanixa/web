from django.shortcuts import render
from django.views.decorators import csrf
import content.modsecurity.func as mod
from content.models import ovs1,ovs2,ns1,ns2
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
def route(request):
    ctx = {}
    if 't' in request.GET and request.GET['t'] == 'd':
        pass
    if 't' in request.GET and request.GET['t'] == 'c':
        pass
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
    return render(request, 'temp.html',{})
