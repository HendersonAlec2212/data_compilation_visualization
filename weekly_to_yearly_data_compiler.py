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
    directory = f'{file_folder}/'
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

def sales_summary_cleaner(xls,date):
    '''
    Sales Summary is a combination of three dataframes, so we will
    
    Take the Sales Summary WKS and break it into parts - Labor, Cogs, and Freebies.
    
    Then transform the pieces into individual DFs, and create a master DF of all information.
    
    Then return all 4 dfs in dictionary
    
    :param: xls --> xls = pd.ExcelFile(file_path) in worksheets_to_df()

    :param: date --> date = meta_data['Unnamed: 4'][0] # week ending date in worksheets_to_df()
    
    '''
    
    sales_summary = pd.read_excel(xls, 'Sales Summary')
    
    # set up cols for parsing
    
    sales_and_cogs_query_cols = sales_summary[f'{sales_summary.columns[0]}'].to_list()
    labor_cost_summary_cols = sales_summary[f'{sales_summary.columns[5]}'].to_list()

    # create dictionary to hold the cleaned DFs
    sales_summary_dfs = {}
    # if a string from the cols matches target, set i for start and end points
    for i in sales_summary.index.to_list():
        # --------------- Freebies --------------- #
        if sales_and_cogs_query_cols[i] == 'Manager Freebies':
            freebies_promos_start = i

        elif sales_and_cogs_query_cols[i] == 'Total Freebies':
            freebies_promos_end = i+1

        # --------------- COGS --------------- #
        if sales_and_cogs_query_cols[i] == 'COGS Summary':
            cogs_start = i+1

        elif sales_and_cogs_query_cols[i] == 'Total Sales':
            cogs_end = i

        # --------------- Labor Cost Summary --------------- #
        if labor_cost_summary_cols[i] == 'Labor Cost Summary':
            labor_summary_start = i+1

        elif labor_cost_summary_cols[i] == 'Total Labor Cost':
            labor_summary_end = i+1

        else:
            continue
    # turn the start and end points into dfs using iloc to slice
    freebies_promos = sales_summary.iloc[freebies_promos_start:freebies_promos_end]
    cogs = sales_summary.iloc[cogs_start:cogs_end]
    labor_summary = sales_summary.iloc[labor_summary_start:labor_summary_end]


        # --------------------------------------------- Freebies --------------------------------------------- #


    # keep only first two columns
    freebies_promos = freebies_promos[['Summary Report (V2)','Unnamed: 1']]

    freebies_promos = freebies_promos.T

    # reset index
    freebies_promos = freebies_promos.reset_index(drop=True)
    # rename column
    freebies_promos.columns=freebies_promos.iloc[0]
    # drop col used for labels
    freebies_promos = freebies_promos.drop(0)
    # insert week ending date
    freebies_promos.insert(0,'week_ending_date',date)
    # reset index
    freebies_promos = freebies_promos.reset_index(drop=True)

        # --------------------------------------------- cogs --------------------------------------------- #

    # set df to these cols from parent DF
    cogs = cogs[['Summary Report (V2)','Unnamed: 1']]
    # remove NaN
    cogs = cogs.dropna(how='all', axis=0).reset_index(drop=True)
    # transpose df
    cogs = cogs.T
    # set column labels
    cogs.columns = cogs.iloc[0]
    # remove name
    cogs.columns.name = None
    # add week ending date
    cogs.insert(0,'week_ending_date',date)
    # reset index and drop col name row
    cogs = cogs.reset_index(drop=True).drop(0).reset_index(drop=True)


        # --------------------------------------------- labor summary --------------------------------------------- #

    # Take the df apart and slap it together such that its formatted as desired

    # slice the bits wanted, set the cols, 

    labor_summary_usd = labor_summary[['Unnamed: 5','Unnamed: 7']].T.reset_index(drop=True)
    labor_summary_usd.columns = labor_summary_usd.iloc[0]
