#!/bin/python

import sys
import os
import subprocess

COMPILER            = "gcc"
COMPILE_CODE        = True
SOURCE_CODE_FILE    = "zadanie3.c"
ARENA_FOLDER        = ".notArenaFr"
BIN_FILE            = "/zadanie3ArenaBin"

ERROR_OUT           = "chyba\n"
OK_OUT              = "ok\n"
NO_FILE_MSG         = "ziaden subor\n"
PRMOPT_MSG          = "# "
USER_NAME           = "Elf"

DEFAULT_PERMISSION  = 7
READ_PERMISSION     = 4
WRITE_PERMISSION    = 2
EXECUTE_PERMISSION  = 1


def main():
    # Compile code
    if compileCode() is False:
        sys.exit(0)

    print("Tests for basic things, like touch, mkdir, ls")
    basicTests()
    print("Tests for chmod functionality")
    chmodTests()
    print("Tests for chown functionality")
    chownTests()
    print("Tests for remove(rm) functionality")
    rmTests()
    print("Tests for permissions")
    permissionsTests()
    print("Tests basich cd behaviour")
    cdBasicTests()
    print("Tests for absolute/relative path")
    absoluteRelativeTests()


def basicTests():
    # Test empty ls test
    test(buildInput(["ls", "quit"]),
         buildOutput([PRMOPT_MSG, NO_FILE_MSG, PRMOPT_MSG]),
         "Test: empty ls", "")

    data = [
        # (command_to_create, reference_name),
        ("touch file", "file"),
        ("mkdir folder", "folder"),
    ]

    for testData in data:
        # Test ls with a simple file/folder
        test(buildInput([testData[0], f"ls {testData[1]}", "quit"]),
             buildOutput([PRMOPT_MSG, PRMOPT_MSG, f"{testData[1]} {getUser()} {getPerm(DEFAULT_PERMISSION)}\n", PRMOPT_MSG]),
             f"Test: basic ls with {testData[1]}", "")

    # Test ls with file and folder
    test(buildInput(["mkdir folder", "touch file", "ls", "quit"]),
         buildOutput([
             PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
             f"folder {getUser()} {getPerm(DEFAULT_PERMISSION)}\n",
             f"file {getUser()} {getPerm(DEFAULT_PERMISSION)}\n",
             PRMOPT_MSG]),
         "Test: file and folder ls", "")


def chmodTests():
    data = [
        # (command_to_create, reference_name),
        ("touch file", "file"),
        ("mkdir folder", "folder"),
    ]

    for testData in data:
        # Test chmod with file/folder
        for perm in range(READ_PERMISSION + WRITE_PERMISSION + EXECUTE_PERMISSION + 1):
            test(buildInput([testData[0], f"chmod {perm} {testData[1]}", "ls", "quit"]),
                 buildOutput([
                     PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
                     f"{testData[1]} {getUser()} {getPerm(perm)}\n",
                     PRMOPT_MSG]),
                 f"Test: {testData[1]} chmod with perm: {getPerm(perm)}", "")


def chownTests():
    data = [
        # (command_to_create, reference_name),
        ("touch file", "file"),
        ("mkdir folder", "folder"),
    ]

    for testData in data:
        # Test chown with file/folder
        test(buildInput([testData[0], f"chown {USER_NAME} {testData[1]}", "ls", "quit"]),
             buildOutput([
                 PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
                 f"{testData[1]} {USER_NAME} {getPerm(DEFAULT_PERMISSION)}\n",
                 PRMOPT_MSG]),
             f"Test: chown with {testData[1]}", "")


def rmTests():
    data = [
        # (command_to_create, reference_name),
        ("touch file", "file"),
        ("mkdir folder", "folder"),
    ]

    for testData in data:
        # Test read command with file/folder
        test(buildInput([testData[0], "ls", f"rm {testData[1]}", "ls", "quit"]),
             buildOutput([
                 PRMOPT_MSG, PRMOPT_MSG,
                 f"{testData[1]} {getUser()} {getPerm(DEFAULT_PERMISSION)}\n",
                 PRMOPT_MSG, PRMOPT_MSG,
                 NO_FILE_MSG,
                 PRMOPT_MSG]),
             f"Test: rm with {testData[1]}", "")

        # Try to remove dir without permission
        test(buildInput([testData[0],
                         # Change permissions
                         f"chmod 5 {testData[1]}",
                         # Try to remove file/folder without good permissions
                         f"rm {testData[1]}",
                         "ls", "quit"]),
             buildOutput([
                 PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
                 ERROR_OUT, PRMOPT_MSG,
                 f"{testData[1]} {getUser()} {getPerm(5)}\n",
                 PRMOPT_MSG]),
             f"Test: rm {testData[1]} without permission", "")


