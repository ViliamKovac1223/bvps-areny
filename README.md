# Tests For bvps
This repo contains 3 programs that can test first 3 assignments from bvps class
on TUKE. All of these programs are made to work on Linux (WSL should be fine
too though). All testing programs check output from your program and compare it
to the expected output. This comparison doesn't use regex so your output has to
be exactly what tests are expecting. At the start of every testing program
there are constants for expected messages, feel free to adjust them to your
needs.

If you don't study at TUKE but somehow you ended up here, the word ``arena``
refers to program that tests assignments. It's just a slang that TUKE students
use.

## Requirements
- Linux system (WSL should be fine too)
- Python 3.x

## General Troubleshooting
- Give arenaX.py file execution permission.
```bash
chmod +x arenaX.py
```
- Check out constants on the start of every arena

# Encryption Assignment
Before running this test the new testing environment needs to be initialized
with following command. 

```bash
./arena1.py -i
```

This initialization will need internet connection to download testing file.
After initialization this program doesn't require internet connection.

Usage:
```bash
arena1.py -h # Prints help menu
arena1.py -i # Inits testing environment
arena1.py -r # Runs all tests
```

## Known Issues Under WSL:
Test with ``weirdOut`` will most likely fail under WSL. This test fails because
all file privileges on NTFS under WSL are 777 but this test require the
privileges for this file to be 006 and file cannot be set to this privileges on
NTFS under WSL. So if this test fails under WSL, don't worry about it.

# Hashing Assignment
This time testing environment is initialized by the program while running
tests, so no need to initialize testing environment manually. Yet the manual
initialization option has stayed in the program, you can manually initialize
testing environment and copy ``hesla.csv``, ``info.txt`` files so you can test
manually with those generated files or you can submit those files along with
your assignment.

Usage:
```bash
arena2.py -h # Prints help menu
arena2.py -i # Inits testing environment
arena2.py -r # Runs all tests
```

## Important Note
Your assignment program has to support ``--hash <password>`` flag. This hash
flag is used by arena to generate ``hesla.csv`` file. Your assignment program
after given ``--hash <password>`` flag will print hash of the password on the
stdout. After printing hashed password the program will shut down and will not
print anything else on the stdout.

Example code for printing hashed password on the stdout.
```c
#define HASH_FLAG 1

char * hash(char * password);

....

#if HASH_FLAG
// Code for --hash flag
if (argc > 2 && strcmp(argv[1], "--hash") == 0) {
    char * hashedPassword = hash(argv[2]);
    printf("%s\n", hashedPassword);
    free(hashedPassword);
    exit(0);
}
#endif
```

# File System Emulation Assignment
Because this assignment doesn't have to work with any files, the arena is much
more simple for usage.

Usage:
```bash
arena3.py # Runs all tests
```

# Warranty
None of the authors, contributors, administrators, or anyone else connected
with this project, in any way whatsoever, can be responsible for your use of
this project.

Don't forget this was made by the student so use it at your own risk. If all
tests are passed by this arena it doesn't mean that they will pass on official
arena.

# Fake internet money
If you like my work and want to support me by some fake internet money, here is my monero address

8AW9BM1E5d67kaX3SiAT6B91Xvn4urhBeGL3FUWezSkRarSmxrAfvUK5XD5VcasXStHT6aYXwjVMrhm4YCNXTqGpRUekQ6i
