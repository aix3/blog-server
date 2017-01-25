from setuptools import setup, find_packages

setup(
    name='Blog',
    version=1.0,
    author='xq.tian',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'aiohttp>=1.2.0',
        'aiomysql>=0.0.9',
        'Jinja2>=2.9.4',
    ]
)