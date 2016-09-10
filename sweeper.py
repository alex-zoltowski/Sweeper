import multiprocessing
import subprocess
import os
import socket
from argparse import ArgumentParser
import sys

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
    ips = []
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

    return ips

def network_sweep(network):
    ips = []
    for x in range(1, 255):
        sn_ips = subnet_sweep(network + "." + str(x))
        for ip in sn_ips:
            ips.append(ip)
        print network + "." + str(x) + " sweeped"

    return ips

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)
    except socket.herror:
        return None, None, None

def print_ips(ips):
    ips.sort()

    for ip in ips:
        name, alias, addresslist = get_hostname(ip)
        if name is None:
            print ip + "   -   " + "hostname not found"
        else:
            print ip + "   -   " + name



def main():
    parser = ArgumentParser()
    parser.add_argument("-s", dest="snet", help="Performs a ping sweep on a subnet")
    parser.add_argument("-n", dest="net", help="Performs a ping sweep on network")
    parser.add_argument("--localsubnet", dest="ls", action="store_true", help="Performs a ping sweep on local subnet")
    parser.add_argument("--localnetwork", dest="ln", action="store_true", help="Performs a ping sweep on local network")
    arguments = parser.parse_args()

    if len(sys.argv) == 1:
        parser.error("No arguments given.  Please choose a ping sweep.")

    if arguments.snet is not None:
        print_ips(subnet_sweep(arguments.snet))
    elif arguments.net is not None:
        print_ips(network_sweep(arguments.net))
    elif arguments.ls is True:
        split_ip = get_local_ip().split(".")
        print_ips(subnet_sweep(split_ip[0] + "." + split_ip[1] + "." + split_ip[2]))
    elif arguments.ln is True:
        split_ip = get_local_ip().split(".")
        print_ips(network_sweep(split_ip[0] + "." + split_ip[1]))

if __name__ == "__main__":
    main()
