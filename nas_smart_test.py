#! /bin/python
import os
import sys
import time
import argparse
import subprocess


def write_output(args, output):
    if 'out_time' not in args:
        args.out_time = time.strftime("%Y_%m_%d_%H%M%S", time.localtime())

    fname = 'selftest_' + args.type + '_' + args.out_time + '_' \
            + args.device.replace('/', '_')

    if args.output_into_subfolders:
        folders = [f[0] for f in os.walk(args.output_path)]
        folders.remove('.')

    if not args.output_into_subfolders or len(folders) == 0:
        folders = [args.output_path]

    for folder in folders:
        with open(os.path.join(folder, fname), 'a') as f:
            f.write(output)
            f.write('\n')


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='NASSelftest',
        description=('This script is intended to be run with cron. It starts a'
                     'S.M.A.R.T. self test and regularly polls the device to'
                     'prevent it from going to sleep. The script exits when the'
                     'self test has finished and it writes the result into all'
                     'shares of the NAS.'))

    parser.add_argument('type',
                        help="Type of self test, typically 'short' or 'long'.")

    parser.add_argument('device', help=('Device is the path to a HDD Ideally it'
                                        ' refers to HDDs by a permanent reference'
                                        ' such as id (e.g. /dev/disk/by-id/...).'
                                        ' Labels such as /dev/sda can change so'
                                        ' they are not ideal.'))

    parser.add_argument('polling_interval',
                        help=('Time in seconds between subsequent calls to the'
                              ' device to keep it awake.'))

    parser.add_argument('output_path',
                        help='Folder to which the output should be written.')

    parser.add_argument('--output_into_subfolders', action='store_true',
                        help=('If set then the output will be written into all'
                              ' subfolders of output_path. If there are no'
                              ' subfolders then the output will be written into'
                              ' output_path instead.'))

    parser.add_argument('--allow_existing', action='store_true',
                        help=('By default this script will exit if a self test'
                              ' is already running. If this setting is set to'
                              ' True then it will wait until the self test has'
                              ' finished and report the results of that test.'))

    args = parser.parse_args()

    # make sure polling interval is a valid number; I'm doing that manually,
    # instead of using argparse, so we can easily notify the user
    try:  
        args.polling_interval = int(args.polling_interval)

    except ValueError:  # invalid polling interval, needs to be an integer 
        write_output(args, f'Invalid polling interval "{args.polling_interval}".')
        sys.exit()

    return args


def check_device_exists(args):
    if not os.path.exists(args.device):
        write_output(args, f'Device {args.device} does not exist.')
        sys.exit()

    
def wait_for_device(args):
    """Waits until device is ready, exits if not ready after 1 minute."""

    def check():
        p = subprocess.run(['smartctl', '-c', args.device],
                           stdout=subprocess.PIPE)
        out = p.stdout.decode()

        # When the device is slow to respond because it's still spinning up
        for line in out:
            if line.strip() == 'Read Device Identity failed: scsi error device will be ready soon':
                return False

        return True

    count = 0

    while check() is False:
        time.sleep(5)
        count += 1

        if count == 20:
            write_output(args, 'Device not ready after 1 minutes.')
            sys.exit()


def selftest_is_running(args):
    """Returns True if a self test is running and false otherwise."""
    p = subprocess.run(['smartctl', '-c', args.device], stdout=subprocess.PIPE)
    out = p.stdout.decode().splitlines()

    for line in out:
        if line.startswith('Self-test execution status:'):
            if line.strip().endswith('Self-test routine in progress...'):
                return True
            return False

        if line.startswith('Someting device not ready'):
            return False
    return False


def start_selftest(args):
    """Starts a self test and returns if it was started successfully."""
    p = subprocess.run(['smartctl', '-t', args.type, args.device],
                       stdout=subprocess.PIPE)
    out = p.stdout.decode().splitlines()

    for line in out:
        if line.strip() == 'Testing has begun.':
            return True

    write_output(args, 'Couldn\'t start self test.')
    sys.exit()


def save_status(args):
    p = subprocess.run(['smartctl', '-x', args.device], stdout=subprocess.PIPE)
    write_output(args, p.stdout.decode())


if __name__ == '__main__':
    args = parse_arguments()
    check_device_exists(args)
    wait_for_device(args)

    if selftest_is_running(args):
        write_output(args, 'A self test is already in progress.')

        if not args.allow_existing:
            write_output(args, 'Parameter allow_existing is False, exiting.')
            sys.exit()
    else:
        start_selftest(args)

    while True:
        time.sleep(args.polling_interval)

        if not selftest_is_running(args):
            break

    # save output to file
    save_status(args)
