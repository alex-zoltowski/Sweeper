import multiprocessing
import subprocess
import os
from socket import socket
from argparse import ArgumentParser
import sys

parser = ArgumentParser("ping.py -h\n       ping.py -s 141.209.100\n       ping.py -n 141.209\n       ping.py --localsubnet\n       ping.py --localnetwork\n\n")
#parser = ArgumentParser()
parser.add_argument("-s", dest="snet", help="Performs a ping sweep on a subnet")
parser.add_argument("-n", dest="net", help="Performs a ping sweep on network")
parser.add_argument("--localsubnet", action="store_true", help="Performs a ping sweep on local subnet")
parser.add_argument("--localnetwork", action="store_true", help="Performs a ping sweep on local network")

arguments = parser.parse_args()

ips = []

def get_local_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def pinger(job_q, results_q):
    DEVNULL = open(os.devnull,'w')
    while True:
        ip = job_q.get()
        if ip is None: break

        try:
            subprocess.check_call(['ping','-c1',ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass

def subnet_sweep(subnet):
    pool_size = 255

    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [ multiprocessing.Process(target=pinger, args=(jobs,results))
                 for i in range(pool_size) ]

    for p in pool:
        p.start()

    for i in range(1,255):
        jobs.put(str(subnet) + '.{0}'.format(i))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    while not results.empty():
        ip = results.get()
        ips.append(str(ip))

    ips.sort()

def network_sweep(network):
    for x in range(1, 255):
        subnet_sweep(network + "." + str(x))
        print network + "." + str(x) + ".0/24 sweeped"
    ips.sort()

def get_hostname(ip):
    try:
        return gethostbyaddr(ip)
    except socket.herror:
        return None, None, None


subnet = raw_input("Type in a subnet (ex: 141.209.1): ")

subnet_sweep(subnet)

ips_and_hostnames = {}

for ip in ips:
    name, alias, addresslist = get_hostname(ip)
    if name == None:
        ips_and_hostnames[ip] = "hostname not found"
    else:
        ips_and_hostnames[ip] = name

print "address         hostname"
print "------------------------"

for k, v in ips_and_hostnames.iteritems():
    print k + " - " + v
