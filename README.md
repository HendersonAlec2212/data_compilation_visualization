# data_compilation_visualization
A series of scripts to compile and process raw data into organized CSVs for use in visualizations

# Intro

With drastic changes in the marketplace due to COVID, the owner of this business/franchise was looking for a faster, more reliable means of compiling information so that it could be saved and used in data visualization programs.

The purpose of this project was to use increase the readability of sales information collected in XLS files one week at a time.
The existing form of data concatenation for this medium-sized business is unreliable and without proper documentation for use. If there is an error in the parameters submitted for generating data visualizations then no data will return, however while the program is operating there is no way to see if what you've submitted has been received, with loading times stretching to around 25 minutes on average for one, low-dpi graph.

To summarize, the initial software is unreliable.

# Data Set 
The goal of the developed scripts was to create AI for extracting information from excel worksheets and transforming them into CSVs for use with visualization software in addition to pure numerical analysis.

The data was spread across 416 files each the collection of information for one week of sales covering 8 years, totaling to 4,756 worksheets. 

Due to an agreement with the client, this data will not be available in the repository.

The final data output is a collection of CSV files for each year in respective fields extracted from the various XLS worksheets.

    Fields/Worksheets are as follows:

    - Sales Summary:
        Initially created to proved week-at-a-glance information. This first worksheet consists of a collection of three fields: 
        COGS: The cost of goods sold reflected as a percentage of the overall earnings per week, running.
        Labor Summary: An at-a-glance summary of labor in a no-frills table.
        Promos: The amount in dollars given as promos for employee meals, sales promotions, or waste.
        This was broken into three CSVs, each covering their respective field.
    - Gross Sales:
         Another week-at-a-glance collection of information combining the following fields:
             Daily Sales: A summary of the sales per day for a 7 day period.
             Fees and Payments: A summary of all fees required for running the business.
             Inventory Summary: A rough inventory summary of in/out valuations of inventory for items sold in a 7 day period.
             Shift Sales Summary: A break down of the dollar amount made in revenue per shift AM/PM across a 7 day period.
    - Weekly Sales:
        A Table containing information covering each item sold over a 7 day period for both AM & PM shifts and the dollar amount earned per total item(s) sold.
    - Petty Cash:
        A table covering all dollar amounts paid out to staff for Reimbursement for using personal vehicle for work purposes in addition to amounts paid should an employee purchase supplies used by the business.
    - Inventory Food Summary:
        Summary of Frozen goods purchased for the week.
    - Inventory Produce Summary:
        Summary of Produce goods purchased for the week.
     - Inventory:
         Full, detailed collection of all items purchased for the upcoming week generated based on sales.
     - Labor Management Staff:
         Detailed Labor information concerning management staff and associated costs across all shifts for a 7 day period.
     - Labor In Store Staff:
        Detailed Labor information concerning In Store staff and associated costs across all shifts for a 7 day period.
    - Labor Driver Staff:
         Detailed Labor information concerning driving staff and associated costs across all shifts for a 7 day period.
     - Drivers Maintenance Reimbursement
         Detailed information concerning each driver and their performance metrics/sales during the shift.

# Method

## Data Architecture 
Since the data was collected the same manner for all years of sales, constructing functions to load and extract data was a straightforward exercise of using the OS library in python to navigate the file folders created for each year of sales.

The files were stored in file folders named after each year (2014,2015,..) A script was constructed to locate files in a supplied directory, check to see if the name of the file could be an integer then if successful, add that number to a list to filter out unwanted folders. Once the list was constructed each folder was parsed for XLS files by first verifying if the item was a .xls file, then read in as "xls" using the pandas, pd.read_excel() method.

## Extraction & Transformation
Once the sales information was assigned to a variable, meta data such as the week_ending_date and year of sales was extracted/constructed in order to have a single similar column across all dataframes, should a join of all information be desired.

In addition, this data was used to create a dictionary with primary keys pertaining to the year of sales and eventually, secondary keys associated with the compiled dataframes.

Now the XLS variable was passed to an array of functions, each constructed to convert the unique worksheet into a dataframe, then "search" the cells for locations matching supplied data values or keywords and record where in the dataframe the words exist. Once found the values were passed into an dataframe.iloc[start:end] formula that sliced the sections out from the initial dataframe before formatting columns and indexes and finally adding it to a list to be used in a pd.concat() method to create a week_to_year summary of the sales information for a particular aspect of sales information.

The dataframes constructed in this manner displayed a row of sales information for each category with columns pertaining to aspects within that category.
        e.g. the C.O.G.S. dataframe showed one years worth of costs associated with running the business instead of needing to open multiple files, each only a week's worth of information.

Once the yearly dataframe was collected, it was stored into a dictionary with a primary key for the year, and secondary key for the particular aspect of sales.

> dataframe_dict['year']['compiled_dataframe'] = compiled_dataframe

The mass of excel sheets was iterated through, loaded, information was extracted and the final dataframe dictionary was used in a function that parses the information, then saves the CSV files in branches of folders similar to the initial layout making navigation easy for existing staff.

All 4,600 worksheets were compiled, organized and saved in under three minutes.

Once the dictionary was created, a second script iterated through lists generated from the primary and secondary keys using various dataframe aggregations on only the most desired information such as Sales, Revenue, Profits, Labor, Inventory costs, Fees/Advertising/etc.

These last 8 dataframes display 8 years of sales information at a glance.

## Storage method

The function created to save the compiled CSVs works by creating a folder to house the compiled data, them mimicking the file path layout of the initial database. Creating folders for each year as needed, saving the CSV files, then navigating back the compiled_data_directory in preparation to construct another directory and repeating with next year.



## Visualizations
The summarized information was then used to create an array of charts shedding light on eight-year trends such as:
     - The fluctuations in sales over time.
    - Changes in the COGS, to allow for predictions on future costs in the coming years.
    - Variances in sales per shift, displaying which times the staffing should be more plentiful to allow for peak performance and sales potential.
    - Fluctuations in the amount of waste and promo-items generated hinted that items are not being properly recorded allotting for improper sales values, signaling a need for retraining certain procedures within management.

These are just some of the visualizations created using a script that saves the images as high-resolution PNG files for referencing in the future.

![sales_dispersion](/visualizations/2021_Sales_Dispersion_AM_PM.png)

![Average Sales](/visualizations/Average%20Sales%20per%20Shift%2C%20per%20Year.png)

![Max Sales](/visualizations/Max%20Sales%20per%20Shift%2C%20per%20Year.png)

![Full Royalty Sales](/visualizations/Royalty%20Sales%20per%20Shift%2C%20per%20Year.png)

![Stack Royal Sales Comparison](/visualizations/Royalty%20Sales%20per%20Shift%2C%20per%20Year%20-%20stacked.png)

![Sales / Day Variance](/visualizations/Variance%20percentage%20of%20Sales%20per%20Shift%2C%20per%20Year.png)


# Conclusion
The compiled data in combination with the visualizations proved quite useful to the owner. The scripts will allow them to generate information across a number of stores giving them insight on trends and allowing them the change as needed in order to maximize sales & profit potential in a shifting marketplace.