#     labor_summary_prcnt = labor_summary[['Unnamed: 5','Unnamed: 6']].T.reset_index(drop=True)
#     labor_summary_prcnt.columns = labor_summary_prcnt.iloc[0]

    # merge with suffixes to identify cols
    labor_summary = labor_summary_usd #.join(labor_summary_prcnt, how='outer', lsuffix='_usd', rsuffix='_prcnt_as_dec')
    #remove label row
    labor_summary = labor_summary.drop(0)
    # add week ending date
    labor_summary.insert(0,'week_ending_date',date)


        # --------------------------------------------- full summary --------------------------------------------- #
    # merge all dfs to have master df
    cogs_and_labor = cogs.merge(labor_summary, how='outer')
    cogs_labor_freebies = cogs_and_labor.merge(freebies_promos, how='outer')
    full_summary = cogs_labor_freebies.dropna(how='all', axis=1)


    sales_summary_dfs['freebies_promos'] = freebies_promos
    sales_summary_dfs['cogs'] = cogs
    sales_summary_dfs['labor_summary'] = labor_summary
    sales_summary_dfs['full_sales_summary'] = full_summary

    
    
    return sales_summary_dfs

def gross_sales_cleaner(xls,date):
    '''
        :param: xls --> "xls = pd.ExcelFile(file_path)" in worksheets_to_df()

        :param: date --> "date = meta_data['Unnamed: 4'][0] # week ending date" in worksheets_to_df()
    '''
    
    gross_sales = pd.read_excel(xls, 'Gross Sales')
    
    try:
        
        strings= gross_sales['Statement of Gross Sales (V2)'].to_list()

        gross_sales_dfs = {}

        for i,string in enumerate(strings):
            '''
            The gross_sales is a combination of four dataframes in one XLS sheet.

            The goal of this section of script is to take the four DFs, parse the starting and
            stopping points of the information, then cut out and format the DFs
            so that they can be combined with future DFs from the following weeks.



            '''

            #--------------------------------- daily_sales    --------------------------------- #
            if string == 'Day':
                d_sales_start = i+1

            elif string == 'Tuesday':
                d_sales_end = i+1

            #--------------------------------- fees_and_payments    --------------------------------- #
            elif string == 'Fees and Payments':
                fees_and_payments_start = i

            elif string == 'Media - at 3% of Royalty Sales':
                fees_and_payments_end = i+1

            #--------------------------------- inventory_summary    --------------------------------- #
            elif string == 'Bread 4311':
                inventory_summary_start = i

            elif string == 'Discounted COGS':
                inventory_summary_end = i+1

            #--------------------------------- shift_sales_summary    --------------------------------- #
            elif string == 'Shift - 1 Wed AM':
                shift_sales_summary_start = i

            elif string == 'Royalty Sales':
                shift_sales_summary_end = i+1

            else:
                continue

        # cut out the DFs from the messy XLS
        daily_sales = gross_sales.iloc[d_sales_start:d_sales_end]
        fees_and_payments = gross_sales.iloc[fees_and_payments_start:fees_and_payments_end]
        inventory_summary = gross_sales.iloc[inventory_summary_start:inventory_summary_end]
        shift_sales_summary = gross_sales.iloc[shift_sales_summary_start:shift_sales_summary_end]

    # ---------------------------- Daily Sales ---------------------------- #
        # name columns
        daily_sales.columns = ['Day',
         'Date',
         'No. Of Sales',
         '(A) Total Dollar Sales',
         '(B) Net Less Over rings',
         '(C) Less Net Promo',
         '(D) Net Less Employee Freebies',
         '(E) Royalty Sales']
        # remove name "4" for cleaner look
        daily_sales.columns.name = None


        daily_sales.insert(0,'week_ending_date',date)
        daily_sales = daily_sales.reset_index(drop=True)


    # ---------------------------- Fees and Payments ---------------------------- #

        #remove NaN in rows and columns
        fees_and_payments = fees_and_payments.dropna(how='all', axis=0).dropna(how='all', axis=1)

        # rest index to allow for droppping of first row in case of formatting changes later on
        fees_and_payments = fees_and_payments.reset_index(drop=True)
        fees_and_payments = fees_and_payments.drop(0).reset_index(drop=True)

        # set up lists to hold values for inserting in DF
        payment_type = []
        prcnt_of_royalty_sales = []

        # for each line in DF, extract values and push to list

        ### I want to have separate columns for the type of payment, and the percent paid
        ### in event of changes later I want to able to record / manipulate them as desired without editing at later stage

        for i in fees_and_payments.index.to_list():
            payment_type.append(fees_and_payments['Statement of Gross Sales (V2)'][i].split(' ')[0])
            prcnt_of_royalty_sales.append(fees_and_payments['Statement of Gross Sales (V2)'][i].split(' ')[3][:-1])

        # insert new columns into previous DF
        fees_and_payments.insert(0,'week_ending_date',date)
        fees_and_payments.insert(1,'payment_type',payment_type)
        fees_and_payments.insert(2,'prcnt_of_royalty_sales',prcnt_of_royalty_sales)

        # rename cols
        fees_and_payments = fees_and_payments.rename(columns={'Unnamed: 3':'fee_or_payment','Unnamed: 4':'amount'})

        # srop column used to acqurie info as it is not needed anymore
        fees_and_payments = fees_and_payments.drop(columns=['Statement of Gross Sales (V2)'])

    # ---------------------------- Inventory Summary ---------------------------- #
        # remove and fill NaN
        inventory_summary = inventory_summary.dropna(how='all', axis=1).dropna(how='all', axis=0).fillna(0)

        # rename the columns
        inventory_summary = inventory_summary.rename(columns={
                                                            'Statement of Gross Sales (V2)':'Category',
                                                            'Unnamed: 1':'Beginning Inventory USD',
                                                            'Unnamed: 2':'Purchases USD',
                                                            'Unnamed: 3':'Ending Inventory USD',
                                                            'Unnamed: 4':'COGS Prcnt as Decimal',})
        # insert the week_ending_date
        inventory_summary.insert(0,'week_ending_date',date)

    # ---------------------------- Shift Sales Summary ---------------------------- #


        # remove NaN values
        shift_sales_summary = shift_sales_summary.dropna(how='all', axis=1).dropna(how='all', axis=0)

        # transpose the dataframe to allow shifts to be the columns
        shift_sales_summary = shift_sales_summary.T

        # mass rename columns
        shift_sales_summary.columns = shift_sales_summary.iloc[0]

        # reset index and remove wor used for column names
        shift_sales_summary = shift_sales_summary.reset_index(drop=True).drop(0)

        # insert date
        shift_sales_summary.insert(0,'week_ending_date',date)

        # remove column.name for prettify purposes
        shift_sales_summary.columns.name = None

    # ---------------------------- set up return dictionary ---------------------------- #
        gross_sales_dfs['daily_sales'] = daily_sales
        gross_sales_dfs['fees_and_payments'] = fees_and_payments
        gross_sales_dfs['inventory_summary'] = inventory_summary
        gross_sales_dfs['shift_sales_summary'] = shift_sales_summary

        return gross_sales_dfs
    
    except KeyError:
        return

