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
    default_target = "server"

    # this needs to be worked out.. optional args are passed as tuples..
    def __init__(self, *stored_user_list):
        if stored_user_list:
            self.userList += stored_user_list
        else:
            pass

    # check for name conflict, otherwise create new user
    # and updating the activeUserList
    # returns the client_name
    def new_user(self, tokens: list):
        if len(tokens) < 3:
            print("not enough args")
            return self.default_name
        for i, v in enumerate(self.userList):
            if v[0] == tokens[1]:
                print("User name taken.. try again")
                return self.default_name
        try:
            name = tokens[1]
            pwd = tokens[2]
            target_name = self.default_target
            newUser = user_object.User(name, pwd, target_name)
            self.userList.append((name, newUser))
            self.userObjectList.append(newUser)
            self.activeUserList.append(name)
            print("NEWUSER success")
            return name
        except:
            print("Failed to add user")
            return self.default_name

    # check if user is already logged in, then check for a match
    # with the actual list of users "registered"
    # update the activeChannels with the user's group
    # returns the client_name
    def login(self, tokens: list):
        if len(tokens) < 3:
            print("not enough args")
            return self.default_name
        try:
            if tokens[1] in self.activeUserList:
                print("fail. user is currently connected")
                return self.default_name
            for i, v in enumerate(self.userList):
                if v[0] == tokens[1]:
                    check_object = self.userObjectList[i]
                    if check_object.get_pwd() == tokens[2]:
                        self.activeUserList.append(tokens[1])
                        for j in check_object.groupList:
                            if j not in self.activeChannel:
                                self.activeChannel.append(j)
                        print("success")
                        return tokens[1]
                    else:
                        print("wrong pw")
                        return self.default_name
            else:
                print("user not found")
                return self.default_name
        except:
            print("Login failed.. possibly not enough args")
            return self.default_name

    # remove the user from the active list.
    # the client_name must be the caller to prevent logging someone else out
    # returns the client_name
    def logout(self, client_name: str):
        try:
            if client_name in self.activeUserList:
                self.activeUserList.remove(client_name)
                print("successful logout")
                return client_name
        except:
            print("LOGOUT fail. cannot find user")
            return client_name

    # add groups to the client saved in user object.
    # add groups to the activeChannels list
    # returns the list of groups the client successfully joined
    def join(self, tokens: list, client_name: str):
        if len(tokens) < 2:
            print("not enough args")
            return []
        try:
            max = len(tokens)
            group_to_add = []
            added_group = []
            for n in range(0, max):
                if "#" in tokens[n]:
                    #print(tokens[n])
                    group_to_add.append(tokens[n])
                    print("JOIN groups to add: ", group_to_add)
            for i, v in enumerate(self.userList):
                print(v[0]," vs ", client_name)
                if v[0] == client_name:
                    print("matched: ", client_name)
                    check_object = self.userObjectList[i]
                    for j in range(0, len(group_to_add)):
                        if "#" in group_to_add[j]:
                            check_object.join(group_to_add[j])
                            print("successfully joined", group_to_add[j])
                            added_group.append(group_to_add[j])
                            if group_to_add[j] not in self.activeChannel:
                                self.activeChannel.append(group_to_add[j])
                            else:
                                print("JOIN: activeChannel, lets introduce ourselves")
            print("JOIN added group: ", added_group)
            print("JOIN activeChannel: ", self.activeChannel)
            return added_group
        except:
            print("JOIN error.")
            return []

    # remove the groups from the client's object
    # returns the list of groups the client successfully left
    def leave(self, tokens: list, client_name):
        left_group = []
        if len(tokens) < 2:
            print("not enough args")
            return []
        try:
            for i, v in enumerate(self.userList):
                if v[0] == client_name:
                    check_object = self.userObjectList[i]
                    for j in range (0, len(tokens)):
                        if "#" in tokens[j]:
                            check_object.leave(tokens[j])
                            left_group.append(tokens[j])
                            print("successfully left", tokens[j])
                            test_empty_group = ["NAME", tokens[j]]
                            if len(self.g_name(test_empty_group)) == 1:
                                self.activeChannel.remove(tokens[j])
                            else:
                                print("LEAVE: still other users in this channel")
            return left_group
        except:
            print("LEAVE error.")
            return []

    # check for a user name to match on
    # else display the caller's groups
    # returns the list of groups
    def part(self, tokens: list, client_name):
        try:
            if len(tokens) > 1:
                print("PART looking up: ", tokens[1])
                for i, v in enumerate(self.userList):
                    if v[0] == tokens[1]:
                        check_object = self.userObjectList[i]
                        return check_object.display_group()
            else:
                print("PART looking up: ", client_name)
                for i, v in enumerate(self.userList):
                    if v[0] == client_name:
                        check_object = self.userObjectList[i]
                        return check_object.display_group()
        except:
            print("PART error.")
            return []

    # list all members of an active group
    # or list all active users
    # returns a list of users
    def g_name(self, tokens: list):
        try:
            if len(tokens) > 1:
                temp_group = []
                result = []
                for i in range(0, len(tokens)):
                    if tokens[i] in self.activeChannel:
                        temp_group.append(tokens[i])
                        # print("temp_group contains: ", temp_group)
                for j in range(0, len(temp_group)):
                    result.append(temp_group[j])
                    for k,v in enumerate(self.userList):
                        if v[0] in self.activeUserList:
                            # print("found active user:", v[0])
                            check_object = self.userObjectList[k]
                            if temp_group[j] in check_object.groupList:
                                result.append(check_object.get_name())
                print("G_NAME:", result)
                return result
            else:
                print("G_NAME:", self.activeUserList)
                return self.activeUserList
        except:
            print("G_NAME: failed")
            return []

    # list all active groups
    # returns a list of activeChannels
    def list(self):
        try:
            print(self.activeChannel)
            return self.activeChannel
        except:
            print("Failed to get list of active channels")
            return []

    # update the target_list based on message calls
    # returns the message tokens (actual data we want to send to another user)
    # and a list of recipients
    def change_recipient(self, tokens: list, client_name: str):
        if len(tokens) < 3:
            print("not enough args to send a message")
            message = "not enough args to send a message"
            return message.split(), []
        try:
            target_list = []
            message_tokens = []
            if tokens[0] == '/w':
                print("whisper @ ", tokens[1], self.activeUserList)
                if tokens[1] in self.activeUserList:
                    target_list.append(tokens[1])
                    message_tokens.append('(WHISPER):')
                    message_tokens += tokens
                    message_tokens.remove('/w')
                    message_tokens.remove(tokens[1])
                    print("CHANGE_RECIPIENT: WHAT WE ARE SENDING", message_tokens)
                    return message_tokens, target_list
                print("CHANGE_RECIPIENT: target not found")
                string = tokens[1] + " not found"
                return string.split(), []
            # elif tokens[0] == '/r':
            #   print("reply")
            elif tokens[0] == '/g':
                print("send to group")
                if len(self.activeChannel) < 1:
                    print("CHANGE_RECIPIENT: no active groups")
                    message = "no group found"
                    return message.split(), []
                # print("CHANGE_RECIPIENT activeChannel: ", self.activeChannel)
                if tokens[1] in self.activeChannel:
                    # print("CHANGE_RECIPIENT activeChannel: ", self.activeChannel)
                    target_list += self.g_name(tokens)
                    # print("CHANGE_RECIPIENT: group members", target_list)
                    if client_name not in target_list:
                        message = "Cannot send. Not part of group: " + tokens[1]
                        print("CHANGE_RECIPIENT:", message)
                        return message.split(), []
                    else:
                        target_list.remove(client_name)
                        print("CHANGE_RECIPIENT: group members", target_list)
                        if len(target_list) < 1:
                            message = "no one in group."
                            return message.split(), []
                        else:
                            sender_id_msg: str = '(' + tokens[1] + '): '
                            message_tokens.append(sender_id_msg)
                            message_tokens += tokens
                            message_tokens.remove('/g')
                            message_tokens.remove(tokens[1])
                            return message_tokens, target_list
        except:
            print("CHANGE_RECIPIENT: ERROR")
            return [], []

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
    # otherwise we allow other commands.
    # returns a triple: client_name, message tokens, target_receiver(s)
    def parse_string(self, tokens: list, client_name: str):
        target_list = []
        result = []
        message_tokens = []
        if client_name == self.default_name:
            c_name = client_name
            if tokens[0] == 'NEWUSER':
                c_name = self.new_user(tokens)
            elif tokens[0] == 'LOGIN':
                c_name = self.login(tokens)
            if c_name == self.default_name:
                message_tokens.append(tokens[0])
                message_tokens.append('Failed')
                return c_name, message_tokens, target_list
            else:
                message_tokens.append(tokens[0])
                message_tokens.append('Success')
                return c_name, message_tokens, target_list
        else:
            if tokens[0] == 'NEWUSER':
                return client_name, "Already LOGGED IN. Cannot do NEWUSER".split(), target_list
            elif tokens[0] == 'LOGIN':
                return client_name, "Already LOGGED IN. Cannot do LOGIN".split(), target_list
            elif tokens[0] == 'PASS':
                # <PASS> <OLDPW> <NEWPW>
                print("change password")
                pass
            elif tokens[0] == 'NICK':
                # <NICK> <PASSWORD> <NEWNICK>
                print("change user name")
                pass
            elif tokens[0] == 'LOGOUT':
                result.append(self.logout(client_name))
            elif tokens[0] == 'JOIN':
                result = self.join(tokens, client_name)
            elif tokens[0] == 'LEAVE':
                result = self.leave(tokens, client_name)
            elif tokens[0] == 'PART':
                result = self.part(tokens, client_name)
            elif tokens[0] == 'NAME':
                result = self.g_name(tokens)
            elif tokens[0] == 'LIST':
                result = self.list()
            elif tokens[0] == '/w':
                print("whisper")
                result, target_list = self.change_recipient(tokens, client_name)
                return client_name, result, target_list
            elif tokens[0] == '/r':
                print("reply")
            elif tokens[0] == '/g':
                print("send to group")
                result, target_list = self.change_recipient(tokens, client_name)
                return client_name, result, target_list
            else:
                print("default send")
                message_tokens = tokens
                target_list = '@-DEFAULT_SEND'.split()
                return client_name, message_tokens, target_list
            message_tokens.append(tokens[0])
            message_tokens += result
            return client_name, message_tokens, target_list

    # take in a string from client, breaks it into tokens
    # returns a triple: client_name, message tokens, target_receiver(s)
    def read_data(self, in_string, client_name):
        tok_string = in_string.split()
        print("READ_DATA(IN): ", tok_string, len(tok_string))
        print(client_name)
        if len(tok_string) > 0:
            c_name, message_tokens, target_list = ParseInput.parse_string(self, tok_string, client_name)
            print("READ_DATA(OUT): ", c_name, message_tokens, target_list)
            return c_name, message_tokens, target_list
        else:
            return client_name, tok_string, []
        # ECHO test
        # string = ' '
        # return string.join(tok_string)
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
