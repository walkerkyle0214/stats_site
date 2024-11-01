This site was intended to read in the data in the excel spreadsheet and contextualize it to give it some purpose. I focused more on showcasing my ability to use SQLite and query the data effectively,
as apposed to focusing on frontend design given the time constraint. additionaly, there is a branch where a spray chart for individual hitters batted balls was being developed, however due to erros with plotting the points,
this did not make it into the final version. I highly recommend looking at this, as I did spend a few hours trying to convert the distance and direction to x and y coordinates using trigonomic functions, but in the end was 
unable to get it just right. The stats on the homepage can be sorted by clicking on the headers, and clicking the batters name shows their outcomes on batted balls for the given date range.

Before cloning the repository, it should be noted that the git ignores the spreadsheet file, and it will have to be placed in the data folder before running. This is to save having to download it.
To run this app, clone the main repository in your system, and run the following command in the directory:

FLASK_APP=app.py flask run 

