from firebase_admin import initialize_app
from ping import ping
from print_weekly_report import print_weekly_report
from print_monthly_report import print_monthly_report
from art import art
from print_file import print_file
from print_translate import print_translate
from print_user_report import print_user_report
from print_yearly_report import print_yearly_report
from print_file import print_file

# Initialize Firebase once in the main file
initialize_app()
