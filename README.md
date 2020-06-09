# dash-cricket-data-construction

Downloads and transforms batting statistics of top performing international cricketers to create the csv's used by the dash-cricket app hosted at https://burningtin-cricket.herokuapp.com/. Data is retrieved from Cricinfo.

Process:
The html of a cricinfo page showing the results of a query for the top 200 test match run scorers with a batting average >35 is loaded.
A regex match is used against this html to create a dictionary of the player names and cricinfo ids, ids_names.json
The list of cricinfo id's is iterated through, downloading each players full innings list into a dataframe. These dataframes are saved as a .pkl before any other actions are performed on them.


* Download innings list for each of these players from cricinfo. Use innings lists to create career average progression, rolling averages, average by opposition, dismissal type proportions for each player - player.py
* Create event tables - survivalFunctions.py
* Calculate confidence bands for the Kaplan-Meier estimates - create_CI.R (rjson and bpcp packages are required)
* Calculate kernel density plot values - hazardKDE.py
* Run through these steps and save all values to final csv's - main.py  
