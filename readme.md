##Генератор конфигурации для SNR-S300

Есть две тонкости 
1. генерится весь конфиг кроме соответствия порт-vlan. Этот конфиг генерится в виде справки с псевдо-интерфейсами по порядку
```
!interface 0
! switchport trunk allowed vlan add 975
! switchport trunk allowed vlan add 555
!interface 1
! switchport trunk allowed vlan add 41
! switchport trunk allowed vlan add 1493
!interface 2
! switchport trunk allowed vlan add 33
! switchport trunk allowed vlan add 44
!interface 3
```
2. Скорее тонкость S300 а не генератора. Когда пытаешься повесить на много интерфейсов vacl, то делать это нужно ожидая результата выполнения предыдущей команды. Например, генератор выдал конфиг
```
vacl ip access-group transit in vlan 101;103;193;975
vacl ip access-group manage-access in vlan 84;7
vacl ip access-group incoming-users in vlan 11-50;52-56;1493-1495
vacl ip access-group forcameras in vlan 586
```