def petty_cash_cleaner(xls, date):
    '''
        :param: xls --> "xls = pd.ExcelFile(file_path)" in worksheets_to_df()

        :param: date --> "date = meta_data['Unnamed: 4'][0] # week ending date" in worksheets_to_df()
    '''

    # load in the snippet from XLS
    petty_cash = pd.read_excel(xls, 'Petty Cash', skiprows=(7))
    # define a starting point for duplicating date across cells
    date_cell = 2
    for i in range(0,8):
        try :
            petty_cash.iloc[1,date_cell+1] = petty_cash.iloc[1,date_cell]
            date_cell+=2
        except IndexError:
            print()
            continue
    # fill NA
    petty_cash = petty_cash.fillna(0)

    # set new column names for reformatting
    cols = [
        'Account Name', 'Account Number', 'Wed - 1', 'Wed - 2', 'Thu - 3', 'Thu - 4', 'Fri - 5', 'Fri - 6', 'Sat - 7', 'Sat - 8', 'Sun - 9', 'Sun - 10', 'Mon - 11', 'Mon - 12', 'Tue - 13', 'Tue - 14', 'Account.1', 'Totals',
    ]

    # Set names of all columns
    petty_cash.columns = cols

    # define and inset new columns to reduce redundant info
    newcol = petty_cash['Account Name'].astype(str) + ' - ' + petty_cash['Account Number'].astype(str)
    petty_cash.insert(0, "Account", newcol)

    # drop un wanted columns and rows
    petty_cash = petty_cash.drop(columns=['Account.1', 'Account Name', 'Account Number'])
    petty_cash = petty_cash.drop([0])

    petty_cash.insert(0,'week_ending_date',date)
    return petty_cash

