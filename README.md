# Overview

This utility aims to simplify patching a boot image for an ARM/ARM64 device on a PC. It is designed to run on WSL2. This has been tested only on ManjaroWSL.

## Prerequisites

* You need to have `adb` installed on windows and `dos2unix` on your wsl2 distro.
* You need to have USB debugging Enabled and configured. Check if your devices appear in WSL2 when running `<path to adb> devices` with device connected via USB.

## Assumptions
The script presumes the location of the adb file to be `C:\ProgramData\chocolatey\bin\adb.exe`. If you have installed adb elsewhere on windows, make sure to update the path to adb [here](https://github.com/sileshn/Magisk-WSL2-Patcher/blob/master/util_functions.sh#L39) and [here](https://github.com/sileshn/Magisk-WSL2-Patcher/blob/master/util_functions.sh#L39) as shown in [this](https://github.com/sileshn/Magisk-WSL2-Patcher/commit/7cf8d041f89ce30608574c2c56af4fba69cca68c) commit.

## How to use

* Plug your phone via USB and make sure adb is properly set up. Your device should appear when running the command `<path to adb> devices`.
* Copy your boot image to the same folder containing the scripts.
* Run `sh boot_patch.sh boot.img`
* The patched file `new-boot.img` will be saved in the same directory. It will/should have the exact sha256 hash as the `magisk_patched-*.img` that's patched using an android device. 

