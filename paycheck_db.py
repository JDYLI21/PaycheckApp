import sqlite3

class Database:
    """Separate file and class used for database for organisational purposes. Having the database as an 
        instance variable is a bit redundant as there would only be one machine accessing the sqlite database
    """

    def __init__(self):
        """Connects to the database and checks for if the table exists. If the table does not exist, a new
            table and/or database file will be created. This is necessary for if the database file was missing
        """
        self.con = sqlite3.connect('bot_database.db')
        self.cur = self.con.cursor()

        self.cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="work_hours"')
        self.check = self.cur.fetchall()
    
    def initialise(self):
        """Only one table is needed to store the hours and date as there will only be one user for this
            program. In the future, if this program had to be adapted for multiple users another table
            mapping the user id would be created
        """
        self.cur.execute('CREATE TABLE work_hours (date TEXT, hours REAL, wage REAL, id INTEGER)')
        self.cur.execute('CREATE TABLE user_ids (id INTEGER, hourly_wage REAL, kiwisaver REAL, student loan INTEGER)')
        self.con.commit()

    def add_user(self, id, wage, kiwisaver, student_loan):
        """Adds the user into the user_ids table in the database to register the user into the system
        
        :param id: the user's discord id from the API
        :param wage: the user's hourly wage
        :param kiwisaver: the user's kiwisaver contributions
        :param student_loan: boolean for whether the user has a student_loan to repay or not
        """
        self.cur.execute('INSERT INTO user_ids VALUES (?, ?, ?, ?)', (id, wage, kiwisaver, student_loan))
        self.con.commit()

    def add_record(self, date, hours, wage, id):
        """Adds the date and hours from the main program into the database which should already be formatted

            :param hours: double containing the amount of hours worked
            :param date: date in the format YYYY/MM/DD for easier sorting
        """
        self.cur.execute('INSERT INTO work_hours VALUES (?, ?, ?, ?)', (date, hours, wage, id))
        self.con.commit()

    def find_user(self, id):
        """Searches the database for the user's details
        """
        self.cur.execute(f'SELECT * FROM user_ids WHERE id = "{id}"')
        return self.cur.fetchall()
    
    def find_records(self, start_date, end_date, id):
        """Searches for the dates between a given range in the database, works as dates are stored in the
            YYYY/MM/DD format which happens to work alphabetically

            :param start_date: the earliest date in the requested search range
            :param end_date: the latest date in the requested search range
            :param single_date: if the user is only searching for a specific date, default value = False
        """
        self.cur.execute(f'SELECT * FROM work_hours WHERE date BETWEEN "{start_date}" AND "{end_date}" AND id = {id}')
        return self.cur.fetchall()
    
    def delete_record(self, date, id):
        """Will search for aand delete the row corresponding to the given date if the row exists

            :param date: the requested date to delete
        """
        self.cur.execute(f'DELETE FROM work_hours WHERE date = "{date}" AND id = {id}')
        self.con.commit()