from functools import reduce
import pandas as pd
import os

def files_to_lists(file_folder):
    '''    finds files in folder specified by directory

           return list of file_names and list of file_paths respectively

       :param: file_folder - dtype:string -  the name / file path from current working directory to directory for
       collecting filenames/filepaths

       :return: separate lists of both file_name and file_path

    '''
    # assign directory
    directory = f'compiled_data/{file_folder}'
    file_name_list = []
    file_path_list = []

    # iterate over files in
    # that directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(file_path):
            # if true: frop file name and path into list as string
            file_name_list.append(filename)
            file_path_list.append(file_path) 
    return file_name_list, file_path_list


directory = os.getcwd()
directory_file_list = os.listdir(f'{directory}/compiled_data/')

# this will remove all names from the list than cannot be made into a number
# while also converting all strings into integers
for i,name in enumerate(directory_file_list):
    try:
        directory_file_list[i] = int(name)
    except ValueError:
        directory_file_list.remove(name)
        continue

# create a dictionary to hold all file names and paths separated by the year
master_file_dict = {}
master_path_dict = {}
# start_year, end_year = take_input()
for year in directory_file_list:
    file_name_list, file_path_list = files_to_lists(f'{year}/')
    master_file_dict[f'{year}'] = file_name_list
    master_path_dict[f'{year}'] = file_path_list
    
    
# create a dictionary of all dataframes with keys for year then individual dataframes from the years.
master_dataframe_dictionary = {}
for year in list(range(2014,2023)):
    master_dataframe_dictionary[f'{year}'] = {} 
    for i,file_path in enumerate(master_path_dict[f'{year}']):
        dataframe = pd.read_csv(file_path)
        string_slice = master_path_dict[f'{year}'][i][24:-4]
        master_dataframe_dictionary[f'{year}'][f'{string_slice}'] = dataframe  
        
# set lists for the primary and secondat keys for navigating the master_dictionary
primary_keys = list(master_dataframe_dictionary.keys())
secondary_keys = list(master_dataframe_dictionary['2014'].keys())

# create a dictionary to hold the cleaned data.
# both RAW and formatted copies
clean_dataframe_dictionary = {}

