## bme590hrm
####**Heart Rate Monitor Assignment**

#####*Deepthi Nacharaju*

[![Build Status](https://travis-ci.org/Deepthi-Nacharaju/bme590hrm.svg?branch=master)](https://travis-ci.org/Deepthi-Nacharaju/bme590hrm)

**Notes on Operation:**
- Changing the butterworth cutoff frequency changes progam's ability to detect different types of peaks. Frequently used values include *0.0045, 0.005 (default), 0.0055 and 0.006*. These can be changed in the main function as *filter_value*.
- If the maximum distance between two peaks is more than a specific distance from the average distance (indicating wide distribution), peak detection will run again after adding 0.002 to the cutoff frequency. This will cycle 3 times. 
**Additional Capabilities:**

- Opens and writes to an excel file in data folder called *Beat_Tracking.xlsx*. Records number of beats found over the entire interval.  
Then highlights the cell in different colors if different than the hand counted value in the previous column. 
Use this to quickly determine how changes affect peak detection functionality across all 30+ csv files.

- Running *main.py* from the terminal followed by a tuple with starting and ending time points will allow user to interactively change bpm calculation window. 

For example:

```
python main.py (0, 60)
```
will choose 0 to 60 seconds. This can also be changed from within the main.py when calling *user_input()*


####MIT License

Copyright (c) [2018] [Deepthi Nacharaju]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.