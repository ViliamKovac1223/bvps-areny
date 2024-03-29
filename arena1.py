#!/bin/python

import os
import subprocess
import urllib.request
import sys
import getopt
import shutil


COMPILER = "gcc"
COMPILE_CODE = True
SOURCE_CODE_FILE = "zadanie1.c"
BIN_FILE = "zadanie1ArenaBin"
ERROR_OUT = "chyba"
ARENA_FOLDER = ".notArenaFr"
ARENA_FOLDER_READ_ONLY = ARENA_FOLDER + "/readonlyFolder"
LINK_FOR_BIGGER_FILE = "https://raw.githubusercontent.com/ViliamKovac1223/dwm-ViliamKovac1223-build/main/dwm.c"

# Files keys
NO_READ_FILE        = "noRead"
NORMAL_INPUT_FILE   = "normalInput"
READ_ONLY_FILE      = "readonly"
GARBAGE_OUT_FILE    = "garbageOut"
WEIRD_OUT_FILE      = "garbageOut"
ZERO_IN_FILE        = "zeroIn"
FF_IN_FILE          = "ffIn"

# Info about files created in initEnv()
FILES_INFO = {
    # key:              File name, permission, content
    NO_READ_FILE:       ("noRead", 0o000, ""),
    NORMAL_INPUT_FILE:  ("normalInput", 0o644, "this is input file"),
    READ_ONLY_FILE:     ("readonly", 0o444, "this is file is read only"),
    GARBAGE_OUT_FILE:   ("garbageOut", 0o644, ""),
    WEIRD_OUT_FILE:     ("weirdOut", 0o006, ""),
    ZERO_IN_FILE:       ("zeroIn", 0o644, b'\x00' * 500),
    FF_IN_FILE:         ("ffIn", 0o644, b'\xff' * 500),
}
BIG_FILE = ARENA_FOLDER + "/code.c"


def initEnv():
    if os.path.exists(ARENA_FOLDER):
        shutil.rmtree(ARENA_FOLDER)

    # Create folders for testing
    os.makedirs(ARENA_FOLDER, mode=0o755)
    os.makedirs(ARENA_FOLDER_READ_ONLY, mode=0o444)

    # Create all files, with given permissions and content
    for _, fileInfo in FILES_INFO.items():
        filePath = ARENA_FOLDER + "/" + fileInfo[0]
        # Create file and set its content
        if type(fileInfo[2]) == str:
            with open(filePath, 'w') as file:
                file.write(fileInfo[2])
        else:
            with open(filePath, 'wb') as file:
                file.write(fileInfo[2])

        # Set permissions for the file
        os.chmod(filePath, fileInfo[1])

    try:
        urllib.request.urlretrieve(LINK_FOR_BIGGER_FILE, BIG_FILE)
    except Exception:
        print("either get internet connection while initing env, or manually create file (the file should have a lot of text): ")
        print(BIG_FILE)


def removeFile(file):
    if os.path.exists(file):
        os.remove(file)


def compileCode():
    if COMPILE_CODE is False:
        return
    removeFile(BIN_FILE)
    os.system(f"{COMPILER} {SOURCE_CODE_FILE}  -o {BIN_FILE}")
    if not os.path.exists(BIN_FILE):
        printError("Compilation error")
    else:
        printSuccess("Compilation successful")


def test(flags):
    """
    Runs command with given flags and returns stdout
    """
    command = f"./{BIN_FILE} {flags}"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    # Check if the command was successful
    return result.stdout


def runTests(testsData):
    """
    @param testsData is list filled with tuples.
    Tuples have following format:
        ("flags for command", "output of command")
    """
    testNumber = 0
    for testData in testsData:
        result = test(testData[0])
        testNumber += 1
        if result == testData[1]:  # Test passes
            printSuccess(f"Test number {testNumber}")
        else:  # Test failed, inform poor student about it
            printError(f"Test number {testNumber}")
            print(f"flags: {testData[0]}")
            print(f"expected output: {testData[1]}")
            if len(result) != 0:
                print(f"actual output: {result}")
            else:
                print("actual output: (no ouput)")


def testFlags():
    inputFile = f"{ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]}"
    outputFile = f"{ARENA_FOLDER}/newOut"
    testsData = [
        # {Flags, expected output}

        # Good flags for encryption
        (f"-s -p key -i {inputFile} -o {outputFile}", ""),
        # Good flags for decryption
        # (f"-d -p key -i {inputFile} -o {outputFile}", ""),
        # Both encryption and decryption flags are used
        (f"-s -d -p key -i {inputFile} -o {outputFile}", ERROR_OUT),
        # Missing -p flag
        (f"-s -i {inputFile} -o {outputFile}", ERROR_OUT),
        # Missing password after -p flag
        (f"-s -p -i {inputFile} -o {outputFile}", ERROR_OUT),
        # Missing input file after -i flag
        (f"-s -p key -i -o {outputFile}", ERROR_OUT),
        # Missing output file after -o flag
        (f"-s -p key -i {inputFile} -o", ERROR_OUT),
        # Missing -o flag
        (f"-s -p key -i {inputFile}", ERROR_OUT),
        # Missing -i flag
        (f"-s -p key -o {outputFile}", ERROR_OUT),
        # Empty key
        (f"-s -p \"\" -i {inputFile} -o {outputFile}", ERROR_OUT),
        # No arguments
        ("", ERROR_OUT),
    ]
    print("Flags test:")
    runTests(testsData)
    removeFile(outputFile)