def food_cleaner(xls,date):
    '''
        :param: xls --> "xls = pd.ExcelFile(file_path)" in worksheets_to_df()

        :param: date --> "date = meta_data['Unnamed: 4'][0] # week ending date" in worksheets_to_df()
    '''
    # load in the snippet from XLS
    master_food = pd.read_excel(xls, 'Master Voucher Food', skiprows=(6))
    # remove all NaN
    master_food = master_food.fillna(0)

    # transpose to make columns the item being purchased
    master_food = master_food.T

    # set columns names to transposed DF row values
    master_food.columns = master_food.iloc[0]

    # remove name of columns resulting from previous transformation
    master_food.columns.name = None

    # drop the row used to make column names, and the row with current week totals.
    master_food = master_food.reset_index(drop=True)

    # setup index
    index_list = master_food.index.to_list()

    # conditional to drop the first and last row of the DF
    for i in index_list:
        if (master_food['Due Date'][i] == "Due Date") or (master_food['Due Date'][i] == "Account"):
            master_food = master_food.drop([i])
        else: 
            continue
    master_food.insert(0,'week_ending_date',date)
    # reset index
    master_food = master_food.reset_index(drop=True)
    return master_food

def produce_cleaner(xls,date):
    '''
        :param: xls --> "xls = pd.ExcelFile(file_path)" in worksheets_to_df()

        :param: date --> "date = meta_data['Unnamed: 4'][0] # week ending date" in worksheets_to_df()
    '''
    # load in the snippet from XLS        
    master_produce = pd.read_excel(xls, 'Master Voucher Produce', skiprows=(6))
    #  transpose to simplify the data sheet
    master_produce = master_produce.T

    # drop NaN column
    master_produce = master_produce.dropna(how='all', axis=1)

    # remove NaN 
    master_produce = master_produce.fillna(0)

    # reset the index to remove the column names
    master_produce = master_produce.reset_index(drop=True)

    #  set columns == first row (which was the 'column' header in the XLS)
    master_produce.columns = master_produce.iloc[0]

    # setup index
    index_list = master_produce.index.to_list()

    # # conditional to drop the first and last row of the DF
    for i in index_list:
        if (master_produce['Due Date'][i] == "Due Date") or (master_produce['Due Date'][i] == "Account"):
            master_produce = master_produce.drop([i])
        else: 
            continue
    master_produce.insert(0,'week_ending_date',date)
    # reset index
    master_produce = master_produce.reset_index(drop=True)
    return master_produce

def labor_manager_cleaner(xls, date):
    '''
        :param: xls --> "xls = pd.ExcelFile(file_path)" in worksheets_to_df()

        :param: date --> "date = meta_data['Unnamed: 4'][0] # week ending date" in worksheets_to_df()
    '''
    
    labor_managers = pd.read_excel(xls, 'Labor Managers')
    try:
        # set strings to use for parsing
        string_list = labor_managers['PAYROLL TIME SHEET - Manager (V2)'].to_list()
        if len(string_list) <=0:
            return None
        else:
            # if string == parsed word, record i and use to set up DF snippet
            for i, string in enumerate(string_list):
                if string =='Manager':
                    start_i = i
                elif string == 'TOTAL WEEKLY    $':
                    ending_i = i
                else:
                    continue

            # set up snippet
            labor_manager_summary = labor_managers.iloc[start_i:ending_i]
            # remove NaN Cols
            labor_manager_summary = labor_manager_summary.dropna(how='all',axis=1)
            # Split DFs then merge with suffxies to avoid having to rename each col
            labor_manager_summary_usd = labor_manager_summary[['PAYROLL TIME SHEET - Manager (V2)','Unnamed: 2']].T.reset_index(drop=True)
            labor_manager_summary_usd.columns = labor_manager_summary_usd.iloc[0]

            labor_manager_summary_prcnt = labor_manager_summary[['PAYROLL TIME SHEET - Manager (V2)','Unnamed: 3']].T.reset_index(drop=True)
            labor_manager_summary_prcnt.columns = labor_manager_summary_prcnt.iloc[0]


            # merge with suffixes to identify cols
            labor_manager_summary = labor_manager_summary_usd.join(labor_manager_summary_prcnt, how='outer', lsuffix='_usd', rsuffix='_prcnt_as_dec')
            #remove label row
            labor_manager_summary = labor_manager_summary.drop(0)
            # add week ending date
            labor_manager_summary.insert(0,'week_ending_date',date)
            return labor_manager_summary
    except KeyError:
        return None

