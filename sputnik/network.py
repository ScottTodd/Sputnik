"""Sputnik Network Implementation

This module provides the Sputnik Network implementation. This is a subclass of
a Connection, and defines an interface to IRC server networks implementing
_RFC 2813: https://tools.ietf.org/html/rfc2813 .
"""

from collections import deque
from connection import Connection


class Network(Connection):
    """An instance of a connection to an IRC network.

    A Network is the product of an asyncio protocol factory, and represents an
    instance of a connection from an IRC client to an IRC server. This could
    be either a single IRC server, or more likely, a network of servers behind
    a load balancer. It does not implement an actual IRC server, as defined in

    Attributes:
        ??? (revisit this later)
    """

    def __init__(self, bouncer, network, nickname, username, realname,
                 hostname, port, password=None, usermode=0):
        """Creates an instance of a Network.

        This performs a minimum level of string formatting and type coercion in
        order to conform to the IRC specifications during the connection stage.

        Args:
            bouncer (sputnik.Bouncer): The singleton Bouncer instance.
            network (str): The name of the IRC network to connect to.
            nickname (str): The IRC nickname to use when connecting.
            username (str): The IRC ident to use when connecting.
            realname (str): The real name of the user.
            hostname (str): The hostname of the IRC network to connect to.
            port (int): The port to connect using.
            password (str, optional): Bouncer password. Defaults to ``None``.
            usermode (int, optional): The IRC usermode. Defaults to ``0``.
        """

        self.usermode = str(usermode)
        self.username = username
        self.nickname = nickname
        self.password = password
        self.realname = ":%s" % realname
        self.bouncer = bouncer
        self.network = network
        self.hostname = hostname
        self.port = port

    def connection_made(self, transport):
        """Registers the connected Network with the Bouncer.

        Adds the Network to the set of connected Networks in the Bouncer and
        saves the transport for later use. This also creates a collection of
        buffers and logging facilities, and initiates the authentication
        handshake, if applicable.
        """

        print("Bouncer Connected to Network")
        if self.network in self.bouncer.networks:
            self.bouncer.networks[self.network].transport.close()
        self.bouncer.networks[self.network] = self

        self.transport = transport
        self.linebuffer = ""
        self.server_log = []
        self.chat_history = deque()

        self.send("PASS", self.password or "")
        self.send("NICK", self.nickname)
        self.send("USER", self.username, self.usermode, "*", self.realname)

    def connection_lost(self, exc):
        """Unregisters the connected Network from the Bouncer.

        Removes the Network from the dictionary of connected Clients in the
        Bouncer before the connection is terminated. After this point, there
        should be no remaining references to this instance of the Network.
        """

        print("Bouncer Disconnected from Network")
        self.bouncer.networks.pop(self.network)

    def data_received(self, data):
        """Handles incoming messages from connected IRC networks.

        Messages coming from IRC networks are potentially batched and need to
        be parsed into individual lines before any other operation may occur.
        On certain occasions, incoming data may overflow the transport buffer,
        requiring additional logic to reconstitute the messages into a single
        stream. Afterwards, we split lines according to the IRC message format
        and perform actions as appropriate.
        """

        data = data.decode()
        if not data.endswith("\r\n"):
            self.linebuffer += data
            return

        for line in (self.linebuffer + data).rstrip().split("\r\n"):

            print("[N to B]\t%s" % line)

            l = line.split(" ", 2)
            if   l[0] == "PING": self.send("PONG", l[1])
            elif l[1] == "PONG": self.forward("PONG", l[2])

            # breaks because it can't check for integers because 353 and 366
            # are related to channel joining and responses etc.

            elif l[1] == "NOTICE": self.server_log.append(line)
            elif l[1] == "MODE": self.server_log.append(line)
            elif l[1].isdigit(): self.server_log.append(line)
            else: self.chat_history.append(line)

        self.linebuffer = ""

        if self.bouncer.clients:
            while self.chat_history:
                line = self.chat_history.popleft()
                self.forward(line)

        # only reset the linebuffer if the server_log is successfully
        # replayed to a client
        # need to periodically PING the client to check if it's still active
        # need to intercept QUIT message
        # quit -> AWAY?
        # load plugins
        # need to validate the auth flow to handle if a user connects with
        # invalid credentials
