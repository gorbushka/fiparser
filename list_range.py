#!/usr/bin/env python
'''alist=['25', '33', '19', '11', '54', '12', '48', '41', '43', '35', '28', '30', '22', '32', '44', '34', '16', '53', '47', '1493',
 '49', '52', '42', '1495', '20', '26', '45', '40', '23', '27', '13', '50', '46', '1494', '29', '15', '37', '38', '14', '24', '31', '39', '17', '36', '21', '56', '55', '171','156']
'''
'''
['30', '53', '54', '35', '49', '21', '24', '1493', '1494', '46', '47', '45', '43', '28', '33', '15', '56', '44', '29', '37', '11', '26', '41', '1495', '38', '17', '14', '20', '34', '23', '13', '48', '25', '39', '55', '42', '18', '36', '52', '16', '27', '40', '32', '50', '31', '22', '12', '19']
['586']
['7', '84']
['193', '975', '103', '101']
'''

alist=['586','456','234']
#alist=['1','2','3']


def vlan_range_join(inlist):
    mlist=[int(item) for item in inlist]
    find_range=0
    range_dict={}
    range_dict[0]=[]
    mlist.sort()
    sortlist=mlist[:]
    vlan_range=[]
    print('Всего',len(mlist))
    print(mlist)
    if len(mlist)<=2:
        range_dict[0]=mlist[:]
    for i,vlan in enumerate(sortlist[0:len(sortlist)-1],0):
        print(i,vlan)
        print('сейчас',vlan,'next',sortlist[i+1])
        range_dict[find_range].append(vlan)
        if vlan==sortlist[i+1]-1:
            print('next!')
            range_dict[find_range].append(vlan+1)
        else:
            print('stop!')
            find_range+=1
            range_dict[find_range]=[]
    print(range_dict)
    for k,v in range_dict.items():
        if len(v)>=3:
            vlan_range.append('{}-{}'.format(min(v),max(v)))
        else:
            vlan_range.append(';'.join([str(item) for item in v]))
    return vlan_range


print(';'.join(vlan_range_join(alist)))