def inventory_cleaner(xls,date):
    '''
        :param: xls --> "xls = pd.ExcelFile(file_path)" in worksheets_to_df()

        :param: date --> "date = meta_data['Unnamed: 4'][0] # week ending date" in worksheets_to_df()
    '''
        # read in the file
    inventory = pd.read_excel(xls, 'Inventory')
    # remove NaN
    inventory = inventory.fillna(0)

    # rename cols to ease concat later
    inventory = inventory.rename(columns={
        'INVENTORY (V2)':'item',
        'Unnamed: 1':'units_of_measure',
        'Unnamed: 2':'beginning_units',
        'Unnamed: 3':'unit_purchases_1',
        'Unnamed: 4':'unit_purchases_2',
        'Unnamed: 5':'unit_purchases_3',
        'Unnamed: 6':'unit_purchases_4',
        'Unnamed: 7':'total_purchased',
        'Unnamed: 8':'on_hand_counts',
        'Unnamed: 9':'ending_units',
        'Unnamed: 10':'unit_cost',
        'Unnamed: 11':'ending_value_usd',
        'Unnamed: 12':'usage_units',
    })
    # one column is a float for some reason - converting to string to keep all cols in same dtype
    inventory['unit_purchases_3'] = inventory['unit_purchases_3'].astype(int).astype(str)
    # make a list to allow for iteration even if the inventory length changes
    inventory_index_list = inventory.index.to_list()

    # create a list to hold sections of dataframe
    inventory_slice_list = []
    for i in inventory_index_list:

        # define row
        row = inventory.iloc[i]

        # set conditionals to identify when to start recording the inventory
        if row['item'] == 'Item':
            # start_i = i+3 b/c I want to remove the two redundant column rows from XLS without pd.df.drop()
            start_i = i+3
            category = inventory.iloc[i+2]['item']
    #         print(f'start_i is {start_i}')
    #         print(f'category is {category}')


        # set conditionals to identify when to stop recording the inventory
        if row['item'] == "Beginning Inventory $'s":
            ending_i = i
    #         print(f'ending_i is {ending_i}')
    #         print()

        else:
            continue

        # define the dataframe object
        inventory_slice = inventory.iloc[start_i:ending_i]

        # insert aggregated data into the dataframe
    #             inventory_slice.insert(1,'week_ending',week_ending)

        inventory_slice.insert(1,'week_ending',date)
        inventory_slice.insert(2,'category',category)

        # add piece to list for combining later
        inventory_slice_list.append(inventory_slice)

    # combine the pieces into one master inventory for the week
    inventory = pd.concat(inventory_slice_list)
    inventory = inventory.reset_index(drop=True)
    
    return inventory

def take_input():
    '''
    this function requests years of the files that are desired to be compiled.
    
    the years will work with the :worksheets_to_df(): function to produce a dictionary of dataframes that will be used
        in later functions
        
    :return:
    
    '''
    
    print('Field 1 of 2:')
    print('Typing numbers only with no spaces or punctuation, input the year you would like to START file combination')
    print()

    start_year = input('If you wish to use for just one year, enter the same value in for both fields. ')
    start_year = int(start_year)
    print()
    print()
    print('Field 2 of 2:')
    print('Typing numbers only with no spaces or punctuation, input the year you would like to STOP file combination')
    print()
    print()

    end_year = input('If you wish to use for just one year, enter the same value in for both fields. ')
    end_year = int(end_year)
    print()

    print('Inputs recieved, Starting concatination...')
    return start_year, end_year

def concat_and_format_DF(dataframe_list):
    
    '''
    Accepts list of dataframes, concats into single DF, resets the index -dropping the initial index- then returns 
    a single dataframe unless there is no data for concat. 
    
    If no data, will return None Object
    
    
    :param: dataframe_list --> list of dataframes
    
    :return_try: --> returns a concatinated dataframe
    
    :return_except: --> return None
    
    '''
    
    
    try:
        dataframe = pd.concat(dataframe_list)
    
        dataframe = dataframe.reset_index(drop=True).fillna(0)

        return dataframe
    
    except:
        print()
        print('No Data to concatinate - Returning "None" Data.')
        print('===================================================')
        return None

