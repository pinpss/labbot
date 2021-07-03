from  setuptools import setup, find_packages

setup(name="labbot",
      packages=find_packages(),
      install_requires=["joblib",
                        "boltons",
                        "jinja2"],
      )
