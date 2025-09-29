prompt = """
Given a few rows of new data, please normalize the data according to some existing rows and data format requirement (if exists) in a database so as to match with database schema. Note that each data value is splited by ';  ' in one row. 
Here is two examples:

Example 1

Input:
New data: 
1939;  7;  Erzincan Province in Turkey;  20.34;  27 Dec;  two
1968;  5.2;  China, Shanghai;  10.3;  December 2 2000;  10

Existing data: 
1940;  7.7;  Romania, Vrancea County;  133.0;  November 10;  31
1941;  5.8;  Yemen, Razih District;  35.0;  January 11;  3
1942;  7.0;  Turkey, Erbaa;  10.0;  December 20;  9

Output:
1939;  7.0;  Turkey, Erzincan Province;  20.3;  December 27;  2
1968;  5.2;  China, Shanghai;  10.3;  December 2;  10



Example 2

Input:
New data: 
December 2 2000
June 10 2004
1889 09 27

Data format requirement:
Birth of Data: date of birth of a single, Text, MM-DD-YYYY

Output:
12-02-2000
06-10-2024
09-27-1889


Example 3

Input:
New data: 
134
nine
six

Data format requirement:
Birth of Data: number of killed people in an earthquake, Int

Output:
134
9
6



Using the format provided above, normaliza a new row given some existing rows as the examples.  Please strictly follow the output format like the given example and do not output any extra words.

"""