#!/usr/bin/env python
import re
from ipaddress import IPv4Network,IPv4Interface,IPv4Address


def alias_old_acl(acl_name):
    '''Функция меняет старое название ACL на новое'''
    aliases={'112':'transit','101':'manage-access'}
    if aliases.get(acl_name):
        out=aliases.get(acl_name)
    else:
        out=acl_name
    return out

def vlan_range_join(inlist):
    mlist=[int(item) for item in inlist]
    find_range=0
    range_dict={}
    range_dict[0]=[]
    mlist.sort()
    sortlist=mlist[:]
    vlan_range=[]
    if len(mlist)<=2:
        range_dict[0]=mlist[:]
    else:
        for i,vlan in enumerate(sortlist[0:len(sortlist)-1],0):
            range_dict[find_range].append(vlan)
            if vlan==sortlist[i+1]-1:
                range_dict[find_range].append(sortlist[i+1])
            else:
                find_range+=1
                range_dict[find_range]=[]
                range_dict[find_range].append(sortlist[i+1])
    for k,iv in range_dict.items():
        v=set(iv)
        if len(v)>=3:
            vlan_range.append('{}-{}'.format(min(v),max(v)))
        else:
            vlan_range.append(';'.join([str(item) for item in v]))
    return vlan_range



def get_foundry_vlan_ip(infile):
    '''Функция принимает на вход список файл с конфигом foundry формирует список, в котором 1й элемент это словарь интерфейсов и вланов, 2й элемент
    это словарь ospf. На выходе формируется конфиг для SNR S300.
    Формат словаря интерфейсов и вланов {45:{'name': 'link-Kalach-on-Don', 'ethe': '1/3', 've': '193', 'acl': '112', 'ipaddr': '10.27.128.105', 'mask': '255.255.255.252', 'ospfarea': '0.0.0.0'},....}
    Формат словаря ospf {'0.0.0.0': {'ospf_ranges': []}, '10.149.128.0': {'ospf_ranges': [['10.149.128.0', '255.255.128.0']]}}
    '''

    regex = ('^vlan (?P<vlan>\d+) name (?P<name>.+) by port'
         '| tagged ethe (?P<ethe>\S+)'
         '| router-interface ve (?P<ve>\S+)'
         '|interface ve (?P<intve>\S+)'
         '| ip access-group (?P<acl>\S+) in'
         '| ip address (?P<ipaddr>\S+) (?P<mask>\S+)'
         '| ip ospf area (?P<ospfarea>\S+)'
         '| ip ospf p(?P<ospfpassive>\S+)'
         '| area (?P<ospf_a>\S+)\n'
         '| area (?P<ospf>\S+) range (?P<ospf_sumnet>\S+) (?P<ospf_summask>\S+) advertise' )
     
    mdict={}
    intve=0
    ospf_dict={}
    with open(infile,'r') as f:
        for line in f:
            m = re.search(regex,line)
            if m:
                if m.lastgroup == 'name':
                    vlan,name = m.group('vlan','name') 
                    mdict[vlan]={}
                    mdict[vlan]['name']=name
                elif mdict and m.lastgroup in ['ethe','ve']:
                    mdict[vlan][m.lastgroup] = m.group(m.lastgroup)
                elif m.lastgroup == 'intve':
                    intve=m.group(m.lastgroup)
                elif intve!=0 and m.lastgroup in ['mask','acl','ospfarea','ospfpassive']:
                    for key,value in mdict.items():
                        if value.get('ve') and value['ve']==intve:
                            #mdict[key][m.lastgroup] = m.group(m.lastgroup)
                            if m.lastgroup == 'mask':
                                ipaddr,mask = m.group('ipaddr','mask')
                                mdict[key]['ipaddr'] = ipaddr
                                mdict[key]['mask'] = mask
                            elif m.group('acl'):
                                if m.group('acl') == 'incoming-users':
                                    mdict[key]['type'] = 'user'
                                else:
                                    mdict[key]['type'] = 'nonuser'
                                mdict[key]['acl'] = alias_old_acl(m.group('acl'))
                            elif m.group('ospfarea'):
                                mdict[key]['ospfarea'] = m.group('ospfarea')
                            elif m.group('ospfpassive'):
                                mdict[key]['ospfpassive'] = True
                if m.lastgroup == 'ospf_a':
                    ospf_dict[m.group(m.lastgroup)]={}
                    ospf_dict[m.group(m.lastgroup)]['ospf_ranges']=[]
                elif ospf_dict and m.lastgroup == 'ospf_summask':
                    ospf,ospf_sumnet,ospf_summask = m.group('ospf','ospf_sumnet','ospf_summask')
                    ospf_dict[ospf]['ospf_ranges'].append([ospf_sumnet,ospf_summask])
    return [mdict,ospf_dict]