def worksheets_to_df(start_year,end_year):
    '''
        :param: start/end_year - integer --> value used in "file_name_list, file_path_list = files_to_lists(f'{year}/')"
            for assembly of file paths used for later functions, and as a primary key in the return_dict.
            
        :return: dictionary of all files as concatinated dataframes organized by primary key, (year)
                 and secondary key, (name of dataframe).
    
        - Takes start and end year of sales to clean and combine; the year is also the file name in original directory.

        - Converts XLS to Dataframe.

        - Snips out desired data using various methods, cleans and transfers each week as DF to list.

        - Converts each week_df into master_df per Work Sheet using pd.concat
                resulting in a DF for each Work Sheet for each year.

        - Returns dictionary of each master DF labeled by worksheet -> 
        return_dict{
                    ['year']{
                    ['worksheet_name']:df_of_worksheet,
                    ['worksheet_name']:df_of_worksheet,
                            },

    '''

    
    
    
    return_dict = {}
    
    
    
    for year in range(start_year,end_year+1):
        
        return_dict[f'{year}'] = {}
        print('- Dictionary for dataframe return successfully constructed...')
        print()

        # in the event that file names are desired to be preserved
        file_name_list, file_path_list = files_to_lists(f'{year}/')
        # make lists to hold the DFs

        # --------- sales summary --------- #
        sales_summary_list = []
        cogs_list = []
        labor_list = []
        promo_list = []

        # --------- gross sales --------- #
        daily_sales_list = []
        fees_and_payments_list = []
        inventory_summary_list = []
        shift_sales_summary_list = []

        # --------- weekly sales --------- #
        weekly_sales_list = []

        # --------- petty cash --------- #
        petty_cash_list = []

        # --------- master voucher food  --------- #

        master_food_list = []

        # --------- master voucher produce  --------- #

        master_produce_list = []

        # --------- Inventory --------- #
        inventory_list = []

        # --------- Labor Managers --------- #
        labor_managers_list = []

        print(f'- Lists for pd.concat {year} successfully made...')
        print('===========================================')
        print()



        # --------- --------- --------- --------- --------- --------- --------- --------- --------- --------- --------- #


        # for each file in the folder read these columns/rows,
        # set == these variables,
        # assign those variables to a dictionary with the Ending Week Date as a common value across all
        # turn that dictionary into a Dataframe for later saving as CSV

        for i,file_path in enumerate(file_path_list):

            try:
                worksheet = 'Meta Data'

                xls = pd.ExcelFile(file_path)
                meta_data = pd.read_excel(xls, 'Sales Summary', nrows=4)

                # ------------------------------------------------------------------- #
                date = meta_data['Unnamed: 4'][0] # week ending date
                store_num = meta_data['Unnamed: 4'][2]
                address = '2785_ridge_rd_rockwall_tx'
                print()


            except ValueError:
                print('File Type Not Supported, Skipping File...')
                print('===========================================')
                print('')
                continue           


        # ------------------------------------------------ sales summary ------------------------------------------------- #
        # ------------------------------------------------ sales summary ------------------------------------------------- #
        # ------------------------------------------------ sales summary ------------------------------------------------- #


            try:
                worksheet = 'Sales Summary'

                sales_summary_dfs = sales_summary_cleaner(xls,date)

                sales_summary_list.append(sales_summary_dfs['full_sales_summary'])
                cogs_list.append(sales_summary_dfs['cogs'])
                labor_list.append(sales_summary_dfs['labor_summary'])
                promo_list.append(sales_summary_dfs['freebies_promos'])


            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue



        # ------------------------------------------------ gross sales ------------------------------------------------- #
        # ------------------------------------------------ gross sales ------------------------------------------------- #
        # ------------------------------------------------ gross sales ------------------------------------------------- #


            try:
                worksheet = 'Gross Sales'

                gross_sales_dfs = gross_sales_cleaner(xls,date)

                daily_sales_list.append(gross_sales_dfs['daily_sales'])
                fees_and_payments_list.append(gross_sales_dfs['fees_and_payments'])
                inventory_summary_list.append(gross_sales_dfs['inventory_summary'])
                shift_sales_summary_list.append(gross_sales_dfs['shift_sales_summary'])


            except (ValueError, TypeError): # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue



        # ------------------------------------------------ Weekly Sales ------------------------------------------------- #
        # ------------------------------------------------ Weekly Sales ------------------------------------------------- #
        # ------------------------------------------------ Weekly Sales ------------------------------------------------- #

            try:
                worksheet = 'Weekly Sales'

                # load in the snippet from XLS
                weekly_sales = pd.read_excel(xls, 'Weekly Sales', skiprows=(7))

                # drop rows that hold the date and AM/PM b/c duplicated information is not wanted
                weekly_sales = weekly_sales.drop([0,1])

                # rename the columns
                weekly_sales = weekly_sales.rename(columns={
                    'Summary':'Revenue_USD',
                    '#EA':'Quantity Sold',
                })

                # fill NA
                weekly_sales = weekly_sales.fillna(0)

                #insert week ending date
                weekly_sales.insert(0,'week_ending_date',date)

                # reset the index
                weekly_sales = weekly_sales.reset_index(drop=True)

                # add finished DF to list for later concat.
                weekly_sales_list.append(weekly_sales)


            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue




        # ------------------------------------------------ Petty Cash ------------------------------------------------- #
        # ------------------------------------------------ Petty Cash ------------------------------------------------- #
        # ------------------------------------------------ Petty Cash ------------------------------------------------- #



            try:
                worksheet = 'Petty Cash'

                petty_cash = petty_cash_cleaner(xls,date)

                # add finished DF to list for later concat.
                petty_cash_list.append(petty_cash)


            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue


    # ------------------------------------------------ Master Voucher Food ------------------------------------------------- #
    # ------------------------------------------------ Master Voucher Food ------------------------------------------------- #
    # ------------------------------------------------ Master Voucher Food ------------------------------------------------- #



            try:
                worksheet = 'Master Food'

                master_food = food_cleaner(xls,date)

                # add finished DF to list for later concat.
                master_food_list.append(master_food)


            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue

    # ------------------------------------------------ Master Voucher Produce ---------------------------------------------- #
    # ------------------------------------------------ Master Voucher Produce ---------------------------------------------- #
    # ------------------------------------------------ Master Voucher Produce ---------------------------------------------- #



            try:
                worksheet = 'Master Produce'

                master_produce = produce_cleaner(xls,date)

                # add finished DF to list for later concat
                master_produce_list.append(master_produce)


            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue

    # ------------------------------------------------ Inventory ------------------------------------------------- #
    # ------------------------------------------------ Inventory ------------------------------------------------- #
    # ------------------------------------------------ Inventory ------------------------------------------------- #


            try:
                worksheet = 'Inventory'

                inventory = inventory_cleaner(xls,date)

                inventory_list.append(inventory)

            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue



    # ------------------------------------------------ Labor Managers ------------------------------------------------- #
    # ------------------------------------------------ Labor Managers ------------------------------------------------- #
    # ------------------------------------------------ Labor Managers ------------------------------------------------- #


            try:
                print()
                print(f'File # {i} of {len(file_path_list)} for year {year} compiled')
                print(f' ------ Week Ending Date {date} ------ ')
                print('=======================================================')


                worksheet = 'Labor Managers'

                labor_managers = labor_manager_cleaner(xls,date)

                labor_managers_list.append(labor_managers)

            except ValueError: # if Worksheet is not found in XLS
                print(f'Worksheet {worksheet} not in XLS file, moving on...')
                print('===========================================')
                print('')
                continue


