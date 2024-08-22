import setuptools

setuptools.setup(name='l3ml',
    version='0.1',
    description='',
    author='Joachim K',
    author_email='jokteur@gmail.com',
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'Pillow',
        'bokeh>=1.3.4',
        'pydicom'
    ],
    python_requires='>=3.6'
)
