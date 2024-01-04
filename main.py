from db import Database
from datetime import date
from datetime import timedelta
from re import split as resplit

class Main:
    """Though the program only requires one class for its interface, a class is still used for ease of organisation
    """
    def __init__(self):
        """Initialises the variables for the calculations to work, as well as dictionaries for organisation"""

        self.hourly_wage = 23.5
        self.tax_bracket = {0: 0.105,
                            14001: 0.175,
                            48001: 0.3,
                            70001: 0.33,
                            180000: 0.39}
        self.acc_levy = 0.0153
        self.student_loan_threshold = 22828
        self.kiwisaver_rate = 0.03
        self.ietc_threshold = [24000, 44000, 10] #min, max, $ per week
        self.ietc_over_threshold = [44001, 48000, 0.13] #min, max, $ reduced every week

        # Menu navigation functions
        self.menu_dict = {1: self.add_hours, 
                          2: self.view_hours,
                          3: self.delete_hours}
        
        self.weekday_map = {0: "Monday",
                            1: "Tuesday",
                            2: "Wednesday",
                            3: "Thursday",
                            4: "Friday",
                            5: "Saturday",
                            6: "Sunday"}

        # Mapping numbers to the corresponding months for ease of formatting
        self.months = {"01": "January",
                       "02": "February",
                       "03": "March",
                       "04": "April",
                       "05": "May",
                       "06": "June",
                       "07": "July",
                       "08": "August",
                       "09": "September",
                       "10": "October",
                       "11": "November",
                       "12": "December"}
        
        self.today = date.today()
    
    def main_menu(self):
        """Self explanatory main menu screen
        """

        print('''\nPlease choose from the following options
1) Add work hour
2) View work hours
3) Delete work hour
or type "exit" to quit''')
        while True:
            try:
                user_choice = input("")
                if user_choice == "exit":
                    exit()
                self.menu_dict[int(user_choice)]()
                break
                
            except ValueError:
                print("Please enter 1, 2, 3, or exit")
                self.main_menu()
                break
    
    def add_hours(self):
        """This will be a repetitive loop until the user types in "exit" to return to the main menu
        """

        print('''\nPlease enter the date and hours worked on that day
Leave blank for today, alternatively type "exit" to return to the main menu
Please note if the date or month is a single digit, prefix it with a 0 (e.g. 3 Feb should be 03/02)
i.e. (7.5) or (20/02/1991 7.5) or (20 7.5) or (20/02 7.5)''')
        user_input = input('')

        if user_input == "exit": self.main_menu() 
            
        # Splits the input into a list based on delimiters "/" and " "
        check = resplit('/|\s', user_input)

        # Checks for the correct formatting of either
        # hours
        # DD hours
        # DD/MM hours
        # DD/MM/YYYY hours
        for index, comp in enumerate(check):
            if not comp.replace(".", "").isnumeric():
                print("\nError in input")
                self.add_hours()
            
            if len(check) == 4:
                if ((index == 0 or index == 1) and len(comp) != 2) or (index == 2 and len(comp) != 4):
                    print("\nError in input")
                    self.add_hours()

            elif len(check) == 2 or len(check) == 3:
                if index != len(check) - 1 and len(comp) != 2:
                    print("\nError in input")
                    self.add_hours()
                
        #Check to see if only a single number was inputted to enter today's hours
        if len(check) == 1:
            formatted_today = f'{self.today.year}/{self.today.month}/{self.today.day}'
            if not database.find_records(formatted_today, formatted_today):
                database.add_record(self.today.strftime("%Y/%m/%d"), check[0], self.hourly_wage)
                print("\nToday's hours successfully added")
                
            else:
                print("\nError, an entry for today already exists")
            
            self.add_hours()
        
        #Add in the missing months then append to the database
        entries = [str(entry) for entry in [self.today.year, self.today.month]]
        if len(entries[1]) == 1: entries[1] = "0" + entries[1]
        [check.extend([check[-1]]) for i in range(4 - len(check))]
        for index, comp in enumerate(check):
            if comp == check[-1] and index != 3:
                check[index] = entries[2 - index]
        
        entry_date = f'{check[2]}/{check[1]}/{check[0]}'
        if not database.find_records(entry_date, entry_date):
            database.add_record(entry_date, check[3], self.hourly_wage)
            print(f"{check[0]} {self.months[check[1]]} {check[2]}'s hours added successfully")
        
        else:
            print("\nAn entry for this date already exists")

        self.add_hours()
    
    def view_hours(self):
        """Will request user to input the range they want to view and return the expected pay
            for that range of time
        """

        #Store the keywords
        keywords = ["this week", "w", "", "this month", "m", "this year", "y", *self.months.values()]

        print('''\nPlease enter the time period you would like to view
Blank defaults to this current month, type month and year (leave blank for current year) for a specific month
Enter a specific date to retrieve hours for that specific date
i.e.  or this week (w) or this month (m) or this year (y) or 2022/04/01 or 2022/04/01 - 2023/03/31 (in that specific format) or April or April 2023''')
        user_input = input('')

        if user_input == "exit": self.main_menu()

        #Checks the input for keywords - this week, this month, this year
        if user_input in keywords:
            if user_input in keywords[0:2]: #this week
                week = self.today.weekday()
                start_of_week = self.today.day - week
                end_of_week = 6 - week + self.today.day
                #Request from database with the exact dates of the start and end of the week
                hours = database.find_records(f'{self.today.year}/{self.today.month}/{start_of_week}', f'{self.today.year}/{self.today.month}/{end_of_week}')
                if not hours:
                    print("\nSorry, no records could be found for this week")
                    self.main_menu()
                #Format the database output to a single list of ready-to-print strings
                formatted_hours = [f'{self.weekday_map[date(int(hour[0][0:4]), int(hour[0][5:7]), int(hour[0][-2:])).weekday()]} - {hour[1]} hours' for hour in hours]
                formatted_hours.reverse()
                print("\nThese are the hours for this week:")
                print(*(hour for hour in formatted_hours), sep = '\n')
                self.take_home_calculation(sum([hour[1] for hour in hours]), "week", hours[0][2])

            elif user_input in keywords[2:5]: #this month
                next_month = self.today.replace(day = 28) + timedelta(days = 4)
                last_day_of_month = next_month - timedelta(days = next_month.day)
                hours = database.find_records(f'{self.today.year}/{self.today.month:02d}/01', f'{self.today.year}/{self.today.month:02d}/{last_day_of_month.day}')
                if not hours:
                    print("\nSorry, no records could be found for this month:")
                    self.main_menu()
                formatted_hours = [f'{hour[0][-2:]} - {hour[1]} hours' for hour in hours]
                formatted_hours.reverse()
                print(f"\nThese are the hours for {self.months[f'{self.today.month}' if len(str(self.today.month)) == 2 else f'0{self.today.month}']}")
                print(*(hour for hour in formatted_hours), sep = '\n')
                self.take_home_calculation(sum([hour[1] for hour in hours]), "month", hours[0][2])

            elif user_input in keywords[5:7]: #this year
                hours = database.find_records(f'{self.today.year}/01/01', f'{self.today.year}/12/31')
                if not hours:
                    print("\nSorry, no records could be found for this year")
                    self.main_menu()
                formatted_hours = [f'{hour[0]} - {hour[1]} hours' for hour in hours]
                formatted_hours.reverse()
                print("\nThese are the hours for this year:")
                print(*(hour for hour in formatted_hours), sep = '\n')
                self.take_home_calculation(sum([hour[1] for hour in hours]), "year", hours[0][2])

            else:
                month_index = list(self.months.keys())[list(self.months.values()).index(user_input)]
                next_month = date(self.today.year, int(month_index), 28) + timedelta(days = 4)
                last_day_of_month = next_month - timedelta(days = next_month.day)
                hours = database.find_records(f'{self.today.year}/{month_index}/01', f'{self.today.year}/{month_index}/{last_day_of_month.day}')
                if not hours:
                    print(f"\nSorry, no records could be found for {user_input} {self.today.year}")
                    self.main_menu()
                formatted_hours = [f'{hour[0][-2:]} - {hour[1]} hours' for hour in hours]
                formatted_hours.reverse()
                print(f"\nThese are the hours for {user_input} @ ${hours[0][2]} an hour:")
                print(*(hour for hour in formatted_hours), sep='\n')
                self.take_home_calculation(sum([hour[1] for hour in hours]), "month", hours[0][2])

        check = resplit('/|-|\s', user_input)
        #Check for if the user wants to search a particular month at a particular year
        if len(check) == 2:
            if check[0] in keywords and check[1].isnumeric() and len(check[1]) == 4:
                month_index = list(self.months.keys())[list(self.months.values()).index(check[0])]
                next_month = date(int(check[1]), int(month_index), 28) + timedelta(days = 4)
                last_day_of_month = next_month - timedelta(days = next_month.day)
                hours = database.find_records(f'{check[1]}/{month_index}/01', f'{check[1]}/{month_index}/{last_day_of_month.day}')
                if not hours:
                    print(f"\nSorry, no records could be found for {check[0]} {check[1]}")
                    self.main_menu()
                formatted_hours = [f'{hour[0][-2:]} - {hour[1]} hours' for hour in hours]
                formatted_hours.reverse()
                print(f"\nThese are the hours for {check[0]} {check[1]} @ ${hours[0][2]} an hour:")
                print(*(hour for hour in formatted_hours), sep='\n')
                self.take_home_calculation(sum([hour[1] for hour in hours]), "month", hours[0][2])
            
            else:
                print("\nError in input")
                self.view_hours()
        
        #Check if the user has only requested for a single date
        if len(check) == 3 and all([comp.isnumeric() for comp in check]):
            if len(check[0]) == 4 and len(check[1]) == len(check[2]) == 2:
                hours = database.find_records(user_input, user_input)
                if not hours:
                    print(f"\nSorry, no records could be found for {user_input}")
                    self.main_menu()
                print(f'\nYou worked {hours[0][1]} hours on {hours[0][0]} @ ${hours[0][2]:.2f} an hour')
                self.main_menu()

        #Check if the lengths of all the inputs match the required format and if all the inputs in the dates are numeric
        if len(check) == 8 and all([comp.isnumeric() for comp in [i for i in check if i != ""]]): #removes the "" from the list to check for numeric
            if len(check[0]) == len(check[5]) == 4 and len(check[1]) == len(check[2]) == len(check[6]) and len(check[7]) == 2 \
                and len(check[3]) == len(check[4]) == 0:
                    hours = database.find_records(f'{check[0]}/{check[1]}/{check[2]}', f'{check[5]}/{check[6]}/{check[7]}')
                    if not hours:
                        print("\nSorry, no records could be found for this time period")
                        self.main_menu()
                    formatted_hours = [f'{hour[0]} - {hour[1]} hours @ ${hour[2]} an hour' for hour in hours]
                    formatted_hours.reverse()
                    print(f"\nThese are the hours for the dates ranging from {check[0]}/{check[1]}/{check[2]} till {check[5]}/{check[6]}/{check[7]}")
                    self.main_menu()

        print("\nError in Input")
        self.view_hours()
    
    def take_home_calculation(self, hours, time_period, wage):
        """Calculates the expected amount of take-home pay, amount and percentage taxed, and any student loans or kiwisaver deductions
        """

        time_period_map = {"week": 52,
                           "month": 12,
                           "year": 1}
        
        total_pay = hours * wage
        estimated_annual_earning = total_pay * time_period_map[time_period]
        student_loan = .12 * (estimated_annual_earning - self.student_loan_threshold) / time_period_map[time_period] if estimated_annual_earning > self.student_loan_threshold else 0
        kiwisaver = total_pay * self.kiwisaver_rate

        tax_rate = 0
        tax_threshold_count = sum(1 for bracket in list(self.tax_bracket.keys()) if estimated_annual_earning > bracket)
        for bracket in range(tax_threshold_count - 1):
            tax_rate += (list(self.tax_bracket.keys())[bracket + 1] - 1) / estimated_annual_earning * (list(self.tax_bracket.values())[bracket] + self.acc_levy)
        tax_rate += (estimated_annual_earning - list(self.tax_bracket.keys())[tax_threshold_count - 1]) / estimated_annual_earning * \
                    (list(self.tax_bracket.values())[tax_threshold_count - 1] + self.acc_levy)

        ietc = 0
        if self.ietc_threshold[0] < estimated_annual_earning < self.ietc_threshold[1]:
            ietc += 520
        elif self.ietc_over_threshold[0] < estimated_annual_earning < self.ietc_over_threshold[1]:
            ietc -= (estimated_annual_earning - self.ietc_over_threshold[0]) * 0.13
        ietc /= time_period_map[time_period]

        print(f'\nThe total amount of hours worked is: {hours} hours @ {wage}')
        print(f'The total pay is: ${total_pay}')
        print(f'The amount of student loan returned is: ${student_loan:.2f}')
        print(f'The amount paid to Kiwisaver contributions is: ${kiwisaver:.2f}')
        print(f'The tax rate will be: {tax_rate * 100:.2f}%')
        print(f'The amount taxed will be: ${total_pay * tax_rate:.2f}')
        print(f'The amount of IETC received will be: ${ietc:.2f}')
        print(f'The expected take home pay will be: ${total_pay * (1 - tax_rate) - student_loan - kiwisaver + ietc:.2f}')

        self.main_menu()

    def delete_hours(self):
        """Will first search for if the requested date exists, then deletes the date
            Done this way to inform user on the requested date's existence in the database
        """
        print('''\nPlease enter the date you would like to delete
Alternatively, type "exit" to exit to main menu
i.e. 2022/04/01''')
        user_input = input('')

        if user_input == "exit": self.main_menu()

        check = resplit('/', user_input)
        if len(check) == 3:
            if len(check[0]) == 4 and len(check[1]) == len(check[2]) == 2:
                if database.find_records(user_input, user_input):
                    database.delete_record(user_input)
                    print(f'\nSuccessfully deleted the record for {user_input}')
                    self.delete_hours()
                else:
                    print(f'\nThe record for {user_input} could not be found')
                    self.main_menu()
        
        print('\nError in Input')
        self.delete_hours()
                

if __name__ == '__main__':
    run = Main()
    database = Database()

    if not database.check:
        database.initialise()

    run.main_menu()