# Overview

This utility aims to simplify patching a boot image for an ARM/ARM64 device on a PC. It is designed to run on WSL2.

## Prerequisites

* You need to have `adb` installed on windows and `dos2unix` on your wsl2 distro.
* You need to have USB debugging Enabled and configured. Check if your devices appear in WSL2 when running `<path to adb> devices` with device connected via USB.

## Assumptions
The script presumes the location of the adb file to be `C:\ProgramData\chocolatey\bin\adb.exe`. If you have installed adb elsewhere on windows, make sure to update the path to adb here and here as shown in this commit.

## How to use

* Plug your phone via USB and make sure adb is properly set up: your device should appear when running `adb devices`.
* Run `sh boot_patch.sh boot.img`
* The patched file `new-boot.img` will/should have the exact sha256 hash as the `magisk_patched-*.img` that's patched using an android device. 

