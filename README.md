# bme590hrm
Heart Rate Monitor Assignment
Deepthi Nacharaju

Notes on Operation:
Changing the butterworth cutoff frequency changes progam's ability to detect different types of peaks. Frequently used values include 0.0045, 0.005 (default), 0.0055 and 0.006. These can be changed in the main function as filter_value.

Additional Capabilities: 

Opens and writes to an excel file in data folder called "Beat_Tracking.xlsx"; Records number of beats found and highlights the cell yellow if different than the hand counted value in the previous column. Use this to quickly determine how changes affect peak detection functionality across all 30+ csv files.

Running load_data.py from the terminal followed by a tuple with starting and ending time points will allow user to interactively change bpm calculation window