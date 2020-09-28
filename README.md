# dash-cricket-data-construction

 This repository gathers and manipulates data from cricinfo to create the csv's used by the dash-cricket dashboard. [Hosted here](https://burningtin-cricket.herokuapp.com/). [Repository here](https://github.com/burningtin/dash-cricket).
 
Code from earlier projects was repurposed and improved to create a streamlined process that will provide updated data when main.py is run.

## Process:

* HTML extracted from the appropriately filtered cricinfo leaderboard page is parsed to provide a dictionary of cricinfo_id:player_name pairs, which is saved as a json.
* Iterate through the cricinfo_id's in this dictionary to download the innings list table available on each players cricinfo page as a dataframe, these are stored as pkl's as each is downloaded. 

These dataframes are used to do the following for each player and for the 200 players in aggregate:

* Rolling averages, average by opposition, and style of dismissal proportions are calcualated.
* Dismissals are viewed as observed events for the purpose of performing survival analysis. An event table is made showing how many innings were ongoing and how many dismissals or censored events (not outs) occurred at each score.
* Survival probabilities for use in a Kaplan-Meier plot are calculated using this table.
* Confidence intervals for these survival probabilities are calculated using bpcpy.py\* 

* These results are combined into dataframes which are saved as csv's, ready for use by the dashboard.


bpcp.py is made specifically for use with this project as a narrow implementation of the beta product confidence procedure for calculating confidence intervals described [here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3769999/). Earlier versions of this repository used the R package [bpcp](https://cran.r-project.org/web/packages/bpcp/bpcp.pdf) to calculate these confience intervals. Results on this dataset from bpcp.py were confirmed against the results I obtained when using the R package to calculate results on the same dataset.
