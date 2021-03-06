import unittest
import bcrypt

from sputnik import datastore


class TestDatastore(unittest.TestCase):
    def setUp(self):
        self.datastore = datastore.Datastore(hostname="localhost", port="6379")
        self.datastore.database.flushall()

    def test_channels(self):
        # set up with add_channel()
        self.datastore.add_channel("freenode", "test12345")
        self.datastore.add_channel("quakenet", "test54321", "somepassword")
        self.datastore.add_channel("quakenet", "test12345", "otherpassword")

        # test get_channels() and previous add_channel() calls
        channels = self.datastore.get_channels()
        self.assertEqual(len(channels), 3)
        self.assertIsNone(channels["freenode:test12345"])
        self.assertEqual(channels["quakenet:test54321"], "somepassword")
        self.assertEqual(channels["quakenet:test12345"], "otherpassword")

        # test get_channels() with specific network
        channels = self.datastore.get_channels("quakenet")
        self.assertEqual(len(channels), 2)

        # test remove_channel()
        self.datastore.remove_channel("quakenet", "test12345")
        channels = self.datastore.get_channels()
        self.assertEqual(len(channels), 2)
        self.assertNotIn("quakenet:test12345", channels)

    def test_networks(self):
        # set up with add_network()
        self.datastore.add_network("freenode", "irc.freenode.net", 6667,
                                   "freenick", "freeuser", "freereal",
                                   "somepassword", 1)
        self.datastore.add_network("quakenet", "irc.quakenet.net", 6668,
                                   "quakenick", "quakeuser", "quakereal")

        # test get_networks() and previous add_network() calls
        networks = self.datastore.get_networks()
        self.assertEqual(len(networks), 2)
        self.assertEqual(networks["freenode"]["username"], "freeuser")
        self.assertEqual(networks["quakenet"]["port"], 6668)
        self.assertEqual(networks["freenode"]["password"], "somepassword")
        self.assertIsNone(networks["quakenet"]["password"])

        # test remove_network()
        self.datastore.remove_network("freenode")
        networks = self.datastore.get_networks()
        self.assertEqual(len(networks), 1)
        self.assertNotIn("freenode", networks)

    def test_password(self):
        # check default password status
        self.assertIsNone(self.datastore.get_password())

        # test password storage
        self.datastore.set_password("testpassword")
        stored_password = self.datastore.get_password()
        self.assertEqual(bcrypt.hashpw("testpassword".encode(),
                                       stored_password.encode()).decode(),
                         stored_password)
        self.assertNotEqual(bcrypt.hashpw("wrongpassword".encode(),
                                          stored_password.encode()).decode(),
                            stored_password)

        # test password update
        self.datastore.set_password("newpassword")
        stored_password = self.datastore.get_password()
        self.assertNotEqual(bcrypt.hashpw("testpassword".encode(),
                                          stored_password.encode()).decode(),
                            stored_password)
        self.assertEqual(bcrypt.hashpw("newpassword".encode(),
                                       stored_password.encode()).decode(),
                         stored_password)

if __name__ == "__main__":
    unittest.main()
