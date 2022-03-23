# Overview

This scripts aims in simplifing patching and installing Magisk after a LineageOS **for microG** update.

It has been made to run on Linux x86 or x64 and patch a boot image for an ARM device.

It detects LineageOS **for microG** version via adb, download the ROM, extracts `payload.bin` and dumps `boot.img`, patches it with Magisk, and flashes it.

:warning: **This has only been tested on a FP3 device, at the time of writing with LineageOS for microG 18.1 (March 17, 2022 build) Magisk v24.3** :warning:

## Run on an other device

Before to run this script for an other device, please make sure you understand what you run and every step of the script.
**I won't be responsible if anything goes wrong.**

The script is designed to:
 * run the script `boot_patch.sh boot.img` with KEEPVERITY and KEEPFORCEENCRYPT to true
 * install Magisk by patching the **boot image** and **not the recovery image**.
 * run to flash the boot image in **boot_a** or **boot_b** partition (the FP3 way) and **not boot partition**


If you fit the conditions above, you have to make sure the patch `KEEPVERITY=true KEEPFORCEENCRYPT=true sh boot_patch.sh` outputs the same boot image than the Magisk Manager app:
 * patch boot via Magisk Manager app
 * run `boot_patch.sh boot.img` manually
 * compare both files `magisk_patched-*.img` and `new-boot.img` with diff or by comparing hashes.

 If **and only if** both output files are the same and you meet all the conditions, you can try the python script.

# Prerequisites

## In PATH

You need to have on your system (in your PATH):
 * adb
 * fastboot
 * payload-dumper-go
 * python (3)
 * dos2unix


## USB debugging

You need to have USB debugging Enabled and configured.
Check your devices appears when running `adb devices` with device connected via USB.

## Using

Replace the `device` variable by your device code, as [listed here](https://download.lineage.microg.org/).

Plug your phone via USB and make sure adb is properly set up: your device should appear when running `adb devices`.
Run `python magisk_boot_flasher.py`.


# Run patch boot locally

That's how we can run Magisk's `boot_patch.sh` on Linux x86 or x64 and patch a boot image for an ARM device

> Tested with Magisk v24.3 with FP3

* Get Magisk `.apk`
* Extract it

Keep in the same folder:
* `assets/boot_patch.sh` -> `boot_patch.sh`
* `assets/util_functions.sh` -> `util_functions.sh`
* `lib/x86_64/libmagiskboot.so` -> `magiskboot`
* `lib/armeabi-v7a/libmagisk32.so` -> `magisk32`
* `lib/arm64-v8a/libmagisk64.so` -> `magisk64`
* `lib/arm64-v8a/libmagiskinit.so` -> `magiskinit`

You can delete all the rest.

In util_functions.sh:
* Change function `ui_print()` to only contain `echo "$1"`
* Change every `getprop` command, to `adb shell getprop`, to go run it on device rather than locally.

You can now run:
`sh boot_patch.sh boot.img`

The outpout file `new-boot.img` has the exact same sha256 hash as the `magisk_patched-*.img`, so we can consider it works :)

