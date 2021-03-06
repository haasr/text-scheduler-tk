from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import themed_tk
from datetime import datetime as dt
import requests
import re

POST_URL = 'https://api.groupme.com/v3/bots/post' # URL for POST requests

notif_time = '30 minutes before'
time_pattern = re.compile("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$") # Pattern to validate time strings
notif_pattern = re.compile("[0-9]?[0-9] [a-z*]") # Pattern to validate time strings for notification

reminder_data = {
    'title': '',
    'phone_number': '',
    'description': '',
    'start_date': '',
    'reminder_time': '',
    'notification': ''
}


def reset_reminder_data():
    global reminder_data

    reminder_data = {
        'title': '',
        'phone_number': '',
        'description': '',
        'start_date': '',
        'reminder_time': '',
        'notification': ''
    }


class ReminderWindow(themed_tk.ThemedTk):
    def __init__(self, bot_id, theme, phone_numbers, default_number_key):
        super().__init__(theme=theme, themebg=True)

        s = ttk.Style()
        s.configure('.', font=('Arial', 13))

        self.BOT_ID = bot_id
        self.phone_numbers_opts = phone_numbers.keys()
        self.phone_numbers = phone_numbers
        self.default_number_key = default_number_key

        self.title('Ryan Bot: Schedule a text reminder')
        self.title_large = 'Ryan Bot: Text Reminders'
        self.minsize(512, 420)

        self.init_components()
        self.init_labels()
        self.add_to_window()
        mainloop()


    def init_components(self):
        self.title_field = ttk.Entry(self, width=41)
        self.phone_number_field = StringVar(self)
        self.phone_number_field.set(self.default_number_key)

        self.phone_numbers_optmenu = ttk.OptionMenu(
            self,
            self.phone_number_field,
            self.default_number_key,
            *self.phone_numbers_opts,
        )

        self.description_field = Text(
            self,
            width=32,
            height=3
        )
        self.start_date_field = ttk.Entry(self, width=41)
        self.reminder_time_field = ttk.Entry(self, width=41)
        self.notification_field = ttk.Entry(self, width=41)

        self.clear_button = ttk.Button(
            self,
            text='Clear',
            command=self.clear_reminder_data,
        )

        self.send_button = ttk.Button(
            self,
            text='Send',
            command=self.send_reminder_data,
        )

        self.exit_button = ttk.Button(
            self,
            text='Exit',
            command=self.destroy,
        )


    def init_labels(self):
        bgcolor = self.config('background')[4] # Current background color

        self.window_title_label = Label(
            self,
            text=self.title_large,
            fg='#4286F6',
            bg=bgcolor,
            font=('Arial', 20),
            wraplength=350,
        )

        self.title_label = ttk.Label(
            text='Title:'
        )

        self.phone_number_label = ttk.Label(
            text='Contact:',
        )

        self.description_label = ttk.Label(
            text='Description:',
        )

        self.start_date_label = ttk.Label(
            text='Start date (mm/dd):',
        )

        self.reminder_time_label = ttk.Label(
            text='Time:',
        )

        self.notification_label = ttk.Label(
            text='Notify at:',
        )


    def add_to_window(self):
       self.window_title_label.place(x=32, y=16)

       self.clear_button.place(x=380, y=22)

       self.title_label.place(x=32, y=92)
       self.title_field.place(x=180, y=92)

       self.phone_number_label.place(x=32, y=128)
       self.phone_numbers_optmenu.place(x=180, y=128)

       self.description_label.place(x=32, y=168)
       self.description_field.place(x=180, y=168)

       self.start_date_label.place(x=32, y=230)
       self.start_date_field.place(x=180, y=230)

       self.reminder_time_label.place(x=32, y=258)
       self.reminder_time_field.place(x=180, y=258)

       self.notification_label.place(x=32, y=286)
       self.notification_field.place(x=180, y=286)

       self.send_button.place(x=180, y=344)
       self.exit_button.place(x=310, y=344)


    # Ensures task date is not already in past
    def validate_date(self, date):
        dt_date = dt.strptime(date, '%m/%d/%y')
        now = dt.now()
        diff = dt_date - now
        if diff.days < -1: # Return false if date precedes today's date.
            print(diff.days)
            return False
        else:
            return True


    def try_set_phone_number(self, number):
        number = number.replace('-', '')
        if re.match('^[0-9]{10,16}$', number):
            reminder_data['phone_number'] = number
            return 'Phone number is set to ' + number, True
        else:
            return 'Specify phone number as a 9-13 digit number either with or without hyphens', False


    # Validates the date format and checks to see whether the date
    # is in the past. If validation passed, the reminder's date is set accordingly.
    # Reply string and date_valid bool returned.
    def try_set_reminder_date(self, date):
        global reminder_data
        date_valid = False
        try:
            dt.strptime(date, '%m/%d/%y') # Validate date format
            if self.validate_date(date): # Validate the date isn't already past.
                reminder_data['start_date'] = date
                reply = 'Task date is set to ' + date
                date_valid = True
            else:
                reply = 'The selected date is already past'
        except:
            # Append current year if not specified:
            try:
                date = date + '/' + str(dt.now().year)[2:]
                dt.strptime(date, '%m/%d/%y') # Validate date format
                if self.validate_date(date): # Validate the date isn't already past.
                    reminder_data['start_date'] = date
                    reply = 'Reminder date is set to ' + date
                    date_valid = True
                else:
                    reply = 'The selected date is already past'
            except:
                reply = f"Date format is invalid. Use 'MM/DD' or 'MM/DD/YY'"

        return reply, date_valid


    # Validates the time format passed by checking it against time_pattern.
    # If AM/PM, it converts to 24-hr time. Sets the reminder's time if validation
    # passed. Returns string reply and bool time_valid.
    def try_set_reminder_time(self, time):
        global reminder_data
        reply = f"The reminder's time is invalid. Format the time as 'HH:MM' or 'HH:MM pm'"
        time_valid = False

        if 'am' in time:
            time = time.split(' am')[0]
            if re.match(time_pattern, time): # Validate time
                reminder_data['reminder_time'] = time
                reply = 'Reminder\'s time is set to ' + time
                time_valid = True

        elif 'pm' in time:
            time = time.split(' pm')[0]
            if re.match(time_pattern, time): # Validate time
                # Convert to 24-hr:
                time_split = time.split(':')
                hour_int = int(time_split[0]) + 12
                reminder_data['reminder_time'] = str(hour_int) + ':' + time_split[1]
                reply = 'Reminder\'s time is set to ' + reminder_data['reminder_time']
                time_valid = True

        else: # Already in 24-hr time
            if re.match(time_pattern, time):
                reminder_data['reminder_time'] = time
                reply = 'Reminder\'s time is set to ' + time
                time_valid = True

        return reply, time_valid


    # Attempts to set the notification time of task. If the time
    # string matches the pattern, notif_pattern and the time unit
    # used (minute, hour, day, etc.) is recognized, the reminder_data's
    # notification value is set to the string.
    # Returns string reply and bool time_valid
    def try_set_notif_time(self, time):
        global reminder_data

        if re.match(notif_pattern, time): # Check that the pattern matches
            if ((' minute' in time) or (' hour' in time) or (' day' in time)
                or (' week' in time)): # check for one of the valid units of time
                reminder_data['notification'] = time
                reply = 'Notification set for ' + time
                time_valid = True
        elif 'start time' in time:
            reminder_data['notification'] = time
            reply = 'Notification set for ' + time
            time_valid = True
        else:
            reply = (
                f"The notification duration is invalid. E.g. '45 minutes before', "
                f" '2 days before', or 'at the reminder's start time'."
            )
            time_valid = False

        return reply, time_valid


    def clear_reminder_data(self):
        self.title_field.delete(0, END)
        self.description_field.delete(1.0, END)
        self.start_date_field.delete(0, END)
        self.reminder_time_field.delete(0, END)
        self.notification_field.delete(0, END)


    def send_reminder_data(self):
        global reminder_data

        stop = False
        # TODO: Write some kind of switch-case-like module in the future.
        # Why doesn't Python just have switch cases tho...
        while not stop: # Keep doing validation checks until first validation fails
            reply, valid = self.try_set_phone_number(self.phone_numbers[self.phone_number_field.get()])
            stop = not valid
            if not valid:
                messagebox.showerror('Validation error', reply)
            reply, valid = self.try_set_reminder_date(self.start_date_field.get())
            stop = not valid
            if not valid:
                messagebox.showerror('Validation error', reply)
            reply, valid = self.try_set_reminder_time(self.reminder_time_field.get())
            stop = not valid
            if not valid:
                messagebox.showerror('Validation error', reply)
            reply, valid = self.try_set_notif_time(self.notification_field.get())
            if not valid:
                messagebox.showerror('Validation error', reply)
            stop = True


        reminder_data['title'] = self.title_field.get().replace('|', '-') # replace | because it is delimiter
        reminder_data['description'] = self.description_field.get(1.0, END).replace('|', '-')

        err = False
        for k in reminder_data.keys():
            if reminder_data[k] == '':
                messagebox.showerror('Empty field', f"{k} field cannot be empty")
                err = True

        if not err:
            message = (
               f"<createreminder> {reminder_data['title']}|{reminder_data['phone_number']}"
               f"|{reminder_data['description']}|{reminder_data['start_date']}"
               f"|{reminder_data['reminder_time']}|{reminder_data['notification']}"
            )

            post_params = {
                'bot_id': self.BOT_ID,
                'text': message
            }

            resp = requests.post(POST_URL, params=post_params)

            if resp.status_code == 202:
                messagebox.showinfo('Sent status', 'Message sent')
            else:
                messagebox.showerror('Sent status', f"{resp.status_code} - {resp.reason}")