def testFiles():
    newOutFile = f"{ARENA_FOLDER}/newOut"
    testsData = [
        # {Flags, expected output}

        # Good flags for encryption
        (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
        # Good flags for decryption
        # (f"-d -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
        # Read only input file
        (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[READ_ONLY_FILE][0]} -o {newOutFile}", ""),
        # Weird output file (chmod 006)
        (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {ARENA_FOLDER}/{FILES_INFO[WEIRD_OUT_FILE][0]}", ERROR_OUT),
        # Not existing input file
        (f"-s -p key -i {ARENA_FOLDER}/notExistingInputFile -o {newOutFile}", ERROR_OUT),
        # Read only output file
        (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {ARENA_FOLDER}/{FILES_INFO[READ_ONLY_FILE][0]}", ERROR_OUT),
    ]
    print("Files test:")
    runTests(testsData)
    removeFile(newOutFile)


def isFileEmpty(filePath):
    with open(filePath, 'rb') as file:
        fileContent = file.read()

    return len(fileContent) == 0


def areFilesTheSame(filePath, filePath1):
    with open(filePath, 'rb') as file:
        fileContent = file.read()
    with open(filePath1, 'rb') as file:
        fileContent1 = file.read()

    # Compare the contents of the files
    return fileContent == fileContent1


def fullTest():
    pass


def testEncDec():
    print("Encryption/Decryption test:")
    newOutFile = f"{ARENA_FOLDER}/newOut"
    newOriginal = f"{ARENA_FOLDER}/newOrig"
    longKey = "key" * 5000
    removeFile(newOutFile)
    removeFile(newOriginal)

    testEncInfo = [
        (  # Basic test
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p key -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Short key
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p k -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p k -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Long key
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p {longKey} -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p {longKey} -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Zero file
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[ZERO_IN_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p key -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[ZERO_IN_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Zero file and longKey
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p {longKey} -i {ARENA_FOLDER}/{FILES_INFO[ZERO_IN_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p {longKey} -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[ZERO_IN_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # FF file
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[FF_IN_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p key -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[FF_IN_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # FF file and longKey
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p {longKey} -i {ARENA_FOLDER}/{FILES_INFO[FF_IN_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p {longKey} -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[FF_IN_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Big file
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {BIG_FILE} -o {newOutFile}", ""),
                (f"-d -p key -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{BIG_FILE}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Long key and big file
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p {longKey} -i {BIG_FILE} -o {newOutFile}", ""),
                (f"-d -p {longKey} -i {newOutFile} -o {newOriginal}", "")
            ],
            # Which files to compare
            (f"{BIG_FILE}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Check if the encryptions are the same with the same passowrd
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
            ],
            # Which files to compare
            (f"{newOutFile}"),
            (f"{newOutFile}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, True),
        ),

        (  # Check if encryptions are different with different keys
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
                (f"-s -p key1 -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOriginal}", ""),
            ],
            # Which files to compare
            (f"{newOutFile}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, False),
        ),

        (  # Check for error in decryption with wrong password
            # Multiple flags for multiple commands for encryption (flags, outputOfCommand)
            [
                (f"-s -p key -i {ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]} -o {newOutFile}", ""),
                (f"-d -p key1 -i {newOutFile} -o {newOriginal}", ERROR_OUT),
            ],
            # Which files to compare
            (f"{ARENA_FOLDER}/{FILES_INFO[NORMAL_INPUT_FILE][0]}"),
            (f"{newOriginal}"),
            # Results (isEmpty (second file only), areTheSame)
            (False, False),
        ),
    ]

    testNumber = 0
    for encInfo in testEncInfo:
        testNumber += 1

        # Run all testing commands and check their output
        outputs = []
        didCmdsFailed = False
        for cmdFlags in encInfo[0]:
            outputs.append(test(cmdFlags[0]))
            if outputs[-1] != cmdFlags[1]:
                didCmdsFailed = True

        isSecondFileEmpty = isFileEmpty(encInfo[2])
        sameFiles = areFilesTheSame(encInfo[1], encInfo[2])

        if didCmdsFailed is True or isSecondFileEmpty != encInfo[3][0] or sameFiles != encInfo[3][1]:
            # Test failed
            printError(f"Test number {testNumber}")
            i = 0
            for cmdFlags in encInfo[0]:
                print(f"flags: {cmdFlags[0]}")
                print(f"expected output: {cmdFlags[1]}")
                if len(outputs[i]) != 0:
                    print(f"actual output: {outputs[i]}")
                else:
                    print("actual output: (no ouput)")
                i += 1
            print(f"file: {encInfo[2]} is ", "empty" if isSecondFileEmpty else "not empty")
            print(f"file: {encInfo[1]} and {encInfo[2]} are ", "the same" if sameFiles else "not the same")
        else:
            # Test passed
            printSuccess(f"Test number {testNumber}")

    print("If last test fails, it still might be okay.")
    print("Last test is based on the idea that if you try to decrypt file with wrong password it should return the error")

    removeFile(newOutFile)
    removeFile(newOriginal)


def printError(text):
    RED = '\033[91m'    # ] Messes with my lsp if this comment ain't here
    END = '\033[0m'     # ] Messes with my lsp if this comment ain't here
    print(f"{RED}[ERROR] {text}{END}")


def printSuccess(text):
    RED = '\033[92m'    # ] Messes with my lsp if this line ain't here
    END = '\033[0m'     # ] Messes with my lsp if this line ain't here
    print(f"{RED}[OK] {text}{END}")


def help():
    print("Usage:")
    print("arena.py -h # Prints help menu")
    print("arena.py -i # Inits testing environment")
    print("arena.py -r # Runs all tests")


def main(argv):
    # Parse arguments
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
        # Compile code
        compileCode()

        # Run tests
        testFlags()
        testFiles()
        testEncDec()

        # Delete used binary
        removeFile(BIN_FILE)


if __name__ == "__main__":
    main(sys.argv[1:])
