from curses import wrapper, color_pair, init_pair, newwin, COLOR_RED, COLOR_WHITE, COLOR_GREEN, COLOR_BLACK
from time import sleep
import subprocess
import sys
import select
import re
import threading
import copy

hosts = {}
running = True


def main(stdscr):

    global running

    parse_hosts()

    stdscr.clear()
    init_pair(1, COLOR_RED, COLOR_BLACK)
    init_pair(2, COLOR_GREEN, COLOR_BLACK)
    init_pair(3, COLOR_WHITE, COLOR_BLACK)

    if len(hosts) == 0:
        print_usage(stdscr)
        stdscr.getkey()
        sys.exit(0)

    stdscr.nodelay(True)

    for host in hosts:
        t = threading.Thread(target=ping_host, args=(host, 1, 1,))
        t.start()

    while True:
        inpt = stdscr.getch()
        if inpt == ord('q'):
            break
        render(stdscr)
        stdscr.refresh()
        stdscr.clear()
        sleep(0.4)

    running = False

def print_usage(stdscr):
    stdscr.addstr(0, 0, "pingtop - by taher <smokiee{at}gmail.com>", color_pair(2))
    stdscr.addstr(1, 0, "Usage: " + sys.argv[0] + " host1, [host2], ...", color_pair(2))
    stdscr.addstr(2, 0, "Press any key to quit", color_pair(1))


def render(stdscr):
    global hosts
    line = 4

    stdscr.addstr(0, 0, "pingtop by taher <smokiee@gmail.com>", color_pair(3))
    stdscr.addstr(1, 0, "Press 'q' to quit", color_pair(3))
    stdscr.addstr(2, 0, "", color_pair(3))
    stdscr.addstr(3, 0, "Host", color_pair(3))
    stdscr.addstr(3, 20, "Status", color_pair(3))
    stdscr.addstr(3, 30, "Ping", color_pair(3))

    for host in hosts:
        if hosts[host]['status'] == "UP":
            clr = color_pair(2)
            ping = hosts[host]['ping'] + " ms "
        else:
            clr = color_pair(1)
            ping = "DOWN"

        stdscr.addstr(line, 0, hosts[host]['host'], clr)
        stdscr.addstr(line, 20, str(hosts[host]['status']), clr)
        stdscr.addstr(line, 30, str(ping), clr)
        line = line + 1


def parse_hosts():
    global hosts
    hosts = {}
    host_struct = {"status": "", "ping:": -1}
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        lines = sys.stdin.readline()
        if lines:
            for line in lines.split(" "):
                line = line.replace(' ', '')
                hosts[line] = copy.deepcopy(host_struct)
                hosts[line]['host'] = line
        else:
            break

    for host in sys.argv[1:]:
        hosts[host] = copy.deepcopy(host_struct)
        hosts[host]['host'] = host

def ping_host(host, timeout, count):
    global hosts, running
    while running:
        try:
            ping = subprocess.check_output(
                ["ping", "-t", str(timeout), "-c", str(count), host]
            )
            result = re.split("\n+", str(ping))
            reg = '.*(\d+\.\d+)\/(\d+\.\d+)\/(\d+\.\d+) ms'
            times_line = [line for line in result if re.match(reg, line)].pop()
            times_res = re.match(reg, times_line)
            hosts[host]['ping'] = times_res.group(2)
            hosts[host]['status'] = "UP"
        except subprocess.CalledProcessError as e:
            hosts[host]['status'] = "DOWN"
        sleep(timeout)


wrapper(main)
