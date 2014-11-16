"""Sputnik Connection Implementation

This module provides the Sputnik Connection implementation. This is a base
class that defines several helper functions for common tasks related to
transport-level interactions, such as message encoding and message passing.
"""

import asyncio


class Connection(asyncio.Protocol):
    """A generic instance of a network connection.

    A Connection is a base class that represents an instance of a network
    connection. The Connection implements commonly used actions that may be
    performed on messages.
    """

    def normalize(self, line, ending="\r\n"):
        """Ensures that a line is terminated with the correct line endings.

        The IRC protocol specifies that line endings should use CRLF line
        endings. This ensures that lines conform to this standard. In the event
        of a server that does not conform to the specification, we preserve
        the ability to provide an alternative line ending character sequence.

        Args:
            line (str): A message to be sent to the IRC network.
            ending (str, optional): The line ending. Defaults to ``"\r\n"``.
        """

        if not line.endswith(ending):
            line += ending
        return line

    def send(self, *args):
        """Writes a message to the connected interface.

        Messages are typically of the form ``<command> <message>``. This
        encapsulates the IRC messaging protocol by concatenating messages and
        checking their line endings before encoding the message into raw bytes,
        as part of the asyncio transport mechanism.

        Args:
            args (list of str): A list of strings to concatenate.
        """

        message = self.normalize(" ".join(args))
        self.transport.write(message.encode())

    # this will eventually be refactored to include the Client-based
    # implementation of forward(), most likely accepting the transport as a
    # parameter and performing any logic in-line.

    def forward(self, *args):

        message = self.normalize(" ".join(args))
        for client in self.bouncer.clients:
            if client.broker == self:
                client.transport.write(message.encode())
                print("[B to C]\t%s" % message, end="")

# these could really be module level functions probably ...