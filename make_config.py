#!/usr/bin/env python
from fiparser.fiparser import *


def dict_from_string(infile):
    mdict={}
    with open(infile,'r') as f:
        for line in f:
            vlan,name,port,acl,mnet,descr,nettype=line.strip().split(";")
            mdict[vlan]={'name':name,'ethe':port,'acl':acl,'ipaddr':IPv4Network(mnet)[1],'mask':IPv4Network(mnet).netmask,'ospfarea':'0.0.0.0'}
    return [mdict,{'0.0.0.0': {'ospf_ranges': []}}]



print(create_s300_vlan(dict_from_string("list-mod")))
print(create_s300_vlan(get_foundry_vlan_ip("config-fi")))