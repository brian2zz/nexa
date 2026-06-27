from setuptools import setup, find_packages

setup(
    name="nexa-cli",
    version="1.0.0",
    description="Nexa AI Framework - Autonomous Coding Assistant",
    author="Nexa Team",
    packages=find_packages(),
    install_requires=[
        # Dependencies yang kita butuhkan
        "click>=8.0.0",
        "requests>=2.25.0",
        "colorama>=0.4.4",
        "rich>=10.0.0",
        "prompt_toolkit>=3.0.0",
        "inquirer>=3.1.3",
        "groq>=0.4.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nexa=nexa.cli:main",
        ],
    },
    python_requires=">=3.8",
)