from setuptools import setup, find_packages

setup(
    name="ai-hedge-fund",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'gradio',
        'pandas',
        'numpy',
        'matplotlib',
    ],
)