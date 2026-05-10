import sys

from nexa.commands.run import handle as run_command
from nexa.commands.new import handle as new_command
from nexa.commands.startapp import handle as startapp_command
from nexa.commands.install import handle as install_command
from nexa.commands.build import handle as build_command
from nexa.commands.makeapi import (
    handle as makeapi_command
)

import subprocess


def main():
    args = sys.argv[1:]

    if not args:
        print('Nexa CLI')
        return

    command = args[0]

    if command == 'run':
        run_command(args[1:])

    elif command == 'new':
        new_command(args[1:])

    elif command == 'startapp':
        startapp_command(args[1:])

    elif command == 'install':
        install_command(args[1:])

    elif command == 'build':
        build_command(args[1:])
    
    elif command == 'make:api':
        makeapi_command(args[1:])

    else:
        subprocess.run([
            'python',
            'manage.py',
            *args
        ])


if __name__ == '__main__':
    main()