def master_cogs_cleaner():
    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.
    
    : ---------------------------------- METADATA ---------------------------------- :

    
    year - year of sales
    
    sum_cash_over_under - sum of all cash levels at end of night
    
    avg_Bread_COGS - average cost of goods sold as decimal 
    
    avg_Food_COGS - average cost of goods sold as decimal 
    
    avg_Sides_COGS - average cost of goods sold as decimal 
    
    avg_Paper_COGS - average cost of goods sold as decimal 
    
    avg_Produce_COGS - average cost of goods sold as decimal 
    
    avg_Beverage_COGS - average cost of goods sold as decimal 
    
    avg_Catering_COGS - average cost of goods sold as decimal 
    
    Sub_Total_COGS - average cost of goods sold as decimal 
    
    Discounted_Total_COGS - average cost of goods sold as decimal 
    
    : ---------------------------------- METADATA ---------------------------------- :
    
    
    '''
    # define list to hold dfs from each year
    cogs_list = []
    
    # define list to act as iteration counter
    years_list = list(master_dataframe_dictionary.keys())
    
    
    current_dataframe = 'master_cogs'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}
    

    # for each year, move through the data making aggregations
    # for into new dataframe
    # format
    # return clean df
    for i,year in enumerate(years_list):
        df = master_dataframe_dictionary[f'{year}']['cogs']  
        year = df['week_ending_date'][0][6:]
        cash_total = df['Cash Over Under'].sum()
        avg_Bread_4311 = df['Bread 4311'].mean()
        avg_Food_4312 = df['Food 4312'].mean()
        avg_Sides_4313 = df['Sides 4313'].mean()
        avg_Paper_4314 = df['Paper 4314'].mean()
        avg_Produce_4315 = df['Produce 4315'].mean()
        avg_Beverage_4316 = df['Beverage 4316'].mean()
        avg_Catering_4320 = df['Catering 4320'].mean()
        Sub_Total_COGS = df['Sub Total COGS'].mean()
        Discounted_Total_COGS = df['Discounted Total COGS'].mean()

        agg_values = {
            'year':year,
            'sum_cash_over_under':cash_total,
            'avg_Bread_COGS':avg_Bread_4311,
            'avg_Food_COGS':avg_Food_4312,
            'avg_Sides_COGS':avg_Sides_4313,
            'avg_Paper_COGS':avg_Paper_4314,
            'avg_Produce_COGS':avg_Produce_4315,
            'avg_Beverage_COGS':avg_Beverage_4316,
            'avg_Catering_COGS':avg_Catering_4320,
            'sub_total_COGS':Sub_Total_COGS,
            'discounted_total_COGS':Discounted_Total_COGS,
        }

        dataframe = pd.DataFrame(agg_values, index=range(0,1))

        cogs_list.append(dataframe)


        master_cogs = pd.concat(cogs_list)
        master_cogs = master_cogs.reset_index(drop=True)
        
        
        cols = master_cogs.columns.to_list()
        
        total_list = []
        
        total_over_under = master_cogs['sum_cash_over_under'].sum()
        
        for col in cols[2:]:
            column_sum = master_cogs[f'{col}'].mean()
            total_list.append(column_sum)
        
        total_list.insert(0,'TOTAL')
        total_list.insert(1,total_over_under)
        
        master_cogs.loc[len(master_cogs.index)] = total_list
        
        
        # drop outlier columns
        for col in cols:
            if master_cogs[f'{col}'][(len(master_cogs.index)-1)] == 0:
                master_cogs = master_cogs.drop(columns=[col])
                
        master_cogs_formatted = master_cogs.copy()
        
        master_cogs_formatted[f'sum_cash_over_under'] = master_cogs[f'sum_cash_over_under'].map('${:,.2f}'.format)
        for col in cols[2:]:
            master_cogs_formatted[f'{col}'] = (master_cogs[f'{col}']*100).map('{:,.2f}%'.format)
            
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_cogs
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_cogs_formatted

def master_daily_sales():
    
    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.

    
    '''

    dataframe_list = []
    years_list = list(master_dataframe_dictionary.keys())
    
    current_dataframe = 'master_daily_sales'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}


    # for each year, move through the data making aggregations
    # for into new dataframe
    # format
    # return clean df 
    for year in years_list:


        df = master_dataframe_dictionary[f'{year}']['daily_sales']

        year = df['week_ending_date'][0][6:]
        transaction_count = df['No. Of Sales'].sum()
        avg_transactions = (transaction_count / (df['No. Of Sales'].count()))
        sum_sales = df['(A) Total Dollar Sales'].sum()
        avg_dollars_per_transaction = sum_sales / transaction_count
        sum_net_less_over_rings = df['(B) Net Less Over rings'].sum()
        sum_less_net_promo = df['(C) Less Net Promo'].sum()
        sum_net_less_employee_freebies = df['(D) Net Less Employee Freebies'].sum()
        sum_royalty_sales = df['(E) Royalty Sales'].sum()



        agg_values = {
            'year' : year,
            'transaction_count': transaction_count,
            'avg_dollars_per_transaction':avg_dollars_per_transaction,
            'total_dollar_sales': sum_sales,
            'total_net_less_over_rings': sum_net_less_over_rings,
            'total_less_net_promo': sum_less_net_promo,
            'total_net_less_employee_freebies': sum_net_less_employee_freebies,
            'total_royalty_sales': sum_royalty_sales,
        }

        dataframe = pd.DataFrame(agg_values, index=range(0,1))

        dataframe_list.append(dataframe)

    master_daily_sales = pd.concat(dataframe_list)
    master_daily_sales = master_daily_sales.reset_index(drop=True)

    # now that we have all years we can form an overall total for the years

    cols = master_daily_sales.columns.to_list()
    total_list = []
    for col in cols[3:]:
        column_sum = master_daily_sales[f'{col}'].sum()
        total_list.append(column_sum)

    total_transaction = master_daily_sales[f'transaction_count'].sum()
    overall_average_dollars_per_transaction = master_daily_sales[f'avg_dollars_per_transaction'].mean()

    total_list.insert(0,'TOTAL')
    total_list.insert(1,total_transaction)
    total_list.insert(2,overall_average_dollars_per_transaction)

    # insertion of total row - will take place at the end of the DF no matter the length
    master_daily_sales.loc[len(master_daily_sales.index)] = total_list

    # for each col in dataframe, except 'year' & transaction_count format for cash values
    cols = master_daily_sales.columns.to_list()

    # drop outlier columns
    for col in cols:
        if master_daily_sales[f'{col}'][(len(master_daily_sales.index)-1)] == 0:
            master_daily_sales = master_daily_sales.drop(columns=[col])
            
    # for each col in dataframe, except 'year' format for cash values
    cols = master_daily_sales.columns.to_list()
    master_daily_sales_formatted = master_daily_sales.copy()
    master_daily_sales_formatted[f'transaction_count'] = master_daily_sales[f'transaction_count'].map('{:,}'.format)
    
    for col in cols[2:]:
        master_daily_sales_formatted[f'{col}'] = master_daily_sales[f'{col}'].map('${:,.2f}'.format)
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_daily_sales
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_daily_sales_formatted

