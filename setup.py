from setuptools import setup, find_packages

setup(
    name="Inference_Monitor",
    version="0.1.0",
    author="최지훈",
    description="AI 추론 중 CPU, 메모리 사용량을 모니터링하고 시각화하는 도구",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "matplotlib",
    ],
    python_requires=">=3.6",
)
