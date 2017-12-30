# CS-E4600 — Programming project

## Author: Aditya Kaushik, 662862

### For computing the exact statistics, follow these steps:
- **Step1:** Pass the locations of the respective network-edgelist to corresponding file for calculating the largest strongly, weakly connected components along with the desired output location: *boost-graph-cpp/lscc_boost.cpp* (lines 89, 172), *boost-graph-cpp/lwcc_boost.cpp* (lines 98, 133)
- **Step2:** Use the *boost-graph-cpp/apsp.cpp* (line 65) to pass the location of the respective component. Prints the network component statistics of that component
- **Requirements:** C++11, boost-cpp (http://www.boost.org/doc/libs/1_61_0/more/getting_started/unix-variants.html)

### For computing the approximate statistics, follow these steps:
- **Requirements:** https://networkx.github.io/, numpy, python (> 2.2)
- Please start with the *source/main.py* file and follow through the documentation of each function