def master_fees_payments():
    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.

    
    '''
    
# set list to hold single line dataframes
    dataframe_list = []
    
    # define list for iteration
    years_list = list(master_dataframe_dictionary.keys())
    
    
    current_dataframe = 'master_fees_payments'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}

    
    # for each dataframe in main_datafrane_dictionary
    # aggregate totals
    # combine into single DF
    # make overall Totals
    # return final, clean DF
    
    for year in years_list:

        df = master_dataframe_dictionary[f'{year}']['fees_and_payments']

        year = df['week_ending_date'][0][6:]

        sum_royalty = df['amount'].loc[df['payment_type'] == 'Royalty'].sum()
        sum_media = df['amount'].loc[df['payment_type'] == 'Media'].sum()
        sum_advertising = df['amount'].loc[df['payment_type'] == 'Advertising'].sum()
        total_fees_payments = sum_royalty + sum_media + sum_advertising



        agg_values = {
            'year': year,
            'advertising_payments' : sum_advertising,
            'media_payments' : sum_media,
            'royalty_payments' : sum_royalty,
            'total_fees_payments':total_fees_payments,
        }


        dataframe = pd.DataFrame(agg_values, index=range(0,1))


        dataframe_list.append(dataframe)
    # create master dataframe, reset index as new df will show 0 for all index entries
    master_fees_payments = pd.concat(dataframe_list)
    master_fees_payments = master_fees_payments.reset_index(drop=True)
    
    # now that we have all years we can form an overall total for the years
    
    cols = master_fees_payments.columns.to_list()
    total_list = []
    
    for col in cols[1:]:
        column_sum = master_fees_payments[f'{col}'].sum()
        total_list.append(column_sum)
        
    total_list.insert(0,'TOTAL')


    # insertion of total row - will take place at the end of the DF no matter the length
    master_fees_payments.loc[len(master_fees_payments.index)] = total_list


    # drop outlier columns
    for col in cols:
        if master_fees_payments[f'{col}'][(len(master_fees_payments.index)-1)] == 0:
            master_fees_payments = master_fees_payments.drop(columns=[col])

    # for each col in dataframe, except 'year' format for cash values
    cols = master_fees_payments.columns.to_list()
    master_fees_payments_formatted = master_fees_payments.copy()
    for col in cols[1:]:
        master_fees_payments_formatted[f'{col}'] = master_fees_payments[f'{col}'].map('${:,.2f}'.format)
        
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_fees_payments
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_fees_payments_formatted

def master_promo_freebies():
    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.

    
    '''

    dataframe_list = []

    # define list for iteration
    years_list = list(master_dataframe_dictionary.keys())
    
    current_dataframe = 'master_promo_freebies'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}


    # for each dataframe in main_datafrane_dictionary
    # aggregate totals
    # combine into single DF
    # make overall Totals
    # return final, clean DF

    for year in years_list:

        df = master_dataframe_dictionary[f'{year}']['freebies_and_promos']

        year = df['week_ending_date'][0][6:]

        total_employee_freebies = df['Employee Freebies'].sum()
        total_promo = df['Promo'].sum()
        total_waste = df['Waste'].sum()
        total_freebies = df['Total Freebies'].sum()


        agg_values = {
            'year':year,
            'total_employee_freebies': total_employee_freebies,
            'total_promo': total_promo,
            'total_waste': total_waste,
            'total_freebies': total_freebies,
        }

        dataframe = pd.DataFrame(agg_values,index=range(0,1))
        dataframe_list.append(dataframe)

    master_promo_freebies = pd.concat(dataframe_list)
    master_promo_freebies = master_promo_freebies.reset_index(drop=True)

    # now that we have all years we can form an overall total for the years

    cols = master_promo_freebies.columns.to_list()
    total_list = []

    for col in cols[1:]:
        column_sum = master_promo_freebies[f'{col}'].sum()
        total_list.append(column_sum)

    total_list.insert(0,'TOTAL')


    # insertion of total row - will take place at the end of the DF no matter the length
    master_promo_freebies.loc[len(master_promo_freebies.index)] = total_list

    # drop outlier columns
    for col in cols:
        if master_promo_freebies[f'{col}'][(len(master_promo_freebies.index)-1)] == 0:
            master_promo_freebies = master_promo_freebies.drop(columns=[col])

    # for each col in dataframe, except 'year' format for cash values
    cols = master_promo_freebies.columns.to_list()
    master_promo_freebies_formatted = master_promo_freebies.copy()
    for col in cols[1:]:
        master_promo_freebies_formatted[f'{col}'] = master_promo_freebies[f'{col}'].map('${:,.2f}'.format)
        
    
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_promo_freebies
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_promo_freebies_formatted
def master_labor():
    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.

    
    '''

    dataframe_list = []

    # define list for iteration
    years_list = list(master_dataframe_dictionary.keys())
        
    current_dataframe = 'master_labor'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}


    # for each dataframe in main_datafrane_dictionary
    # aggregate totals
    # combine into single DF
    # make overall Totals
    # return final, clean DF

    for year in years_list:

        df = master_dataframe_dictionary[f'{year}']['labor']

        year = df['week_ending_date'][0][6:]


        # aggrehate values
        manager = df['Manager'].sum()
        inshop = df['InShop'].sum()
        driver = df['Driver'].sum()
        tax = df['Tax'].sum()
        dmr = df['DMR'].sum()
        total = df['Total'].sum()
        vacation = df['Vacation'].sum()
        training_pay = df['Training Pay'].sum()
        vacation_tax = df['Vacation Tax'].sum()
        training_tax = df['Training Tax'].sum()
        total_vacation_training = df['Total Vacation/Training'].sum()
        total_labor_cost = df['Total Labor Cost'].sum()

        agg_values = {
            'year': year,
            'total_labor_manager_USD' : manager,
            'total_labor_inshop_USD' : inshop,
            'total_labor_driver_USD' : driver,
            'total_labor_tax_USD' : tax,
            'total_labor_dmr_USD' : dmr,
            'total_labor_USD' : total,
            'total_vacation_USD' : vacation,
            'total_training_pay_USD' : training_pay,
            'total_vacation_tax_USD' : vacation_tax,
            'total_training_tax_USD' : training_tax,
            'total_vacation_training_USD' : total_vacation_training,
            'total_labor_cost_USD': total_labor_cost,

            }

        dataframe = pd.DataFrame(agg_values, index = range(0,1))

        dataframe_list.append(dataframe)
        
        # assemble all years dataframe and reset the index
        master_labor = pd.concat(dataframe_list).reset_index(drop=True)
        
        
        
        # now that we have all years we can form an overall total for the years

            
        cols = master_labor.columns.to_list()
        total_list = []
        
        # for each column, calculate the sum and add to list for later insertion at bottom of dataframe
        for col in cols[1:]:
            column_sum = master_labor[f'{col}'].sum()
            total_list.append(column_sum)

        total_list.insert(0,'TOTAL')


        # insertion of total row - will take place at the end of the DF no matter the length
        master_labor.loc[len(master_labor.index)] = total_list

        # drop outlier columns
        for col in cols:
            if master_labor[f'{col}'][(len(master_labor.index)-1)] == 0:
                master_labor = master_labor.drop(columns=[col])
        
        # for each col in dataframe, except 'year' format for cash values
        cols = master_labor.columns.to_list()
        master_labor_formatted = master_labor.copy()
        for col in cols[1:]:
            master_labor_formatted[f'{col}'] = master_labor[f'{col}'].map('${:,.2f}'.format)
            
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_labor
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_labor_formatted
def master_produce():

    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.

    
    '''
    dataframe_list = []

    # define list for iteration
    years_list = list(master_dataframe_dictionary.keys())
    
    current_dataframe = 'master_produce'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}


    # for each dataframe in main_datafrane_dictionary
    # aggregate totals
    # combine into single DF
    # make overall Totals
    # return final, clean DF

    for year in years_list:

        df = master_dataframe_dictionary[f'{year}']['master_produce']

        year = df['week_ending_date'][0][6:]

        
        # aggrehate values
        produce_4315 = df['Produce 4315'].sum()
        discounts = df['Discounts'].sum()
        delivery_charges = df['Delivery Charges'].sum()
        invoice_totals = df['Invoice Totals'].sum()

        agg_values = {
            'year':year,
            'total_produce_4315':produce_4315,
            'total_produce_discounts':discounts,
            'total_produce_delivery_charges':delivery_charges,
            'produce_invoice_totals':invoice_totals,
                    }

        dataframe = pd.DataFrame(agg_values, index = range(0,1))

        dataframe_list.append(dataframe)
        
        # assemble all years dataframe and reset the index
        master_produce = pd.concat(dataframe_list).reset_index(drop=True)
        
        
        
        # now that we have all years we can form an overall total for the years

            
        cols = master_produce.columns.to_list()
        total_list = []
        
        # for each column, calculate the sum and add to list for later insertion at bottom of dataframe
        for col in cols[1:]:
            column_sum = master_produce[f'{col}'].sum()
            total_list.append(column_sum)

        total_list.insert(0,'TOTAL')


        # insertion of total row - will take place at the end of the DF no matter the length
        master_produce.loc[len(master_produce.index)] = total_list

        # drop outlier columns
        for col in cols:
            if master_produce[f'{col}'][(len(master_produce.index)-1)] == 0:
                master_produce = master_produce.drop(columns=[col])
        
        # for each col in dataframe, except 'year' format for cash values
        cols = master_produce.columns.to_list()
        master_produce_formatted = master_produce.copy()
        for col in cols[1:]:
            master_produce_formatted[f'{col}'] = master_produce[f'{col}'].map('${:,.2f}'.format)
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_produce
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_produce_formatted
def master_food():
    '''
    This function creates a list to hold dataframes made from each year_summary created using the worksheets_to_df()
    function then performs aggregations to tabulate totals and averages as needed across all years of sales before
    compiling into one dataframe.

    
    '''

    dataframe_list = []

    # define list for iteration
    years_list = list(master_dataframe_dictionary.keys())
    
    current_dataframe = 'master_food'
    clean_dataframe_dictionary[f'{current_dataframe}'] = {}
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = {}

    # for each dataframe in main_datafrane_dictionary
    # aggregate totals
    # combine into single DF
    # make overall Totals
    # return final, clean DF

    for year in years_list:

        df = master_dataframe_dictionary[f'{year}']['master_food']

        year = df['week_ending_date'][0][6:]

        
        # aggrehate values
        bread_4311 = df['Bread 4311'].sum()
        food_4312 = df['Food 4312'].sum()
        sides_4313 = df['Sides 4313'].sum()
        paper_4314 = df['Paper 4314'].sum()
        beverage_4316 = df['Beverage 4316'].sum()
        catering_4320 = df['Catering 4320'].sum()
        operating_supplies_5220 = df['Operating Supplies 5220'].sum()
        fuel_surcharge = df['Fuel Surcharge'].sum()
        discounts = df['Discounts'].sum()
        delivery_charges = df['Delivery Charges'].sum()
        tax = df['Tax'].sum()
        invoice_totals = df['Invoice Totals'].sum()

        agg_values = {
            'year':year,
            'total_bread_4311':bread_4311,
            'total_food_4312':food_4312,
            'total_sides_4313':sides_4313,
            'total_paper_4314':paper_4314,
            'total_beverage_4316':beverage_4316,
            'total_catering_4320':catering_4320,
            'total_operating_supplies_5220':operating_supplies_5220,
            'total_food_fuel_surcharge':fuel_surcharge,
            'total_food_discounts':discounts,
            'total_food_delivery_charges':delivery_charges,
            'total_food_tax':tax,
            'food_invoice_totals':invoice_totals,
#             'total_aprons_floor_mats_5285':aprons_floor_mats_5285,
                    }

        dataframe = pd.DataFrame(agg_values, index = range(0,1))

        dataframe_list.append(dataframe)
        
        # assemble all years dataframe and reset the index
        master_food = pd.concat(dataframe_list).reset_index(drop=True)
        
        
        
        # now that we have all years we can form an overall total for the years

            
        cols = master_food.columns.to_list()
        total_list = []
        
        # for each column, calculate the sum and add to list for later insertion at bottom of dataframe
        for col in cols[1:]:
            column_sum = master_food[f'{col}'].sum()
            total_list.append(column_sum)

        total_list.insert(0,'TOTAL')


        # insertion of total row - will take place at the end of the DF no matter the length
        master_food.loc[len(master_food.index)] = total_list

        # drop outlier columns
        for col in cols:
            if master_food[f'{col}'][(len(master_food.index)-1)] == 0:
                master_food = master_food.drop(columns=[col])
        
        # for each col in dataframe, except 'year' format for cash values
        cols = master_food.columns.to_list()
        master_food_formatted = master_food.copy()
        for col in cols[1:]:
            master_food_formatted[f'{col}'] = master_food[f'{col}'].map('${:,.2f}'.format)
            
            
    clean_dataframe_dictionary[f'{current_dataframe}'] = master_food
    clean_dataframe_dictionary[f'{current_dataframe}_formatted'] = master_food_formatted


