from setuptools import setup, find_packages


setup(
    name='pyclts',
    version='3.0.1',
    description='A python library for the handling of phonetic transcriptions',
    author='Johann-Mattis List, Cormac Anderson, Tiago Tresoldi, and Robert Forkel',
    author_email='mattis.list@lingpy.org',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='',
    license='Apache 2.0',
    url='https://github.com/cldf-clts/pyclts',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'clts=pyclts.__main__:main',
        ],
    },
    platforms='any',
    python_requires='>=3.5',
        install_requires=[
        'attrs>=18.2',
        'clldutils>=3.5',
        'cldfcatalog>=1.3',
        'csvw>=1.6',
        'uritemplate',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=6',
            'pytest-mock',
            'pytest-cov',
            'coverage',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
