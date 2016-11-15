## Introduction 
This is a program that detects events using Tweets. 

## Installation
The first step is to install Python. Afterthat, you install the necessary packages : numpy, python-dateutil, scipy, scikit-learn, matplotlib. You can execute the following command lines:

```
sudo pip install numpy
sudo pip install python-dateutil
sudo pip install scipy
sudo pip install -U scikit-learn
sudo pip install matplotlib
```
## How to use it
In order to execute this program, we use the following command line
```
Python main.py --inputFile <the input file path> --outputPath <the output file path>
```
An example using the input file  "smallFileTweets.csv" is:
```
Python main.py --inputFile smallFileTweets.csv --outputPath foundEvents.txt
```
