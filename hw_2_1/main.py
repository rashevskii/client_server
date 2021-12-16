import platform
from ipaddress import ip_address
from subprocess import Popen, PIPE
from tabulate import tabulate

PARAMS = '-n' if platform.system().lower() == 'windows' else '-c'


def ping(address):
    args = ['ping', PARAMS, '1', address]
    answer = Popen(args, stdout=PIPE, stderr=PIPE)
    code = answer.wait()
    if code == 0:
        return address, 1
    else:
        return address, 0


def host_ping(lst_addr):
    dct = {
        'Reachable': [],
        'Unreachable': [],
    }
    for addr in lst_addr:
        res = ping(addr)
        if res[1] == 1:
            dct['Reachable'].append(res[0])
        elif res[1] == 0:
            dct['Unreachable'].append(res[0])
    return dct


def host_range_ping():
    start_ip_user = input('Введите стартовый ip: ')
    count_ip = int(input('Введите желаемое количество ip: '))
    start_ip = ip_address(start_ip_user)
    ip_adresses = []
    print('Пожалуйста, подождите результат...')
    for num in range(0, count_ip):
        next_ip = start_ip + num
        if (int(str(next_ip).split('.')[3]) == 255):
            ip_adresses.append(str(next_ip))
            print(f'Нельзя задать ip больше 255 в последнем октете. Пинговаться будут адреса до {str(next_ip)}')
            break
        else:
            ip_adresses.append(str(next_ip))
    return host_ping(ip_adresses)


adresses = ['yandex.ru', '192.168.1.1']
print(tabulate(host_ping(adresses), headers='keys', tablefmt='grid'))
print(tabulate(host_range_ping(), headers='keys', tablefmt='grid'))
