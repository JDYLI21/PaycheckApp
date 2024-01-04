import config
import discord
from paycheck_db import Database
from datetime import date
from datetime import timedelta
from re import split as resplit

months = {"01": "January",
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

weekday_map = {0: "Monday",
               1: "Tuesday",
               2: "Wednesday",
               3: "Thursday",
               4: "Friday",
               5: "Saturday",
               6: "Sunday"}

tax_bracket = {0: 0.105,
               14001: 0.175,
               48001: 0.3,
               70001: 0.33,
               180000: 0.39}

ietc_threshold = [24000, 44000, 10] #min, max, $ per week
ietc_over_threshold = [44001, 48000, 0.13] #min, max, $ reduced every week

class AddHour:
    def __init__(self, hourly_wage, kiwisaver, student_loan, user_input):
        """This class will handle parsing the user's message, and returning the required format for
            appending to the database if it is successful

            :param hourly_wage: the user's hourly wage fetched from the database
            :param kiwisaver: the user's kiwisaver rate fetched from the database
            :param student_loan: whether the user has a student loan to repay, fetched from the database
            :param user_input: the user's raw input to the bot
        """
        self.hours = 0
        self.hourly_wage = hourly_wage
        self.kiwisaver = kiwisaver
        self.student_loan_threshold = 22828 if student_loan == 0 else 999999999
        self.ietc_threshold = [24000, 44000, 10] #min, max, $ per week
        self.ietc_over_threshold = [44001, 48000, 0.13] #min, max, $ reduced every week

        self.today = date.today()
        self.date = None

        self.user_input = user_input.content
        self.parsed_input = None
        self.input_error = None
        self.today_check = None

    def parse(self):
        """Takes the user's input and checks its formatting, running the necessary functions when
            the check is satisfactory
        """
        # Truncates the bot command portion of the input and splits into list based on delimiters "/" and " "
        self.parsed_input = resplit('/|\s', self.user_input[5:])

        """Check for correct formatting of either
            hours
            DD hours
            DD/MM hours
            DD/MM/YYYY hours
        """
        for index, comp in enumerate(self.parsed_input):
            if not comp.replace('.', '').isnumeric():
                self.input_error = "A non numeric character was entered in the date or hours portion"
                return
            
            if len(self.parsed_input) == 4:
                if ((index == 0 or index == 1) and (len(comp) != 2) and len(comp) != 1) or (index == 2 and len(comp) != 4):
                    self.input_error = "Please enter accordingly to the format DD/MM/YYYY hours"
                    return
                
            elif len(self.parsed_input) == 2 or len(self.parsed_input) == 3:
                if index != len(self.parsed_input) - 1 and (len(comp) != 2 and len(comp) != 1):
                    self.input_error = "Please enter accordingly to the format DD/MM hours"
                    return
                
        self.parsed_input = [f'{int(num):02d}' if num != self.parsed_input[-1] and len(num) != 4 else num for num in self.parsed_input]
            
    def add(self):
        # Adding in the missing months to the user's input
        entries = [str(self.today.year), f'{self.today.month:02d}', f'{self.today.day:02d}']
        # Extends the parsed list to have 4 elements for day, month, year, hours
        [self.parsed_input.extend([self.parsed_input[-1]]) for i in range(4 - len(self.parsed_input))] 
        for index, comp in enumerate(self.parsed_input): 
            # If the day, month, or year elements in the parsed list have the same value as hours, change it to
            # the current day, month, or year
            if comp == self.parsed_input[-1] and index != 3:
                self.parsed_input[index] = entries[2 - index]
        self.date = f'{self.parsed_input[2]}/{self.parsed_input[1]}/{self.parsed_input[0]}'
        self.hours = self.parsed_input[3]
        
    def __str__(self):
            """Success string for the feedback embed
            """
            if self.date:
                if self.date == f'{self.today.year}/{self.today.month:02d}/{self.today.day:02d}':
                    return "Today's hours successfully added"
                return f"{self.parsed_input[0]} {months[self.parsed_input[1]]} {self.parsed_input[2]}'s hours were added successfully"
        
class ViewHours:
    pass

class RemoveHour:
    pass

class PayCalc:
    pass

class PossibleCommands:
    """Embed of all the possible commands for this bot
    """
    def __init__(self):
        self.embed = discord.Embed(title = None, description = None, color = discord.Color.blue())
        self.embed.set_author(name = None, icon_url = None)
        
    async def send_embed_a(self, message):
        """Examples for commands to add hours

        :param message: the user's message fetched from the discord API
        """
        self.embed.title = 'Commands for Adding Hours'
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.description = """To add your hours, prefix your command with .p a, followed by the date
and how many hours you want to add, leave blank for today
e.g. 
.p a 7.5 - 7.5 hours worked today
.p a 20 7.5 - 7.5 hours worked on the 20th
.p a 20/02 7.5 - 7.5 hours wored on the 20th of Feb
.p a 20/02/1991 7.5 - 7.5 hours worked on the 20th of Feb, 1991"""
        await message.channel.send(embed=self.embed)

    async def send_embed_v(self, message):
        """Examples for commands to view hours
        
        :param message: the user's message fetched from the discord API
        """
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.description = """To view your hours, prefix your command with .p v, followed by the date
Leave blank for today, type the month and year (leave blank for current year) for a specific month
Enter a specific date to retrieve hours for that specific date
e.g.
.p v  - displays the hours for the current month
.p v week - displays the hours for the current week
.p v w - shortform of .p v week
.p v month - longform of .p v
.p v year - displays the hours for the current year
.p v y - shortform of .p v year
.p v 2022/04/01 2023/03/31 - displays the hours from 2022/04/01 to 2023/03/31 (both inclusive)
.p v 04 - displays the hours for April in the current year
.p v April - displays the hours for April in the current year
.p v 04/2023 - displays the hours for April 2023
.p v April 2023 - displays the hours for April 2023"""
        await message.channel.send(embed=self.embed)

    async def send_embed_d(self, message):
        """Examples for commands to delete records
        
        :param message: the user's message fetched from the discord API
        """
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.description = """To delete a record, prefix your command with .p d, followed by the date
Leave blank for today, and please note to type the specific date otherwise
e.g.
.p d  - Deletes the record for today
.p d 2022/04/01 - Deletes the record for 2022/04/01"""
        await message.channel.send(embed=self.embed)

    async def send_embed_calc(self, message):
        """Examples for commands to use the calculator
        
        :param message: the user's message fetched from the discord API
        """
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.description = """To use the calculator, prefix your command with .p calc, followed by the following parameters
.p calc hours (n) | frequency of pay (weekly, fornightly, **monthly**) | kiwisaver (**3%**. n%) | student_loan (n, **y**) - bold indicates default 
e.g.
.p calc 7.5 - defaults to monthly pay, kiwisaver rate of 3%, with student loans to repay
.p calc 7.5 monthly - defaults to kiwisaver rate of 3% with student loans to repay
.p calc 7.5 monthly 3 - defaults to student loans to repay
----------
It is also possible to skip parameters to default by putting d for the parameter
e.g.
.p calc 7.5 d d n - 7.5 hours with monthly pay, kiwisaver rate of 3%, and no student loans to repay"""
        await message.channel.send(embed=self.embed)

    async def send_embed(self, message):
        """General overview of how to use the bot
        
        :param message: the user's message fetched from the discord API
        """
        self.embed.title = "Paycheck Calculator & Database"
        self.embed.description = "This is a description of the possible commands for this bot"
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.add_field(name = "Adding Hours", inline = False, value = """To add your hours, prefix your command with .p a, followed by the date
and how many hours you want to add, leave blank for today
----------
.p a ? to view examples for commands to add hours""") # Description for adding hours
        self.embed.add_field(name = "Viewing Hours", inline = False, value = """To view your hours, prefix your command with .p v, followed by the date
Leave blank for today, type the month and year (leave blank for current year) for a specific month
Enter a specific date to retrieve hours for that specific date
----------  
.p v ? to view examples for commands to view hours""") # Description for viewing hours
        self.embed.add_field(name = "Delete Record", inline = False, value = """To delete a record, prefix your command with .p d, followed by the date
Leave blank for today, and please note to type the specific date otherwise
----------
.p d ? to view examples for commands to delete records""")
        self.embed.add_field(name = "Calculator", inline = False, value = """For commands to use the calculator, type
.p calc ?""")
        await message.channel.send(embed=self.embed)
        self.embed.clear_fields()

class FeedbackEmbed:
    """This embed class is for success or error in the user's input
    """
    def __init__(self):
        self.embed = discord.Embed(title = None, description = None, color = None)
        self.embed.set_author(name = None, icon_url = None)

    async def send_success_embed(self, message, operation):
        """Sends the embed with the successful operation in the user's input
        
        :param message: the user's message fetched from the discord API
        :param operation: the operation performed on the user's requested, passed in on the fly
        """
        self.embed.title = 'Success!'
        self.embed.description = str(operation)
        self.embed.color = discord.Color.green()
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        await message.channel.send(embed=self.embed)

    async def send_error_embed(self, message, error):
        """Sends the embed with the specific error in the user's input
        
        :param message: the user's message fetched from the discord API
        :param error: the user's error formatted before being passed onto this parameter
        """
        self.embed.title = 'Error in Input'
        self.embed.description = error
        self.embed.color = discord.Color.red()
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        await message.channel.send(embed=self.embed)

    async def new_user_embed(self, message):
        """Sends the embed providing instructions for the user to register their info with the bot
        
        :param message: the user's message fetched from the discord API
        """
        self.embed.title = 'New User'
        self.embed.description = 'Please register your info to use the paycheck app'
        self.embed.color = discord.Color.red()
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.add_field(name = 'To Register your Details', inline = False, 
                             value = """Please type the prefix .p r, followed by your hourly wage, kiwisaver contributions, and whether you have any student loans or not
hourly wage - just the number without the dollar sign (23.5)
kiwisaver - just the percentage without the percent sign (0) (3) (10)
student loans - y (yes) or n (no)
e.g.
.p r 23.5 3 y
.p r 23.5 0 n""")
        await message.channel.send(embed=self.embed)

if __name__ == '__main__':
    database = Database()
    bot_embed = PossibleCommands()
    feedback = FeedbackEmbed()
    
    if not database.check:
        database.initialise()

    intents = discord.Intents.default()
    intents.message_content = True
    
    client = discord.Client(intents = intents)

    @client.event   
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        if message.content.startswith('.p'):
            user = database.find_user(message.author.id)
            if not user and message.content.startswith('.p r'):
                pass # WORK ON THIS RN

            elif not user:
                await feedback.new_user_embed(message)

            if message.content in ['.p a ?', '.p v ?', '.p d ?', '.p calc ?']:
                cmd_map = {'.p a ?': bot_embed.send_embed_a,
                           '.p v ?': bot_embed.send_embed_v,
                           '.p d ?': bot_embed.send_embed_d,
                           '.p calc ?': bot_embed.send_embed_calc}
                await cmd_map[message.content](message)

            elif message.content.startswith('.p a'):
                add_instance = AddHour(user[0][1], user[0][2], user[0][3], message)
                add_instance.parse()
                if add_instance.input_error:
                    await feedback.send_error_embed(message, add_instance.input_error)

                else:
                    add_instance.add()

                    if not database.find_records(add_instance.date, add_instance.date, user[0][0]):
                        database.add_record(add_instance.date, add_instance.hours, user[0][1], user[0][0])
                        await feedback.send_success_embed(message, add_instance)
                    
                    else:
                        await feedback.send_error_embed(message, "An entry for this date already exists")

            elif message.content.startswith('.p w'):
                pass

            elif message.content.startswith('.p r'):
                pass
            
            else: #Print embed of possible commands
                await bot_embed.send_embed(message)

    client.run(config.api_key)