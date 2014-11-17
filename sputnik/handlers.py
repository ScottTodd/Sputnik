import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, bouncer):
        self.bouncer = bouncer


class MainHandler(BaseHandler):
    @tornado.web.addslash
    def get(self):
        self.render("index.html", networks=self.bouncer.networks)

    def post(self):
        network_name = self.get_argument('networkname')
        network_address = self.get_argument('networkaddress')
        nickname = self.get_argument('nickname')
        ident = self.get_argument('ident')

        print('network_name: ' + network_name)
        print('network_address: ' + network_address)
        print('nickname: ' + nickname)
        print('ident: ' + ident)

        self.bouncer.add_network(network=network_name,
                                 hostname=network_address,
                                 port=6667,
                                 nickname=nickname,
                                 username=ident,
                                 realname=ident)

        # Race condition, should wait for the network to be added?
        # Or data bind and update the site when it is added?
        self.get()


class EditHandler(BaseHandler):
    @tornado.web.addslash
    def get(self, network_name):
        network = self.bouncer.networks[network_name]
        self.render("edit.html", network=network)


class AddHandler(BaseHandler):
    @tornado.web.addslash
    def get(self):
        self.render("add.html")
