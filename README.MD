# DQX server stub
This proof-of-concept allows to replay the initial login sequence of a Dragon
Quest X client (v3.5.9) on Wii.

![image](https://user-images.githubusercontent.com/7890055/147498885-22ffe2de-533b-48ef-a786-2847f9a5d8ef.png)

**This PoC only works once! It will fail on the 2nd attempt!**
**It will mostlikely corrupt your current progress and save too!**
**Use this PoC at your own risk!**

## Structure
### User
Dolphin emulator's User folder. It holds the savestate and its dependencies
that make the replay possible.

### Lobby forwarder
This server redirects to the lobby server. IIRC, this redirection didn't exist
on Dragon Quest X version 1.

### Lobby server
The replay attack is performed by this server replaying the encrypted login
sequence.

## Approach
A savestate can be used to address the complexity of porting this PoC on
multiple versions of Dragon Quest X. Especially since the network protocol
changed between several versions up until the version 3.5.9.

It has enough state to be able to process the initial login sequence as a legit
version 3.5.9 would do. **However, it will crash if it tries to load any file
supposed to be opened.** In theory, the savestate can be avoided if stricter
prerequisites are met.


By the way, I tried the replay attack on v1, v2 and v3 (disc versions) and they
didn't work. The forwarder was adjusted to use the `--legacy` option but the
game didn't accept the stub server replayed login sequence.

## Prerequisites
### Ultra-shortcut (using savestate)
 - `Python` to launch the servers (should work on both Python2 and Python3)
 - `Dolphin emulator` (with support for build 5.0-15663's savestates)
 - Dragon Quest X Wii installed
   * Tested with v1, v2, v3 from the installers' discs
   * Tested with v3.5.9, the latest available update before the shutdown

### The legit way (without savestate)
 - The game's version is 3.5.9
 - A real NAND tied to a Japanese Wii Shop account is used
 - The DOL files are patched to use Nintendo servers alternatives:
   * [Wiimmfi](https://wiimmfi.de/)
   * **or** [AltWFC](https://github.com/polaris-/dwc_network_server_emulator)

## Usage
### Lobby forwarder
Can be run using Python without additional parameter.
```bash
python lobby_forwarder.py
```

### Lobby stub
Need to be run using a Python interactive shell.
```bash
python -i lobby_stub.py

# In the Python interactive shell
client = lobby_accept(replay=True)
```
