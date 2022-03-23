import requests
import hashlib
import sys
import zipfile
from tqdm import tqdm
import subprocess
import time

device = 'FP3'
magiskdir = 'Magisk-v24.3'


def yes_or_no(question, default=None):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def isMagiskInstalled():
    cmdlist = ['adb', 'shell', 'command', '-v', 'su']
    sp = subprocess.run(cmdlist, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
    if sp.returncode != 0:
        return False
    else:
        return True


def checkInstalledVersion():
    cmdlist = ['adb', 'shell', 'getprop', 'ro.lineage.version']
    sp = subprocess.run(cmdlist, stdout=subprocess.PIPE)
    currentversion = sp.stdout.decode('UTF-8').rstrip()
    return currentversion


def downloadUpdate(device, version):
    filename = f"lineage-{version}.zip"
    url = f'https://download.lineage.microg.org/{device}/{filename}'
    r = requests.get(url, stream=True)
    with tqdm.wrapattr(open(filename, "wb"), "write",
                       miniters=1, desc=filename,
                       total=int(r.headers.get('Content-Length'))) as fout:
        for chunk in r.iter_content(chunk_size=4096):
            fout.write(chunk)
    fout.close()

    print('Comparing hashes...', end='', flush=True)
    checkHash(filename)
    print('  [OK]')

    return filename


def checkHash(filename):
    filehash = sha256sum(filename)

    hurl = f'https://download.lineage.microg.org/{device}/{filename}.sha256sum'
    r = requests.get(hurl)
    correcthash = r.text.split(' ')[0]

    if filehash != correcthash:
        print(f'\n[ERR]: {filename}')
        print(f'[ERR] Computed hash: {filehash}')
        print(f'[ERR] Should be:     {correcthash}')
        sys.exit("Error: File hash doesn't match ! Aborting.")


def sha256sum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


def patchBootimg():
    cmd = ['sh', f'{magiskdir}/boot_patch.sh', '../boot.img']
    env = {"KEEPVERITY": "true", "KEEPFORCEENCRYPT": "true"}
    sp = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
    if sp.returncode != 0:
        sys.exit('\nERROR: boot_patch.sh exited with errors!')


def rebootToBootloader():
    cmd = ['adb', 'reboot', 'bootloader']
    subprocess.run(cmd, stdout=subprocess.DEVNULL)

    cmd = ['fastboot', 'devices']
    while "Waiting for device in fastboot":
        time.sleep(2)
        sp = subprocess.run(cmd, stdout=subprocess.PIPE)
        if sp.stdout != b'':
            break


def flashBoot():
    currentSlot = getCurrentSlot()
    cmd = ['fastboot', 'flash', f'boot_{currentSlot}',
           f'{magiskdir}/new-boot.img']
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def getCurrentSlot():
    cmd = ['fastboot', 'getvar', 'current-slot']
    ps = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    currentSlot = ps.stdout.decode('UTF-8').rstrip()
    currentSlot = currentSlot.split('slot: ')[1].split('\n')[0]
    return currentSlot


def cleanUp(filename):
    cmd = ['rm', 'payload.bin', 'boot.img', filename]
    subprocess.run(cmd, stdout=subprocess.DEVNULL)

    magiskFilelist = ['kernel', 'kernel_dtb', 'ramdisk.cpio', 'new-boot.img',
                      'stock_boot.img']
    for f in magiskFilelist:
        cmd = ['rm', f'{magiskdir}/{f}']
        subprocess.run(cmd, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    print("Checking if Magisk already installed...", end='', flush=True)
    if isMagiskInstalled():
        print("\nIt seems Magisk is already installed (su in PATH).")
        print("Aborting.")
        sys.exit()
    print('  [OK]')

    print("Getting installed verion (via adb)...", end='', flush=True)
    installedversion = checkInstalledVersion()
    print('  [OK]')

    print("Seems you have haven't flashed yet Magisk on the new firmware.")
    if not yes_or_no("Would you like do download the new firmware?"):
        sys.exit()

    print(f"Downloading version: {installedversion}")
    filename = downloadUpdate(device, installedversion)

    print("Download finished, extracting payload.bin from release...", end='',
          flush=True)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extract('payload.bin')
    print('  [OK]')

    print("Extracting boot.img...", end='', flush=True)
    cmd = ['payload-dumper-go', '-p', 'boot', '-o', '.', 'payload.bin']
    subprocess.run(cmd, stdout=subprocess.DEVNULL)
    print('  [OK]')

    print("Patching boot.img with Magisk scripts...", end='', flush=True)
    patchBootimg()
    print('  [OK]')

    if not yes_or_no("Would you like to flash the new boot image?"):
        sys.exit()

    print("Make sure your device is connected via USB.")
    input("Press Enter to continue...")

    print('Rebooting device to bootloader...', end='', flush=True)
    rebootToBootloader()
    print('  [OK]')

    print('Flashing new boot image...', end='', flush=True)
    flashBoot()
    print('  [OK]')

    print('Cleaning up files...', end='', flush=True)
    cleanUp(filename)
    print('  [OK]')

    print('Rebooting device, enjoy Magisk! ;)')
    cmd = ['fastboot', 'reboot']
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
