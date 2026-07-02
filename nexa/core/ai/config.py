import os

class AgentConfig:
    IGNORE_LIST = [
        '.git',
        'node_modules',
        'vendor',
        'dist',
        'build',
        '__pycache__',
        '.idea',
        '.vscode',
        '.nexa',
        'nexa.egg-info',
        'nexa_framework.egg-info'
    ]
