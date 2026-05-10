import os
import shutil
import subprocess


def handle(args):

    # Check npm installed
    if not shutil.which('npm'):

        print('npm is not installed')
        return

    package_json = os.path.join(
        os.getcwd(),
        'package.json'
    )

    if not os.path.exists(package_json):

        print('package.json not found in root')
        return

    print('Installing dependencies...')

    subprocess.run(
        'npm install',
        cwd=os.getcwd(),
        shell=True
    )

    print('Dependencies installed')