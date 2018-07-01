from setuptools import setup

setup(
    name='FTT',
    version='1.0',
    author='Michal Brauner',
    author_email='michal.br@gmail.com',
    python_requires='>3.5.0',
    setup_requires=[
        'numpy>=1.14.2',
        'scipy'
    ],
    install_requires=[
        'pandas',
        'scipy',
        'requests>=2.15',
        'urllib3>=1.11',
        'numpy>=1.14.2',
        'scikit_learn>=0.19.1',
    ],
)
