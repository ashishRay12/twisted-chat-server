from twisted.internet import reactor, protocol
from collections import deque
from twisted.internet.defer import Deferred


class handleChat(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.users = factory.users
        self.status = 'register'
        self.name = ''
        self.chatingFrom = ''
        self.chatList = []
        self.reqList = deque([])

    def connectionMade(self):
        self.transport.write("what is your name ->")

    def dataReceived(self, data):
        data = ''.join(data.split('\r\n'))
        if data == 'y()':
            print 'y()'
            self.addToChatList()
        if data == 'no()':
            self.reqList[0].premitDenied()
            self.reqList.popleft()
        print '%s -> %s' % (self.name, data)
        if self.status == 'register':
            self.addUser(data)
            self.activeList()
        elif self.chatingFrom == '':
            if data in self.factory.users:
                protocol = self.factory.users[data]
                protocol.chatPermission(self, self.name)
            else:
                self.transport.write('user is not active try another user from list below')
                self.activeList()
        else:
            self.startChat(data)

    def addUser(self, name):
        if name in self.users:
            self.transport.write('please select another name ->')
        else:
            self.factory.users[name] = self
            self.name = name
            self.status = 'ACTIVE'
            self.transport.write('\n welcome %s' % self.name)

    def activeList(self):
        self.transport.write('\n active users are ->%s' % str(self.users))
        self.transport.write('\n write any name from array for chat ->')

    def addToChatList(self):
        protocol = self.reqList[0]
        self.reqList.popleft()
        protocol.chatingFrom = self.name

    def chatPermission(self, client, name):
        self.reqList.append(client)
        self.transport.write('%s wants to talk to you < y()/no() >' % name)

    def premitDenied(self):
        self.transport.write('permission denied, try another user')
        self.activeList()

    def startChat(self, data):
        if data == 'exit()':
            self.chatingFrom = ''
        else:
            protocol = self.factory.users[self.chatingFrom]
            message = "<%s> %s" % (self.name, data)
            protocol.transport.write('\n %s \n' % message)


class chatFactory(protocol.Factory):

    users = {}
    chatSessions = {}

    def buildProtocol(self, addr):
        return handleChat(self)


reactor.listenTCP(27022, chatFactory())
reactor.run()
