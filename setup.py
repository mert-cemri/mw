"""
Setup configuration for the AgentDash library.
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AgentDash - Multi-Agent Systems Failure Taxonomy Library"

# Read version from __init__.py
def read_version():
    version_path = os.path.join(os.path.dirname(__file__), 'agentdash', '__init__.py')
    with open(version_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

setup(
    name="agentdash",
    version=read_version(),
    author="MAST Research Team",
    author_email="cemri@berkeley.edu",
    description="Multi-Agent Systems Failure Taxonomy (MAST) annotation library using LLM-as-a-Judge",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/multi-agent-systems-failure-taxonomy/MAST",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
        ],
    },
    keywords="multi-agent systems, failure taxonomy, llm judge, ai evaluation, mast, agentdash",
    project_urls={
        "Bug Reports": "https://github.com/multi-agent-systems-failure-taxonomy/MAST/issues",
        "Source": "https://github.com/multi-agent-systems-failure-taxonomy/MAST",
        "Documentation": "https://github.com/multi-agent-systems-failure-taxonomy/MAST",
    },
    include_package_data=True,
    package_data={
        'agentdash': ['*.txt', 'data/*.txt'],
    },
)