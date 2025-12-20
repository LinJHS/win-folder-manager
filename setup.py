import os
from setuptools import setup, find_packages


def read_requirements():
    req_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'requirements.txt')
    if not os.path.exists(req_file):
        return []
    with open(req_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


setup(
    name='win-folder-manager',
    use_scm_version=True,
    description='A lightweight, Flask-powered web file manager for Windows. Manage, browse, and transfer files via a clean browser UI.',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={'console_scripts': ['win-folder-manager=manager.app:main']},
    license='GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
)
