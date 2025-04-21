from setuptools import setup, find_packages

setup(
    name="image_gen_benchmark",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "click",
        "pydantic",
        "sqlalchemy",
        "aiofiles",
        "jinja2",
        "pillow",
        "python-dotenv",
        "openai>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "benchmark=benchmark.cli:cli",
        ],
    },
)