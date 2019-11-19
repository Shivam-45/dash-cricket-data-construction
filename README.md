# dash-cricket-data-construction

 Creates the data tables used in the dash-cricket app
 
Process and relevant files:
* Extract the cricinfo id of each player we want data on -id_finder.py
* Download innings list for each of these players from cricinfo. Use innings lists to create career average progression, rolling averages, average by opposition, dismissal type proportions for each player - player.py
* Create event tables - survivalFunctions.py
* Calculate confidence bands for the Kaplan-Meier estimates - create_CI.R (rjson and bpcp packages are required)
* Calculate kernel density plot values - hazardKDE.py
* Save all values to final csv's - main.py

To do: Change aspects of the process that are left over from earlier versions which served different purposes e.g. remove unnecessary file creation, rename functions/files appropriately, integrate create_CI.R into process 
