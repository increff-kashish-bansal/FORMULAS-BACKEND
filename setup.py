from setuptools import setup, find_packages

setup(
    name="formulas",
    version="1.0.0",
    packages=["src"],
    include_package_data=True,
    install_requires=[
        "fastapi>=0.116.0",
        "uvicorn>=0.28.0",
        "python-multipart>=0.0.20",
        "openpyxl>=3.1.5",
        "pandas>=2.3.1",
        "xlcalculator>=0.5.0",
        "numpy>=1.26.4",
        "numpy-financial>=1.0.0",
        "scipy>=1.16.0",
        "python-dateutil>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4.1",
            "pytest-asyncio>=1.0.0",
            "pytest-cov>=6.2.1",
            "black>=24.3.0",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "formulas-cli=src.cli:main_wrapper",
        ],
    },
    python_requires=">=3.8",
    author="Formulas Team",
    author_email="info@formulas.example.com",
    description="A tool to convert Excel formulas to Python code",
    keywords="excel, formulas, python, conversion",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 