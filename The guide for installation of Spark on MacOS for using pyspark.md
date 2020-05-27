# The guide for installation of Spark on MacOS for using pyspark

## 1. Assumption:

- a. You have installed python3 on your system

  ```shell
  $ python --version
  Python 3.7.7
  ```

- b. You do not want to use pip to install pyspark. If you do, please refer to [PypI website](https://pypi.org/project/pyspark/)

  > The Python packaging for Spark is not intended to replace all of the other use cases. This Python packaged version of Spark is suitable for interacting with an existing cluster (be it Spark standalone, YARN, or Mesos) - but does not contain the tools required to set up your own standalone Spark cluster. At its core PySpark depends on Py4J (currently version 0.10.7), but some additional sub-packages have their own extra requirements for some features (including numpy, pandas, and pyarrow).

  

- c. You Download the newest version of spark from [the official site](https://spark.apache.org/downloads.html). Currently, I use the version 2.4.5 (Feb 05 2020)

## 2. unzip related files and add configuration

Most posts said it needs java and scala as **prerequisite**, so I download the related files. However, the process of [this website](https://jmedium.com/pyspark-in-mac/)  and [another](https://medium.com/@GalarnykMichael/install-spark-on-mac-pyspark-453f395f240b) that I think are the most simple and easy way to use pyspark in jupyter.

```shell
$ tar-xvzf spark-2.4.5-bin-hadoop2.7.tgz
```

and Add it to the .zshrc or .bash_profile

```shell
# >>>>   spark configuration    >>>>
export SPARK_HOME=/Users/kadima/server/spark-2.4.5-bin-hadoop2.7
export PYSPARK_PYTHON=python3
export PATH=$JAVA_HOME/bin:$SPARK_HOME:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
export PYSPARK_PYTHON=/Users/kadima/anaconda3/bin/python3.7
# the following setups will pop up a jupyter notebook when you type "pyspark" in the terminal
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS='notebook'
```

## 3. findspark

If you do not like the way of typing *pyspark* in the terminal and poping up the correspoding jupyter notebook, you can normally start your jupyter and then use the package named findspark as follows:

```python
import pandas as pd
import numpy as np
import os
import sys
import findspark # import the findspark lib
findspark.init() #initialization, it will automatically search the location of pyspark
from pyspark import SparkConf, SparkContext # without the findspark, this line will report error


# sc = pyspark.SparkContext(appName="spark_v1")
conf = SparkConf().setMaster("local").setAppName("My App")
sc = SparkContext(conf = conf)
```

### Output:

-----

**SparkContext**

[Spark UI](http://10.1.5.157:4040/)

- Version

  `v2.4.5`

- Master

  `local`

- AppName

  `My App`

-------



## Now you can enjoy your spark !