master_cogs_cleaner()
master_daily_sales()
master_fees_payments()
master_promo_freebies()
master_labor()
master_food()
master_produce()


# set list of keys for use with naming files
clean_df_list = list(clean_dataframe_dictionary.keys())

# set home location for restting CWD after saving files
home = os.getcwd()

# use variables for naming directories in the event that you want to change them
compiled_dir = 'compiled_data'
all_years_dir = 'all_years_sales_data'
formatted_dir = 'formatted_data_sheets'

# try to make directory if exists, navigate into directory
try:
    os.mkdir(f'{home}/{compiled_dir}/{all_years_dir}')
    os.mkdir(f'{home}/{compiled_dir}/{all_years_dir}/{formatted_dir}')
    os.chdir(f'{home}/{compiled_dir}/{all_years_dir}')
    
except FileExistsError:
    print(f'Directory "{all_years_dir}" Already Exists, Moving into "{all_years_dir}"... ')
    print(f'')
    os.chdir(f'{home}/{compiled_dir}/{all_years_dir}')

# for each key in the dictionary save the dataframe associated with that key, using the key as the name of the file.


formatted_df_list = []
raw_df_list =[]
for key in clean_df_list:
    if key[-9:] == 'formatted':
        formatted_df_list.append(clean_dataframe_dictionary[f'{key}'])
    else:
        raw_df_list.append(clean_dataframe_dictionary[f'{key}'])
        
clean_dataframe_dictionary['all_years_data_formatted'] = reduce(lambda l, r: pd.merge(l,r, on='year', how='outer'),formatted_df_list)
clean_dataframe_dictionary['all_years_data'] = reduce(lambda l, r: pd.merge(l,r, on='year', how='outer'),raw_df_list)


clean_df_list = list(clean_dataframe_dictionary.keys())

for key in clean_df_list:
    if key[-9:] == 'formatted':
        os.chdir(f'{home}/{compiled_dir}/{all_years_dir}/{formatted_dir}')
        dataframe = clean_dataframe_dictionary[f'{key}'].to_csv(f'{key}.csv', index=False)
        os.chdir('../')
        print(f"Saving {key}.csv in {formatted_dir}")
        print()
    else:
        dataframe = clean_dataframe_dictionary[f'{key}'].to_csv(f'{key}.csv', index=False)
        print(f"Saving {key}.csv in {all_years_dir}")
        print()
    
# navigate back home.
os.chdir(home)
