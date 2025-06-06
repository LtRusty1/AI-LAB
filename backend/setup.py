from setuptools import setup, find_packages

setup(
    name="ai-lab-backend",
    version="0.1.0",
    packages=find_packages(include=["ai_lab", "ai_lab.*"]),
    install_requires=[
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain-openai",
        "langgraph",
        "rich",
    ],
) 