# ============================================= DATAFRAME CREATION =============================================== #

        # define list to hold final Dataframes

        # concat all dataframes from lists of dictionaries

        # --------- sales summary --------- #
        year_end_cogs_df = concat_and_format_DF(cogs_list)
        year_end_labor_df = concat_and_format_DF(labor_list)
        year_end_promo_df = concat_and_format_DF(promo_list)
        sales_summary_df = concat_and_format_DF(sales_summary_list)

        # --------- gross sales --------- #

        daily_sales_df = concat_and_format_DF(daily_sales_list)
        fees_and_payments_df = concat_and_format_DF(fees_and_payments_list)
        inventory_summary_df = concat_and_format_DF(inventory_summary_list)
        shift_sales_summary_df = concat_and_format_DF(shift_sales_summary_list)


        # --------- weekly sales --------- #
        weekly_sales_df = concat_and_format_DF(weekly_sales_list)

        # --------- petty cash --------- #
        petty_cash_df = concat_and_format_DF(petty_cash_list)

        # --------- master voucher food --------- #
        master_food_df = concat_and_format_DF(master_food_list)

        # --------- master voucher produce --------- #
        master_produce_df = concat_and_format_DF(master_produce_list)

        # --------- inventory --------- #
        inventory_df = concat_and_format_DF(inventory_list)

        # --------- labor managers --------- #
        labor_manager_summary_df = concat_and_format_DF(labor_managers_list)









    # ================================================= FUNCTION RETURNS ================================================== #

        # add cleaned DFs to list in dictionary for later iteration in worksheets to CSV function

        # Sales Summary #
        return_dict[f'{year}']['sales_summary'] = sales_summary_df

        return_dict[f'{year}']['freebies_and_promos'] = year_end_promo_df

        return_dict[f'{year}']['cogs'] = year_end_cogs_df

        return_dict[f'{year}']['labor'] = year_end_labor_df

        # Gross Sales #
        return_dict[f'{year}']['daily_sales'] = daily_sales_df

        return_dict[f'{year}']['fees_and_payments'] = fees_and_payments_df

        return_dict[f'{year}']['inventory_summary'] = inventory_summary_df

        return_dict[f'{year}']['shift_sales_summary'] = shift_sales_summary_df


        # Weekly Sales #
        return_dict[f'{year}']['weekly_sales'] = weekly_sales_df

        # Petty Cash #
        return_dict[f'{year}']['petty_cash'] = petty_cash_df

        # Master Voucher Food #
        return_dict[f'{year}']['master_food'] = master_food_df

        # Master Voucher Produce #
        return_dict[f'{year}']['master_produce'] = master_produce_df

        # Inventory #
        return_dict[f'{year}']['inventory'] = inventory_df    


        # Labor Manager Summary #
        return_dict[f'{year}']['labor_manager_summary'] = labor_manager_summary_df



        print()
        print('====================================')
        print(f'Files processed for year {year}.')
        print('====================================')
        print()


    return return_dict

