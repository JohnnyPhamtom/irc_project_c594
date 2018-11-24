

class User:
    # NEWUSER defaults sending message to server.
    def __init__(self, name: str, pwd: str, target_name: str) -> object:
        self.name = name
        self.pwd = pwd
        self.target = target_name
        self.groupList = []

    # print out user info
    def inspect(self):
        print("Name: ", self.name)
        print("Pass: ", self.pwd)
        print("Target: ", self.target)
        print("Groups", self.groupList)

    def get_name(self):
        return self.name

    def get_pwd(self):
        return self.pwd

    # NICK change user name
    def update_name(self, name):
        self.name = name

    # PASS change password
    def update_pwd(self, pwd):
        self.pwd = pwd

    # select appropriate client to route messages
    def update_target(self, target_name):
        self.target = target_name

    # JOIN add group membership
    def join(self, group):
        if self.groupList.__contains__(group):
            pass
        else:
            self.groupList.append(group)

    # LEAVE remove group membership
    def leave(self, group):
        if self.groupList.__contains__(group):
            self.groupList.remove(group)
        else:
            pass

    # PART shows group membership
    def display_group(self):
        print(self.groupList)

    # check for group membership
    def member_of(self, group):
        if self.groupList.__contains__(group):
            return True
        else:
            return False

    def get(self):
        return self

"""
## test bed
userList = []
for i in range(0, 10):
    userList.append(User('user' + str(i),'temp',('host_addr', 8000)))
for i in range(0,10):
    print(userList[i].get_name())
print(len(userList))
d = User('DarkFlameMaster', 'excell', 'addr')
print(d.name)
d.update_name("cow")
print(d.name)
d.join("cash moines")
d.join("pocky")
d.join("cash moines")
d.member_of()
d.leave('pocky')
d.leave('pocky1')
d.inspect()
"""