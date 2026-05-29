import os
from setuptools import setup, find_packages

setup(
    name='nexa-framework',
    version='0.1.9',
    author='Brian',
    description='A full-stack framework for Django and Vue.js applications',
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/brian/nexa',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=4.0',
        'djangorestframework',
        'django-cors-headers',
        'whitenoise',
    ],
    entry_points={
        'console_scripts': [
            'nexa=nexa.cli:main'
        ]
    },
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)