def dictionary_dataframes_to_csv(dictionary_of_dataframes):
    
    '''
    :param: dictionary_of_dataframes - a dictionary with the years as primary keys and the files as secondary keys
        see function -> worksheets_to_df(start_year,end_year)

        for each primary_key or year in dict_o_dataframes
        make a list of the DFs in the sub-dict
        nav to HOME > make new DIR for year
            
            then
            
        for each file in sub-dict:
            extract info such as the year and name of file > save file as CSV
            REPEAT
        ------------------------------------------------------------------------------------------------
            
    resulting file structure - compiled data>
                                            year>
                                                file01.csv
                                                file01.csv
                                                file03.csv
                                            year>
                                                etc.


    
    '''
    
    # sets home as current working directory
    home = os.getcwd()
    
    # sets up primary keys for iteration through years of dictionary O' dataframes.
    years_list = list(dictionary_of_dataframes.keys())
    
    # sets the name of the directory to create, that will house all of the newly cruched CSVs
    compiled_dir = 'compiled_data'
    for file_year in years_list:
        # nav to Home Directory
        os.chdir(home)

        files_list = list(dictionary_of_dataframes[f'{file_year}'].keys())
        print()
        print()
        print(' --------------------- BEGIN SAVING OF DATAFRAMES as CSV --------------------- ')
        print()
        print(' ---------------------------------------------------------------------------------------- ')
        print(f'Current Working Directory is {os.getcwd()}')
        print(' ---------------------------------------------------------------------------------------- ')
        try:
            print(f'Attempting to create directory for {compiled_dir}...')
            print(f'')
            os.mkdir(f'{home}/{compiled_dir}')
            os.chdir(f'{home}/{compiled_dir}')

        except FileExistsError:
            print(f'Directory {compiled_dir} Already Exists, Moving into {compiled_dir}... ')
            print(f'')
            os.chdir(f'{home}/{compiled_dir}')

        try:
            print(f'Attempting to create directory for {file_year}...')
            print(f'')
            os.mkdir(f'{home}/{compiled_dir}/{file_year}')
            os.chdir(f'{home}/{compiled_dir}/{file_year}')

        except FileExistsError:
            print(f'Directory {file_year} Already Exists, Moving into {file_year}... ')
            print(f'')
            os.chdir(f'{home}/{compiled_dir}/{file_year}')


        for file in files_list:
            try:
                print(f'Saving {file_year}_{file} as CSV')
                dictionary_of_dataframes[f'{file_year}'][f'{file}'].to_csv(f'{file_year}_{file}.csv', index=False)        
                print('=======================')
                print()
            except:
                print(f'Issue detected with {file}, it may not exist. Moving on..')
                print()

        print(f'Resetting Directory to {home}')
        os.chdir(f'{home}')
        print()
        print(f'Current Working Directory is {os.getcwd()}')
        print()

start_year,end_year = take_input()

dataframe_dictionary = worksheets_to_df(start_year,end_year)

dictionary_dataframes_to_csv(dataframe_dictionary)