def create_s300_vlan(inlist):
    '''Функция принимает на вход список в котором 1й элемент это словарь интерфейсов и вланов, 2й элемент
    это словарь ospf. На выходе формируется конфиг для SNR S300.
    Формат словаря интерфейсов и вланов {45:{'name': 'link-Kalach-on-Don', 'ethe': '1/3', 've': '193', 'acl': '112', 'ipaddr': '10.27.128.105', 'mask': '255.255.255.252', 'ospfarea': '0.0.0.0'},....}
    Формат словаря ospf {'0.0.0.0': {'ospf_ranges': []}, '10.149.128.0': {'ospf_ranges': [['10.149.128.0', '255.255.128.0']]}}
    '''
    mdict=inlist[0]
    odict=inlist[1]
    vlans='!\n'
    interface_vlan='!\n'
    vacl='!\n'
    router_ospf="!\nrouter ospf 1\n"
    ospf_passive=''
    vacl_dict={}
    port_dict={}
    ind=0
    port_list='!<psevdo-config>\n'
    for k,v in odict.items():
        if v.get('ospf_ranges'):
            for mrange in v.get('ospf_ranges'):
                range_format=IPv4Network('{}/{}'.format(*mrange)).with_prefixlen
                router_ospf+='area {} range {}\n'.format(k,range_format)
    for key,val in mdict.items():
        vlans+="vlan {}\n name {}\n!\n".format(key,val['name'])
        if val.get('ipaddr'):
            interface_vlan+="interface vlan{}\n ip address {} {}\n!\n".format(key,val.get('ipaddr'),val.get('mask'))
            mnet,wildmask=IPv4Interface('{}/{}'.format(val.get('ipaddr'),val.get('mask'))).network.with_hostmask.split('/')
        if val.get('acl'):
            acl_name=val.get('acl')
            if vacl_dict.get(acl_name)!=None:
                vacl_dict[acl_name].append(key)
            else:
                #print(vacl_dict.get(acl_name))
                vacl_dict[acl_name]=[]
                vacl_dict[acl_name].append(key)            
        if val.get('ospfarea'):
            router_ospf+='network {} {} area {}\n'.format(mnet,wildmask,val.get('ospfarea'))
        if val.get('ospfpassive'):
            ospf_passive+='passive-interface Vlan{}\n'.format(key)
        if val.get('ethe'):
            port=val.get('ethe')
            if port_dict.get(port)!=None:
                port_dict[port].append(key)
            else:
                port_dict[port]=[]
                port_dict[port].append(key)
    for i,j in vacl_dict.items():
        print(j)
        vacl+='vacl ip access-group {} in vlan {}\n'.format(i,";".join(vlan_range_join(j)))
    for i,j in port_dict.items():
        sw_port_gen=["! switchport trunk allowed vlan add {}".format(item) for item in j]
        port_list+='!interface {}\n{}\n'.format(ind,"\n".join(sw_port_gen))
        ind+=1
    print(port_dict)
    return vlans+interface_vlan+vacl+router_ospf+ospf_passive+port_list




print(create_s300_vlan(get_foundry_vlan_ip('config-fi')))
print(get_foundry_vlan_ip('config-fi')[0]['50'])
