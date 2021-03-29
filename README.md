# ACSF2-Reader
This is a python reader for the ACSF time-series dataset [[1](https://ieeexplore.ieee.org/abstract/document/7007996?casa_token=sxDLWbtPKK8AAAAA:51LbIRoHtLAYzbzfdB4vv1SEtLNOUfB7u2kPkxJEEFjhjDMHAlzyGl3hgykj5GNNS1ImN8GbOA)]. 

In this dataset there are energy consumption recordings of 15 different household devices. The recodings are done over 1 hour with a recoding at every 10 seconds, resulting in time-series of ~360 steps. 

The classes are:

 ```{'Monitor': 0,
 'Shaver': 1,
 'Microwave oven': 2,
 'Computer station': 3,
 'Hi-Fi system': 4,
 'Printer': 5,
 'Kettle': 6,
 'Laptop': 7,
 'Mobile phone': 8,
 'Lamp CFL': 9,
 'Fridge / Freezer': 10,
 'Fan': 11,
 'Coffee machine': 12,
 'TV': 13,
 'Lamp Inc.': 14}
 ```



This reader is created to make the use of the data more convinients and offers some tools to make your life easier. 

The most important features are shown in ```GettingStarted.ipynb```



If there are questions about the dataset or the reader do not hesitate to contact me.