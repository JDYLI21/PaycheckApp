import discord
import config
from paycheck_db import Database
from datetime import date
from datetime import timedelta
from re import split as resplit


class AddHour:
    def __init__(self, hours, hourly_wage, kiwisaver, student_loan, user_input):
        """This class will handle parsing the user's message, and returning the required format for
            appending to the database if it is successful
        """
        self.hours = hours
        self.hourly_wage = hourly_wage
        self.kiwisaver = kiwisaver
        self.student_loan_threshold = 22828 if student_loan == 0 else 999999999
        self.ietc_threshold = [24000, 44000, 10] #min, max, $ per week
        self.ietc_over_threshold = [44001, 48000, 0.13] #min, max, $ reduced every week

        self.date = None

        self.user_input = user_input
        self.input_error = None

    def parse():
        pass

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
        
    async def send_embed_a(self, message): # Examples for adding hours
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

    async def send_embed_v(self, message): # Examples for viewing hours
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

    async def send_embed_d(self, message): # Examples for deleting hours
        self.embed.set_author(name = message.author.display_name, icon_url = message.author.display_avatar)
        self.embed.description = """To delete a record, prefix your command with .p d, followed by the date
Leave blank for today, and please note to type the specific date otherwise
e.g.
.p d  - Deletes the record for today
.p d 2022/04/01 - Deletes the record for 2022/04/01"""
        await message.channel.send(embed=self.embed)

    async def send_embed_calc(self, message): # Examples for the pay calculator
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

class ErrorEmbeds:
    pass

if __name__ == '__main__':
    database = Database()
    bot_embed = PossibleCommands()
    errors = ErrorEmbeds()
    
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
            if not user:
                pass #Embed of you are not in the system

            if message.content in ['.p a ?', '.p v ?', '.p d ?', '.p calc ?']:
                cmd_map = {'.p a ?': bot_embed.send_embed_a,
                           '.p v ?': bot_embed.send_embed_v,
                           '.p d ?': bot_embed.send_embed_d,
                           '.p calc ?': bot_embed.send_embed_calc}
                await cmd_map[message.content](message)

            elif message.content.startswith('.p a'):
                add_instance = AddHour(user[1], user[2], user[3], message)
                if add_instance.input_error:
                    errors # ASFUHAILEFJHAKSLEJFHBASKLEJFKASELJFEASKLJALEKJRTHEALKRJHASER 

                database.add_record(add_instance.date, add_instance.hours)

            elif message.content.startswith('.p w'):
                pass

            elif message.content.startswith('.p r'):
                pass
            
            else: #Print embed of possible commands
                await bot_embed.send_embed(message)

    client.run(config.api)