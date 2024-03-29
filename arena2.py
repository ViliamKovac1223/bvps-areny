#!/bin/python

import os
import subprocess
import sys
import getopt
import shutil
import random

COMPILER            = "gcc"
COMPILE_CODE        = True
SOURCE_CODE_FILE    = "zadanie2.c"
ARENA_FOLDER        = ".notArenaFr"
BIN_FILE            = "/zadanie2ArenaBin"
INFO_FILE           = ARENA_FOLDER + "/info.txt"
USERS_FILE          = ARENA_FOLDER + "/hesla.csv"
NUMBER_OF_KEYS      = 10

ERROR_OUT           = "chyba"
OK_OUT              = "ok"
NAME_MSG            = "meno: "
PASSWORD_MSG        = "heslo: "
KEY_MSG             = "overovaci kluc: "
FULL_OK_OUT         = NAME_MSG + PASSWORD_MSG + KEY_MSG + OK_OUT
FULL_ERROR_OUT      = NAME_MSG + PASSWORD_MSG + KEY_MSG + ERROR_OUT

USERS = [
    # username, password
    ("shortPass", "p"),
    ("longPass", "abcd" * ((256 // 4) - 1)),
    ("weirdZnaky!12)", "12jk';a123901;"),
    ("Elf", "BowAndSword"),
    ("Dwarf ", "ShieldAndSword"),
    ("Witch ", "MagicThings"),
]


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hir", [])
    except getopt.GetoptError:
        help()
        sys.exit(0)

    isInitEnv = False
    isTesting = False
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit(0)
        elif opt == '-i':
            isInitEnv = True
        elif opt == '-r':
            isTesting = True

    if isInitEnv and isTesting:
        help()
        sys.exit(0)

    if not isInitEnv and not isTesting:
        help()
        sys.exit(0)

    if isInitEnv:
        initEnv()
    elif isTesting:  # Start testing
        usersKeys = initEnv()
        # Compile code
        if compileCode() is False:
            sys.exit(0)

        # Basic test
        basicTest(usersKeys, (NUMBER_OF_KEYS // 2) - 1)
        usersKeys = initEnv()

        # First key test
        usersKeys = initEnv()
        basicTest(usersKeys, 0)

        # Last key test
        usersKeys = initEnv()
        basicTest(usersKeys, NUMBER_OF_KEYS - 1)

        # Remove all keys test
        usersKeys = initEnv()
        removeAllKeysTest(usersKeys)

        # Try wrong password but right key
        usersKeys = initEnv()
        wrongPasswordTest(usersKeys)

        # Try wrong key but good password
        usersKeys = initEnv()
        wrongKeyTest(usersKeys)


def wrongKeyTest(usersKeys):
    """
    Attempt to auth user with good password and wrong key
    """
    printBanner()
    print("This test uses good password but wrong key to login")
    print("Reasons for failed test:")
    print("Wrong output from your program")
    print(f"The {USERS_FILE} is empty")
    for user, _ in usersKeys.items():
        usedKey = "noKeyFound"
        password = getPassword(user)
        out = test(user, password, usedKey)
        if (out == FULL_ERROR_OUT and isFileEmpty(USERS_FILE) is False):
            printSuccess(f"test passed for username {user}")
        else:
            printError(f"test failed for username: {user}, password: {password}, key: {usedKey}")
            printError(f"Expected output: {FULL_ERROR_OUT}")
            printError(f"Your output: {out}")
            printError("Feel free to re-init env and run test manually")


def wrongPasswordTest(usersKeys):
    password = "hopeYouDindtSetThisAsPassword"
    """
    Attempt to auth user with wrong password and good key
    """
    printBanner()
    print("This test uses wrong password but good key to login")
    print("Reasons for failed test:")
    print("Wrong output from your program")
    print("The key that was used is not in the file anymore")
    print(f"The {USERS_FILE} is empty")
    for user, keys in usersKeys.items():
        usedKey = keys[len(keys) // 2]
        out = test(user, password, usedKey)
        if (findKeyInFile(user, usedKey) is True and out == FULL_ERROR_OUT and isFileEmpty(USERS_FILE) is False):
            printSuccess(f"test passed for username {user}")
        else:
            printError(f"test failed for username: {user}, password: {password}, key: {usedKey}")
            printError(f"Expected output: {FULL_ERROR_OUT}")
            printError(f"Your output: {out}")
            printError("Feel free to re-init env and run test manually")


def removeAllKeysTest(usersKeys):
    """
    Remove all keys for all users
    """
    printBanner()
    print("This test removes all keys for all users")
    print("Reasons for failed test:")
    print("Wrong output from your program")
    print("The key that was supposed to be removed is still there")
    print(f"The {USERS_FILE} is empty")
    for user, keys in usersKeys.items():
        isFail = False
        failedKey = ""
        failedNumberOfKey = 0
        for key in keys:
            password = getPassword(user)
            out = test(user, password, key)
            failedNumberOfKey += 1
            if (not (findKeyInFile(user, key) is False and out == FULL_OK_OUT and isFileEmpty(USERS_FILE) is False)):
                failedKey = key
                isFail = True
                break

        if (isFail is False):
            printSuccess(f"Test passed for username {user}")
        else:
            printError(f"Test failed for username: {user}, password: {password}, key={failedKey}, round number: {failedNumberOfKey}/{NUMBER_OF_KEYS}")
            printError(f"Expected output: {FULL_OK_OUT}")
            printError(f"Your output: {out}")
            printError("Feel free to re-init env and run test manually")


def basicTest(usersKeys, keyNumber):
    """
    Remove one key (key in the middle for all users)
    """
    printBanner()
    print(f"Basic test, Removes one key ({keyNumber + 1}/{NUMBER_OF_KEYS}) for all users")
    print("Reasons for failed test:")
    print("Wrong output from your program")
    print("The key that was supposed to be removed is still there")
    print(f"The {USERS_FILE} is empty")
    for user, keys in usersKeys.items():
        usedKey = keys[len(keys) // 2]
        password = getPassword(user)
        out = test(user, password, usedKey)
        if (findKeyInFile(user, usedKey) is False and out == FULL_OK_OUT and isFileEmpty(USERS_FILE) is False):
            printSuccess(f"test passed for username {user}")
        else:
            printError(f"test failed for username: {user}, password: {password}, key: {usedKey}")
            printError(f"Expected output: {FULL_OK_OUT}")
            printError(f"Your output: {out}")
            printError("Feel free to re-init env and run test manually")


def test(user, password, key):
    """
    Runs command with given flags and returns stdout
    """
    inputString = f"{user}\n{password}\n{key}\n"
    result = subprocess.run(f"./{BIN_FILE}",  input=inputString,
                            shell=True, cwd=f"./{ARENA_FOLDER}", text=True,
                            capture_output=True)
    # Check if the command was successful
    return result.stdout


def isFileEmpty(fileName) -> bool:
    return os.path.getsize(fileName) == 0


def findKeyInFile(userName, key) -> bool:
    isKeyInFile = False
    with open(USERS_FILE, 'r') as userFile:
        for line in userFile:
            data = line.split(':')
            data.extend(data.pop().split(','))

            if data[0] != userName:
                continue

            for i in range(2, len(data)):
                if (key == data[i]):
                    isKeyInFile = True
                    break
            break  # If right user was found but key wasn't just break loop and return False

    return isKeyInFile


def getPassword(user):
    for u in USERS:
        if u[0] == user:
            return u[1]
    return ""


def initEnv():
    if os.path.exists(ARENA_FOLDER):
        shutil.rmtree(ARENA_FOLDER)

    # Create folders for testing
    os.makedirs(ARENA_FOLDER, mode=0o755)

    if compileCode(False) is False:
        printError("Compilation error during initEnv")
        sys.exit(0)

    # Generate info file
    with open(INFO_FILE, 'w') as infoFile:
        for user in USERS:
            infoFile.write(f"{user[0]}:{user[1]}\n")

    usersKeys = {}
    # Generate passwords file
    with open(USERS_FILE, 'w') as userFile:
        for user in USERS:
            usersKeys[user[0]] = []
            # Generate keys
            keys = ""
            for i in range(NUMBER_OF_KEYS):
                if i != 0:
                    keys += ","
                key = generateKey()
                keys += key
                usersKeys[user[0]].append(key)
            hash = getHash(user[1])
            userFile.write(f"{user[0]}:{hash}:{keys}\n")

    return usersKeys


def generateKey():
    newKey = ""
    for i in range(6):
        randomDigit = random.randint(0, 9)
        newKey += str(randomDigit)
    return newKey


def getHash(key):
    result = subprocess.run(f"./{BIN_FILE} --hash \"{key}\"", shell=True, cwd=f"./{ARENA_FOLDER}", text=True, capture_output=True)
    result = result.stdout
    # Remove new line symbol from key if it's present at the end
    if result[-1] == '\n':
        resultTxt = result[:-1]
    return resultTxt


def compileCode(printStatus=True) -> bool:
    if COMPILE_CODE is False:
        return True
    removeFile(f"./{ARENA_FOLDER}/{BIN_FILE}")
    os.system(f"{COMPILER} {SOURCE_CODE_FILE}  -o {ARENA_FOLDER}/{BIN_FILE}")
    if not os.path.exists(f"./{ARENA_FOLDER}/{BIN_FILE}"):
        if printStatus is True:
            printError("Compilation error")
        return False
    else:
        if printStatus is True:
            printSuccess("Compilation successful")
        return True


def help():
    print("Usage:")
    print("arena.py -h # Prints help menu")
    print("arena.py -i # Inits testing environment")
    print("arena.py -r # Runs all tests")


def removeFile(file):
    if os.path.exists(file):
        os.remove(file)


def printError(text):
    RED = '\033[91m'    # ] Messes with my lsp if this comment ain't here
    END = '\033[0m'     # ] Messes with my lsp if this comment ain't here
    print(f"{RED}[ERROR] {text}{END}")


def printSuccess(text):
    RED = '\033[92m'    # ] Messes with my lsp if this line ain't here
    END = '\033[0m'     # ] Messes with my lsp if this line ain't here
    print(f"{RED}[OK] {text}{END}")


def printBanner():
    print("=" * 25)


if __name__ == "__main__":
    main(sys.argv[1:])
