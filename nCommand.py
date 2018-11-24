import user_object


class ParseInput:
    # userList is a pair containing the user_name and user_object
    # userObjectList contains actual user data. it is instantiated in the same order
    # as userList for ease. Contains all registered* users
    # activeUserList contains only users who are Logged in. It is a subset of the userList
    # activeChannel contains a list of channels created.
    # CURRENTLY DOES NOT UPDATE ITSELF IF THERE ARE NO USERS IN THE CHANNEL
    userList = []
    userObjectList = []
    activeUserList = []
    activeChannel = []
    default_name = "@-DEFAULT"

    # this needs to be worked out.. optional args are passed as tuples..
    def __init__(self, *stored_user_list):
        if stored_user_list:
            self.userList += stored_user_list
        else:
            pass

    # check for name conflict, otherwise create new user
    # and updating the activeUserList
    def new_user(self, tokens: list):
        if len(tokens) < 3:
            print("not enough args")
            return 0
        for i, v in enumerate(self.userList):
            if v[0] == tokens[1]:
                print("User name taken.. try again")
                return 0
        try:
            name = tokens[1]
            pwd = tokens[2]
            target_name = 'server'
            newUser = user_object.User(name, pwd, target_name)
            self.userList.append((name, newUser))
            self.userObjectList.append(newUser)
            self.activeUserList.append(name)
            print("NEWUSER success")
            return 1
        except LookupError:
            print("Failed to add user")
            return 0

    # check if user is already logged in, then check for a match
    # with the actual list of users "registered"
    # update the activeChannels with the user's group
    def login(self, tokens: list):
        if len(tokens) < 3:
            print("not enough args")
            return 0
        try:
            if tokens[1] in self.activeUserList:
                print("fail. user is currently connected")
                return 0
            for i, v in enumerate(self.userList):
                if v[0] == tokens[1]:
                    check_object = self.userObjectList[i]
                    if check_object.get_pwd() == tokens[2]:
                        self.activeUserList.append(tokens[1])
                        for j in check_object.groupList:
                            if j not in self.activeChannel:
                                self.activeChannel.append(j)
                        print("success")
                        return 1
                    else:
                        print("wrong pw")
                        return 0
            else:
                print("user not found")
                return 0
        except LookupError:
            print("Login failed.. possibly not enough args")
            return 0

    # remove the user from the active list.
    # the client_name must be the caller to prevent logging someone else out
    def logout(self, client_name: str):
        try:
            if client_name in self.activeUserList:
                self.activeUserList.remove(client_name)
                print("successful logout")
                return 1
        except LookupError:
            print("LOGOUT fail. cannot find user")

    # add groups to the client saved in user object.
    # add groups to the activeChannels list
    def join(self, tokens: list, client_name: str):
        if len(tokens) < 2:
            print("not enough args")
            return 0
        try:
            max = len(tokens)
            group_to_add = []
            for n in range(0, max):
                if "#" in tokens[n]:
                    #print(tokens[n])
                    group_to_add.append(tokens[n])
            for i, v in enumerate(self.userList):
                print(v[0]," vs ", client_name)
                if v[0] == client_name:
                    print("matched: ", client_name)
                    check_object = self.userObjectList[i]
                    for j in range(0, len(group_to_add)):
                        if "#" in group_to_add[j]:
                            check_object.join(group_to_add[j])
                            print("successfully joined", group_to_add[j])
                            if tokens[j] not in self.activeChannel:
                                self.activeChannel.append(group_to_add[j])
            return 1
        except LookupError:
            print("JOIN error.")

    # remove the groups from the client's object
    def leave(self, tokens: list, client_name):
        if len(tokens) < 2:
            print("not enough args")
            return 0
        try:
            for i, v in enumerate(self.userList):
                if v[0] == client_name:
                    check_object = self.userObjectList[i]
                    for j in range (0, len(tokens)):
                        if "#" in tokens[j]:
                            check_object.leave(tokens[j])
                            print("successfully left", tokens[j])
            return 1
        except LookupError:
            print("LEAVE error.")

    # check for a user name to match on
    # else display the caller's groups
    def part(self, tokens: list, client_name):
        try:
            if len(tokens) > 1:
                for i, v in enumerate(self.userList):
                    if v[0] == tokens[1]:
                        check_object = self.userObjectList[i]
                        check_object.display_group()
            else:
                for i, v in enumerate(self.userList):
                    if v[0] == client_name:
                        check_object = self.userObjectList[i]
                        check_object.display_group()
        except LookupError:
            print("PART error.")

    # list all members of an active group
    # or list all active users
    def g_name(self, tokens: list):
        try:
            if len(tokens) > 1:
                temp_group = []
                result = []
                for i in range(0, len(tokens)):
                    if tokens[i] in self.activeChannel:
                        temp_group.append(tokens[i])
                        print("temp_group contains: ", temp_group)
                for j in range(0, len(temp_group)):
                    result.append(temp_group[j])
                    for k,v in enumerate(self.userList):
                        if v[0] in self.activeUserList:
                            print("found active user:", v[0])
                            check_object = self.userObjectList[k]
                            if temp_group[j] in check_object.groupList:
                                result.append(check_object.get_name())
                print(result)
                return 1
            else:
                print(self.activeUserList)
            return 1
        except LookupError:
            print("G_NAME: failed")
            return 0

    # list all active groups
    def list(self):
        try:
            print(self.activeChannel)
            return 1
        except LookupError:
            print("Failed to get list of active channels")
            return 0

    # find the person receiving the private message and send the message
    def whisper(self, tokens):
        if len(tokens) < 2:
            print("WHISPER/REPLY not enough args")
            return 0
        try:
            print("parse the target and send rest of message")
        except LookupError:
            print("Failed to create message")

    # if the client_name is default_name, we only allow NEWUSER or LOGIN
    def parse_string(self, tokens: list, client_name: str):
        # if client_name == self.default_name:
            if tokens[0] == 'NEWUSER':
                self.new_user(tokens)
            elif tokens[0] == 'LOGIN':
                self.login(tokens)
        #else:
            if tokens[0] == 'PASS':
                # <PASS> <OLDPW> <NEWPW>
                print("change password")
                pass
            elif tokens[0] == 'NICK':
                # <NICK> <PASSWORD> <NEWNICK>
                print("change user name")
                pass
            elif tokens[0] == 'LOGOUT':
                self.logout(client_name)
            elif tokens[0] == 'JOIN':
                self.join(tokens, client_name)
            elif tokens[0] == 'LEAVE':
                self.leave(tokens, client_name)
            elif tokens[0] == 'PART':
                self.part(tokens, client_name)
            elif tokens[0] == 'NAME':
                self.g_name(tokens)
            elif tokens[0] == 'LIST':
                self.list()
            elif tokens[0] == '/w':
                print("whisper")
            elif tokens[0] == '/r':
                print("reply")
            else:
                print("default send")

    def read_data(self, in_string):
        tok_string = in_string.split()
        print(tok_string, len(tok_string))
        client_name = "myname"
        print(client_name)
        ParseInput.parse_string(self, tok_string, client_name)
        string = ' '
        return string.join(tok_string)
        # print(tok_string[0])




"""
# test bed
test = ParseInput()
#userList = []
test.read_data("NEWUSER myname mypwd")

print(test.userList)
for i, v in enumerate(test.userList):
    if v[0] == 'myname':
        print("true", i)
        print(test.userList[0], test.userObjectList)
tempObj = test.userObjectList[0]
tempObj.inspect()

   #test.userObjectList[0].get_name()
"""
