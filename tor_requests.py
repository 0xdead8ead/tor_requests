#!/usr/bin/env python
#
#   Author:     Chase Schultz
#   Date:       03/25/2018
#   Purpose:    Simple Tor Example Code - Sockets & Requests Lib
#
#   Req:    On OSX edit the following file (if using the tor browser bundle):
#
#           /Users/<user>/Library/Application Support/TorBrowser-Data/Tor/torrc
#
#           Add the following lines:
#
#           ControlPort 9051
#           HashedControlPassword <Output of 'tor --hash-password "passwd"'>
#
#           --
#
#           Tor binary can be install with 'brew install tor'.
#


import requests
import socks
from stem import Signal
from stem.control import Controller
from time import sleep


class Tor():

    def __init__(self):
        self.control_pw = ''
        self.control_port = '9051'
        self.tor_ip = '127.0.0.1'
        self.tor_port = '9150'
        self.tor_req = self.get_tor_session()
        self.tor_sock = self.get_socket()

    def get_tor_session(self):
        '''Returns a requests object routed through Tor'''
        session = requests.session()
        session.proxies = {
            'http':  'socks5://'+self.tor_ip+':'+self.tor_port,
            'https': 'socks5://'+self.tor_ip+':'+self.tor_port
        }
        return session

    def renew_connection(self):
        '''Establishes a new Tor circuit'''
        with Controller.from_port(port=int(self.control_port)) as controller:
            controller.authenticate(password=self.control_pw)
            controller.signal(Signal.NEWNYM)
        sleep(10)

    def get_socket(self):
        '''Returns a socket object routed through Tor'''
        socks.setdefaultproxy(
            socks.PROXY_TYPE_SOCKS5,
            self.tor_ip,
            int(self.tor_port),
            True
        )
        return socks.socksocket()


if __name__ == '__main__':
    print 'Tor Library for HTTP Requests'

    # Socket Example
    tor = Tor()
    tor.control_pw = '<INSERT_PASSWORD_HERE>'
    s = tor.get_socket()
    s.connect(('redteam.fsociety.ninja', 1337))
    s.sendall('Hello Via Tor\n')
    s.settimeout(1)
    s.close()
    print 'connection closed'

    # Get new Tor Circuit
    tor.renew_connection()

    s = tor.get_socket()
    s.connect(('redteam.fsociety.ninja', 1337))
    s.send('Second Connection, who dis?\n')
    s.close()

    # Get new Tor Circuit
    tor.renew_connection()

    # Tor Requests Example
    r = tor.tor_req
    r.get('http://redteam.fsociety.ninja:8000')