def cdBasicTests():
    test(buildInput(["mkdir folder",
                     # Go to folder and back
                     "cd folder",
                     "cd ..",
                     # Change folder permission (rw-)
                     "chmod 6 folder",
                     # Try to cd into folder (error expected)
                     "cd folder",
                     "quit"]),
         buildOutput([
             PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
             PRMOPT_MSG, PRMOPT_MSG,
             ERROR_OUT,
             PRMOPT_MSG]),
         "Test: basic cd", "")


def permissionsTests():
    cmdsData = [
        ("vypis", READ_PERMISSION),
        ("zapis", WRITE_PERMISSION),
        ("spusti", EXECUTE_PERMISSION),
    ]

    # Test all commands
    for cmdData in cmdsData:
        data = [
            # (command_to_create, reference_name),
            ("touch file", "file"),
            ("mkdir folder", "folder"),
        ]

        # Test command for file/folder
        for testData in data:
            test(buildInput([testData[0],
                             # Set right permission
                             f"chmod {cmdData[1]} {testData[1]}",
                             # Run command and expect positive result
                             f"{cmdData[0]} {testData[1]}",
                             # Delete given permission
                             f"chmod 0 {testData[1]}",
                             # Run command and expect negative result
                             f"{cmdData[0]} {testData[1]}",
                             "quit"]),
                 buildOutput([
                     PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
                     OK_OUT,
                     PRMOPT_MSG, PRMOPT_MSG,
                     ERROR_OUT,
                     PRMOPT_MSG]),
                 f"Test: {cmdData[0]} with {testData[1]}", "")


def absoluteRelativeTests():
    TEST_FOLDER_NAME = "testFolder"
    data = [
        # (command_to_create, reference_name),
        (f"touch {TEST_FOLDER_NAME}/file", "file"),
        (f"mkdir {TEST_FOLDER_NAME}/folder", "folder"),
    ]

    # Test command for file/folder
    for testData in data:
        test(buildInput([
                         # Create a testing folder
                         f"mkdir /{TEST_FOLDER_NAME}",
                         # Create a file/folder in testing folder
                         f"{testData[0]}",
                         # List the file/folder
                         f"ls {TEST_FOLDER_NAME}/{testData[1]}",
                         # Remove the file/folder
                         f"rm {TEST_FOLDER_NAME}/{testData[1]}",
                         # Cd into testing folder and list everything in it
                         f"cd {TEST_FOLDER_NAME}",
                         # Should print message about empty output
                         "ls",
                         "quit"]),
             buildOutput([
                 PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
                 f"{testData[1]} {getUser()} {getPerm(DEFAULT_PERMISSION)}\n",
                 PRMOPT_MSG, PRMOPT_MSG, PRMOPT_MSG,
                 NO_FILE_MSG,
                 PRMOPT_MSG]),
             # absolute functionality
             f"Test: absolute/relative functionality for {testData[1]}", "")


def test(inputStr, ouputStr, testName, testErr):
    """
    Run command with given inputStr,
    check if command's output is the same as given output
    if not print error
    """
    result = subprocess.run(f"./{BIN_FILE}",  input=inputStr,
                            shell=True, cwd=f"./{ARENA_FOLDER}", text=True,
                            capture_output=True)
    # Check if the command was successful
    if result.stdout == ouputStr:
        printSuccess(f"[{testName}]")
    else:
        if testErr == "":
            printError(f"[{testName}]")
        else:
            printError(f"[{testName}] {testErr}")

        print(f"input: {inputStr}")
        print(f"expected output: {ouputStr}")
        print(f"actual output: {result.stdout}")


def buildOutput(outputArr):
    outputStr = ""

    for element in outputArr:
        outputStr += element

    return outputStr


def buildInput(inputArr):
    inputStr = ""

    for element in inputArr:
        inputStr += element + "\n"

    return inputStr


def compileCode(printStatus=True) -> bool:
    if not os.path.exists(ARENA_FOLDER):
        os.makedirs(ARENA_FOLDER, mode=0o755)

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


def getUser():
    return os.getlogin()


def getPerm(perm):
    permStr = ""

    permsMap = {
        READ_PERMISSION: "r",
        WRITE_PERMISSION: "w",
        EXECUTE_PERMISSION: "x"
    }

    tmpPerm = perm
    for key, value in permsMap.items():
        if (tmpPerm - key >= 0):
            tmpPerm -= key
            permStr += value
        else:
            permStr += "-"

    return permStr


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


if __name__ == "__main__":
    main()
