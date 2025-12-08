from setuptools import setup

setup(
    name='python-cli-app',
    version='1.0.0',
    author='harrie19',
    description='Eine interaktive, erweiterbare Kommandozeilenanwendung.',
    py_modules=["main", "config", "commands", "command_processor"],
    entry_points={
        'console_scripts': [
            'cli-app=main:run',
        ],
    },
    python_requires='>=3.7',
)
