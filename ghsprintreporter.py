# release 1.1

from __future__ import division
from github3 import login
import datetime
from string import letters
from openpyxl import Workbook
from Tkinter import *
import ttk
import time
import threading
import smtplib
import csv
from email.mime.text import MIMEText

root = Tk()

# the csv file is formatted as follows:
# github username | user email | user manager's username | team name
# this 3 column csv is used to get the emails of the
# users who have violated the commit message format, and
# an email is sent to them and their manager about the
# violating commit. the csv file should reside in the
# same folder this program is being run from.
CSV_FILE_NAME = 'team'
NUM_BUSINESS_DAYS_PER_WEEK = 5


# a class for hourly burndown data structure and xls publishing
class Burndown:

    # process the ideal hours array incrementally and push it to a date-hours dict
    def process_ideal_by_inc(self, estimate_inc):
        self.estimate += estimate_inc
        self.interval = round(float(self.estimate / self.days), 3)
        temp = self.interval
        inc_date = self.start_date
        for num in range(self.days):
            self.date_hours_ideal_map[ inc_date ] += estimate_inc
            self.date_hours_ideal_map[ inc_date ] = self.estimate - temp
            temp += self.interval
            if inc_date.weekday() == 4:
                inc_date += datetime.timedelta(days = 3)
            else:
                inc_date += datetime.timedelta(days = 1)

    def process_actual_item(self, actual_hours, date):
        if (date.weekday() != 5) and (date.weekday() != 6):
            self.date_hours_actual_map[ date ] += actual_hours
            self.date_hours_burnup_map[ date ] += actual_hours

    def post_process(self):
        inc_date = self.start_date
        prev_date = None
        prev_hours = self.estimate
        burnup_prev_hours = 0
        for num in range(self.days):
            if (inc_date.weekday() != 5) and (inc_date.weekday() != 6):
                if prev_date:
                    prev_hours = self.date_hours_actual_map[ prev_date ]
                    burnup_prev_hours = self.date_hours_burnup_map[ prev_date ]
                temp = prev_hours - self.date_hours_actual_map[ inc_date ]
                self.date_hours_actual_map[ inc_date ] = temp
                self.date_hours_burnup_map[ inc_date ] += burnup_prev_hours
                prev_date = inc_date
            if inc_date.weekday() == 4:
                inc_date += datetime.timedelta(days = 3)
            else:
                inc_date += datetime.timedelta(days = 1)

    def burndown_data_to_sheet_obj(self, sheet):
        arr = [ "Ideal", "Burndown", "Burnup" ]
        sheet.add_data_row_bd(arr)
        inc_date = self.start_date
        for num in range(self.days):
            arr = [ self.date_hours_ideal_map[ inc_date ],
                self.date_hours_actual_map[ inc_date ],
                self.date_hours_burnup_map[ inc_date ] ]
            sheet.add_data_row_bd(arr)
            if inc_date.weekday() == 4:
                inc_date += datetime.timedelta(days = 3)
            else:
                inc_date += datetime.timedelta(days = 1)

    def print_completed_burndown(self):
        inc_date = self.start_date
        for num in range(self.days):
            if inc_date.weekday() == 4:
                inc_date += datetime.timedelta(days = 3)
            else:
                inc_date += datetime.timedelta(days = 1)

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        # this dict will map date keys to an array of ideal and actual hours
        # data structure ---> { date : [ ideal_hours, actual_hours ] }
        self.date_hours_ideal_map = {}
        self.date_hours_actual_map = {}
        self.date_hours_burnup_map = {}
        self.days = 1
        self.start_date = start_date
        self.end_date = end_date
        self.curr_actual_remaining = 0
        self.estimate = 0
        temp_date = self.start_date
        if self.start_date < self.end_date:
            while temp_date != self.end_date:
                if (temp_date.weekday() != 5) and (temp_date.weekday() != 6):
                    self.days += 1
                temp_date += datetime.timedelta(days = 1)
        inc_date = self.start_date
        for num in range(self.days):
            # self.date_hours_map_dict[ inc_date ] = [ 0, 0 ]
            self.date_hours_ideal_map[ inc_date ] = 0
            self.date_hours_actual_map[ inc_date ] = 0
            self.date_hours_burnup_map[ inc_date ] = 0
            if inc_date.weekday() == 4:
                inc_date += datetime.timedelta(days = 3)
            else:
                inc_date += datetime.timedelta(days = 1)


class ReportSheet:
    def __init__(self, name):
        self.name = name
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = 'Sprint Report'
        self.data = [ ]
        self.bd_data = [ ]
        # if (teamArr):
        #     for item in teamArr:
        #         self.bd_ws = self.wb.create_sheet(str(item) + ' ' + 'Burndown')
        # else:
        self.bd_ws = self.wb.create_sheet('Burndown')
        self.wb.save(name + ".xlsx")

    def add_data_row(self, arr):
        self.data.append(arr)

    def add_data_row_bd(self, arr):
        self.bd_data.append(arr)

    def post_process(self):
        for item in self.data:
            self.ws.append(item)
        for item in self.bd_data:
            self.bd_ws.append(item)
        self.wb.save(self.name + ".xlsx")


# email notification on report generation completion as traversing the
# issues in the repository can take time
def push_email():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_input.get(), email_pwd_input.get())
        FROM = email_input.get()
        TO = recipent_input.get()
        SUBJECT = "NOTIFICATION: Sprint Report Generated"
        TEXT = "Hello, your sprint report has been generated. Enjoy!"
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(email_input.get(), recipent_input.get(), message)
        server.quit()
    except Exception:
        update_status_message("Unable to send email", 2)


def push_email_to_user(sender_email, sender_pwd, recipent_email_list, email_sub,
                        email_msg, bcc_email=None, error_code=2):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_pwd)
        recipents = list([])
        recipents.extend(recipent_email_list)
        if bcc_email is not None:
            recipents.append(bcc_email)
        message = MIMEText(email_msg)
        message[ 'Subject' ] = email_sub
        message[ 'From' ] = sender_email
        message[ 'To' ] = ", ".join(recipents)
        server.sendmail(sender_email, recipents, message.as_string())
        server.quit()
    except Exception:
        update_status_message("Unable to send email", error_code)


# verify that the milestone assigned to the issue is in the on-going sprint
# this will be done by getting the current sprint, extracting the date from
# the current sprint, and comparing against milestone assigned to the issue
def verify_milestone(repo):
    sprint_due_date = None
    open_stones = repo.milestones('open')
    for stone in open_stones:
        if 'Sprint' in str(stone):
            if stone.due_on:
                sprint_due_date = stone.due_on.date()
    curr_date = datetime.date.today()
    if curr_date <= sprint_due_date:
        is_within_sprint = True
    else:
        is_within_sprint = False
    return is_within_sprint


def get_repo_by_index(gh, index):
    repos = gh.repositories()
    reparr = list([])
    for repo in repos:
        reparr.append(repo)
    return reparr[ index ]


def get_repo_by_name(gh, name):
    repos = gh.repositories()
    ret_repo = None
    for repo in repos:
        if repo.name == name:
            ret_repo = repo
    return ret_repo


def get_sprint_from_issue(issue):
    curr_sprint = issue.milestone
    sprint_info = None
    if curr_sprint:
        sprint_end_date = curr_sprint.due_on.date()
        start_date = sprint_end_date
        sprint_issues_count = curr_sprint.open_issues_count + \
                              curr_sprint.closed_issues_count
        sprint_info = { 'object': curr_sprint, 'issue-count': sprint_issues_count,
                        'end-date': sprint_end_date, 'start-date': start_date }
    return sprint_info


# this will return a dictionary containing the actual sprint object,
# the number of issues within the sprint, and the due date.
def get_curr_sprint_info(repo):
    curr_sprint = None
    sprint_info = None
    open_stones = repo.milestones('open')
    closed_stones = repo.milestones('closed')
    criteria = 'Sprint'
    num_days = int(sprint_weeks_input.get()) * NUM_BUSINESS_DAYS_PER_WEEK
    if sprint_override_input.get() != '':
        criteria = sprint_override_input.get()
    for stone in closed_stones:
        if criteria in str(stone):
            curr_sprint = stone
    for stone in open_stones:
        if criteria in str(stone):
            curr_sprint = stone
    if curr_sprint:
        sprint_issues_count = curr_sprint.open_issues_count + \
            curr_sprint.closed_issues_count
        sprint_end_date = curr_sprint.due_on.date()
        start_date = sprint_end_date
        for num in range(num_days - 1):
            if start_date.weekday() == 0:
                start_date += datetime.timedelta(days = -3)
            else:
                start_date += datetime.timedelta(days = -1)
        sprint_info = { 'object': curr_sprint, 'issue-count': sprint_issues_count,
                        'end-date': sprint_end_date, 'start-date': start_date }
    return sprint_info


def is_date_within_sprint(sprint_info, verify_date):
    if (verify_date <= sprint_info[ 'end-date' ]) and \
            (verify_date >= sprint_info[ 'start-date' ]):
        return True
    else:
        return False


def is_date_within_range(start_date, end_date, verify_date):
    if (verify_date >= start_date) and (verify_date <= end_date):
        return True
    else:
        return False


def get_date_from_input(date_str):
    date_year = int(date_str[ 0:4 ])
    date_month = int(date_str[ 5:7 ])
    date_day = int(date_str[ 8:10 ])
    created_date = datetime.date(date_year, date_month, date_day)
    if type(created_date) == datetime.date:
        return created_date
    else:
        return None


# returns the github username of the person who made the comment
# on the sprint issue
def get_comment_author(comment):
    author = comment.user
    return author


# hours can be written as a part of the comment body as
# '8hrs'. the numeric value will be extracted and recorded 
# for the resource against the issue, along with additional
# development notes provided inside the issue. how cool is that?
# multiple hour entries in one comment or issue body will be 
# added up and written as one value in a row on the sheet.
def parse_comment(text):
    data = [ 0, None ]
    loc = []
    hours_text_arr = []
    splt = text.split(' ')
    breakout = False
    for item in splt:
        if breakout is False:
            if 'hrs' in item:
                splt_yet_again = item.split("\n")
                for sub_item in splt_yet_again:
                    if 'hrs' in sub_item:
                        loc.append(sub_item.find('hrs'))
                        full_hours_text = str(sub_item)
                        hours_text_arr.append(full_hours_text)
    for item in hours_text_arr:
        if loc.count > 0:
            prefix_cleaned = item[ :-3 ]
            prefix_cleaned = prefix_cleaned.translate(None, letters)
            if prefix_cleaned.isdigit():
                data[ 0 ] += int(prefix_cleaned)
                data[ 1 ] = text.split(item)[ 1 ]
    return data


# need to check whether the comment we are processing for hours
# has already has its hours recorded in the Google Sheet. this
# will be done by checking the comment ID against the ID column
# in the sheet for the current sprint.
def comment_id_check(gs, comment):
    pass


# write information passed through the array into the xlsx
def process_sheet(ws, wb, arr, sheet_data_arr):
    ws.append(arr)
    sheet_data_arr.append(arr)
    wb.save('report.xlsx')
    return sheet_data_arr


def is_item_in_sheet(sheet_data_arr, item, col_num):
    found = False
    if sheet_data_arr:
        for row in sheet_data_arr:
            if row[ col_num ] == item:
                found = True
                break
    return found


# function checks whether an issue within the sprint or the date range
# has comments or not, then parses any available comments to check for
# hours which are appended to the worksheet array as well as the sheet
# itself.
def process_comments_and_report(sheet, issue, comments, sprint_info = None,
                                start_date = None, end_date = None, bd = None):
    processed_count = 0
    cmnt_count = 0
    some_hours_found = False
    stry_pnts = get_sp(issue)
    assignees = get_assignee_str(issue)
    status = issue.state
    sprint = str(issue.milestone)
    est = get_issue_estimate(issue)
    if (bd):
        bd.process_ideal_by_inc(est)
    for comment in comments:
        cmnt_count += 1
        comment_body = comment.body
        hours, notes = parse_comment(comment_body)
        if (hours is not None) and (hours != 0):
            some_hours_found = True
    if (cmnt_count > 0) and some_hours_found:
        for comment in comments:
            comment_date = comment.created_at.date()
            process = False
            if sprint_info and (issue_retrieval_method_var.get() == 1):
                if is_date_within_sprint(sprint_info, comment_date):
                    process = True
            elif issue_retrieval_method_var.get() == 2:
                if start_date and end_date:
                    if is_date_within_range(start_date, end_date, comment_date):
                        process = True
            if process:
                comment_body = comment.body
                comment_id = comment.id
                hours, notes = parse_comment(comment_body)
                if (hours is not None) and (hours != 0):
                    if not is_item_in_sheet(sheet.data, comment_id, 1):
                        arr = [ issue.number, assignees, status, stry_pnts,
                                comment_id, str(comment.user), sprint, est, hours,
                                comment_date, notes ]
                        sheet.add_data_row(arr)
                        processed_count += 1
                        if bd:
                            bd.process_actual_item(hours, comment_date)
    else:
        # put the issue in the list anyway even if it doesn't have any comments
        # only for the case when a sprint report is required, and not a date
        # range report. For the case of a date range report, this would not be
        # applicable since we need only report issues which have had comments
        # and they can be issues with or without sprint assignments.
        if sprint_info and (issue_retrieval_method_var.get() == 1):
            if not is_item_in_sheet(sheet.data, issue.number, 0):
                arr = [ issue.number, assignees, status, stry_pnts, None, None, sprint,
                        est, None, None, None ]
                sheet.add_data_row(arr)
                processed_count += 1
    if processed_count > 0:
        # return True, sheet_data_arr
        return True
    else:
        # return False, sheet_data_arr
        return False


def disable_process_buttons():
    sprint_report_button.config(state='disabled')


def enable_process_buttons():
    sprint_report_button.config(state='normal')


def disable_commit_buttons():
    commits_button.config(state='disabled')


def enable_commit_buttons():
    commits_button.config(state='normal')


def update_status_message(msg, code = 0):
    if code == 0:
        status_label.configure(foreground = "blue")
        enable_process_buttons()
        status_label[ 'text' ] = msg
    elif code == 1:
        status_label.configure(foreground = "orange")
        disable_process_buttons()
        status_label[ 'text' ] = msg
    elif code == 2:
        status_label.configure(foreground = "red")
        enable_process_buttons()
        enable_commit_buttons()
        status_label[ 'text' ] = msg
    elif code == 4:
        commits_status_label.configure(foreground = "orange")
        disable_commit_buttons()
        commits_status_label[ 'text' ] = msg
    elif code == 5:
        commits_status_label.configure(foreground = "blue")
        enable_commit_buttons()
        commits_status_label[ 'text' ] = msg
    elif code == 6:
        commits_status_label.configure(foreground = "red")
        commits_status_label[ 'text' ] = msg


issue_retrieval_method_var = IntVar()


def get_team_dict_from_csv():
    dict = {}
    file = open(CSV_FILE_NAME + '.csv', 'rU')
    reader = csv.reader(file, dialect=csv.excel_tab)
    for item in reader:
        splt = item[ 0 ].split(",")
        dict[ splt[ 0 ] ] = [ splt[ 1 ], splt[ 2 ] ]
    return dict


# checks we need to consider in commit:
# 1) check if issue reference format is present in the commit
# 2) check if 'what, why, impact' are present in the commit message
def is_commit_format(cmt):
    violation_code = 0
    if (not str(issue_criteria_input.get()).lower() in str(cmt).lower()) \
        and (not str("Merge").lower() in str(cmt).lower()) \
        and (not str("Rebasing").lower() in str(cmt).lower()):
        violation_code = 1
    return violation_code


# this function will return the story points that are assigned to the
# issue passed to the function. The assignment is done in the form of 
# a label on Github in the format '1sp', or '5sp', etc.
def get_sp(issue):
    labels = issue.labels()
    sp_num = 0
    for label in labels:
        if 'sp' in label.name:
            sp_num = int(label.name[ :-2 ])
    return sp_num


def get_assignee_str(issue):
    assignees = issue.assignees
    asg_arr = ''
    count = 0
    for assignee in assignees:
        if count > 0:
            asg_arr += ", "
        asg_arr += str(assignee)
        count += 1
    return str(asg_arr)


# this method assumes that the estimate is provided in the main description
# in the format '4hrs', and that only one estimate is available. If multiple
# estimates are available in the main description, all of the estimates will
# be added up to form the total estimate for the issue / story
def get_issue_estimate(issue):
    hours, notes = parse_comment(issue.body)
    return hours


def gh_login():
    try:
        gh = login(str(username_input.get()), str(password_input.get()))
        repo_check = gh.repositories()
        for repo in repo_check:
            gh_login_success = True
    except Exception as exc:
        update_status_message("Incorrect username / password / repo", 2)
        gh_login_success = False
    return gh_login_success, gh


def commits_email_content(repo, cmt):
    email_sub = "[ commit message violation ] " + \
                str(repo.name) + " " + str(cmt.sha)
    email_msg = "Dear " + str(cmt.author) + \
                ", you have not included the reference to the Github" + \
                " issue in the prescribed format."
    email_msg += "\n\nPlease visit the link below and add the" + \
                 " issue reference in the comment box."
    email_msg += "\n\nCommit URL: " + str(cmt.html_url)
    return email_sub, email_msg


def commits_report():
    gh_login_success, gh = gh_login()
    if gh_login_success:
        def process_commmit_thrd():
            repo = get_repo_by_name(gh, repo_input.get())
            cmt_date = "2018-01-01"
            if commits_date_input.get():
                cmt_date = commits_date_input.get()
            cmts = repo.commits(None, None, None, -1, None, cmt_date, None, None)
            team_dict = get_team_dict_from_csv()
            if team_dict:
                for cmt in cmts:
                    msg = 'Processing, please wait...'
                    update_status_message(msg, 4)
                    violation_code = is_commit_format(cmt.commit.message)
                    if violation_code == 1:
                        if str(cmt.author) in team_dict:
                            author_email = team_dict[ str(cmt.author) ][ 0 ]
                            author_manager = team_dict[ str(cmt.author) ][ 1 ]
                            manager_email = team_dict[ author_manager ][ 0 ]
                            emails_list = list([])
                            emails_list.append(author_email)
                            if manager_email:
                                emails_list.append(manager_email)
                            comments = cmt.comments()
                            comment_adjustment_found = False
                            email_sub, email_msg = commits_email_content(repo, cmt)
                            for cmnt in comments:
                                if (str(issue_criteria_input.get()).lower()
                                        in str(cmnt.body).lower()):
                                    comment_adjustment_found = True
                            if comment_adjustment_found is False:
                                push_email_to_user(commits_sender_email_input.get(),
                                                   commits_sender_pwd_input.get(), emails_list,
                                                   email_sub, email_msg,
                                                   commits_admin_email_input.get(), 6)
                                time.sleep(5.0)
                    elif violation_code == 2:   # something for later
                        pass
                    elif violation_code == 3:   # something for later
                        pass
                    elif violation_code == 4:   # something for later
                        pass
                update_status_message("Commit messages processed!", 5)
            else:
                update_status_message("Unable to process team CSV!", 2)
        t = threading.Thread(target = process_commmit_thrd)
        t.start()


def team_check(issue, team_name):
    team_name = str(team_name).lower()
    labels = issue.labels()
    is_team_issue = False
    for lbl in labels:
        if team_name == str(lbl.name).lower():
            is_team_issue = True
    return is_team_issue


def sprint_report_main():
    if issue_retrieval_method_var.get() == 1:
        if (sprint_override_input.get() != '') and \
                (sprint_weeks_input.get() != '') and \
                (int(sprint_weeks_input.get()) > 0):
            sprint_report()
        else:
            update_status_message("Enter sprint name and weeks count", 2)
    elif issue_retrieval_method_var.get() == 2:
        if (start_date_input.get() != '') and (end_date_input.get() != ''):
            sprint_report()
        else:
            update_status_message("Enter start and end dates", 2)


def sprint_report_preprocess(repo):
    repo_issues = repo.issues(None, 'all')
    sprint_info = None
    bd = None
    terminate = False
    if issue_retrieval_method_var.get() == 1:
        sprint_info = get_curr_sprint_info(repo)
        if sprint_info is None:
            update_status_message("Invalid sprint name!", 2)
            terminate = True
        else:
            bd = Burndown(sprint_info['start-date'], sprint_info['end-date'])
    else:
        if (get_date_from_input(start_date_input.get())) and \
                get_date_from_input(end_date_input.get()):
            bd = Burndown(get_date_from_input(start_date_input.get()),
                          get_date_from_input(end_date_input.get()))
        else:
            update_status_message("Invalid start or end dates!", 2)
            terminate = True
    return repo_issues, sprint_info, bd, terminate


def sprint_report_issue_processor(issue, sprint_info, issues_count_inc,
                                  report_sheet, bd, processed_count):
    msg = 'Processing #' + str(issue.number) + ', please wait...'
    break_out = False
    update_status_message(msg, 1)
    if issue_retrieval_method_var.get() == 1:
        if issue.milestone:
            if sprint_info:
                if issue.milestone == sprint_info['object']:
                    issues_count_inc += 1
                    comments = issue.comments()
                    is_processed = process_comments_and_report(report_sheet,
                                                               issue, comments,
                                                               sprint_info, None,
                                                               None, bd)
                    if is_processed:
                        processed_count += 1
                    if str(isscount_override_input.get()) != '':
                        print(issues_count_inc)
                        if issues_count_inc == int(isscount_override_input.get()):
                            break_out = True
                    else:
                        if issues_count_inc == sprint_info['issue-count']:
                            break_out = True
    elif issue_retrieval_method_var.get() == 2:
        if (start_date_input.get()) and (end_date_input.get()):
            created_start_date = get_date_from_input(start_date_input.get())
            created_end_date = get_date_from_input(end_date_input.get())
            if created_start_date and created_end_date:
                comments = issue.comments()
                if comments:
                    sprint_info = get_sprint_from_issue(issue)
                    is_processed = process_comments_and_report(report_sheet, issue,
                                                               comments, sprint_info,
                                                               created_start_date,
                                                               created_end_date, bd)
                    if is_processed:
                        processed_count += 1
            else:
                update_status_message("Please provide valid dates", 2)
    return break_out, processed_count, issues_count_inc


def sprint_report():
    status_label[ 'text' ] = ''
    status_label.configure(foreground = "red")
    gh_login_success, gh = gh_login()
    if gh_login_success:
        report_sheet = ReportSheet('report')
        arr = [ "Issue", "Assignees", "Status", "St. Pts", "Comment ID", "Author",
                "Sprint", "Estimate", "Actual Hours", "Date", "Comments" ]
        report_sheet.add_data_row(arr)

        def process_thread():
            update_status_message("Processing, please wait...", 1)
            status_label.configure(foreground = "orange")
            repo = get_repo_by_name(gh, repo_input.get())
            if repo:
                repo_issues, sprint_info, bd, terminate = sprint_report_preprocess(repo)
                processed_count = 0
                issues_count_inc = 0
                if terminate is False:
                    for issue in repo_issues:
                        if issue_term_input.get() != '':
                            if int(issue_term_input.get()) > int(issue.number):
                                break
                        process = True
                        if str(team_input.get()) != '':
                            if team_check(issue, team_input.get()):
                                process = True
                            else:
                                process = False
                        if process:
                            break_out, processed_count, issues_count_inc = \
                                sprint_report_issue_processor(issue, sprint_info,
                                                              issues_count_inc,
                                                              report_sheet,
                                                              bd, processed_count)
                            if break_out:
                                break
                if processed_count > 0:
                    bd.post_process()
                    bd.burndown_data_to_sheet_obj(report_sheet)
                    report_sheet.post_process()
                    update_status_message("Sprint report generated!", 0)
                    push_email()
                else:
                    update_status_message("Nothing to process, review criteria", 2)

        t = threading.Thread(target=process_thread)
        t.start()


root.geometry('350x460')
rows = 0
while rows < 50:
    root.rowconfigure(rows, weight=1)
    root.columnconfigure(rows, weight=1)
    rows += 1
style = ttk.Style()
white = "#ffffff"
style.theme_create("test", parent="alt", settings = {
        "TNotebook": { "configure": { "tabmargins": [ 2, 5, 2, 0 ] } },
        "TNotebook.Tab": {
            "configure": { "padding": [ 5, 2 ] },
            "map":       { "expand": [ ("selected", [ 1, 1, 1, 0 ]) ] } } })
style.theme_use("test")
nb = ttk.Notebook(root)
nb.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')
settings_frame = ttk.Frame(nb)
nb.add(settings_frame, text='Settings')
main_frame = ttk.Frame(nb)
nb.add(main_frame, text='Sprint Report')
commits_frame = ttk.Frame(nb)
nb.add(commits_frame, text='Commits Report')
right_margin = Frame(main_frame, width = 20)
right_margin.pack(side = RIGHT)
left_margin = Frame(main_frame, width = 20)
left_margin.pack(side = LEFT)
bot_margin = Frame(main_frame, height = 10)
bot_margin.pack(side = BOTTOM)
top_margin = Frame(main_frame, height = 20)
top_margin.pack(side = TOP)
right_margin = Frame(settings_frame, width = 20)
right_margin.pack(side = RIGHT)
left_margin = Frame(settings_frame, width = 20)
left_margin.pack(side = LEFT)
bot_margin = Frame(settings_frame, height = 10)
bot_margin.pack(side = BOTTOM)
top_margin = Frame(settings_frame, height = 20)
top_margin.pack(side = TOP)
username_container = Frame(settings_frame, width = 30)
username_container.pack()
password_container = Frame(settings_frame, width = 30)
password_container.pack()
repo_container = Frame(settings_frame, width = 30)
repo_container.pack()
username_label = Label(username_container, width=15, height=1,
    text="Github username", anchor='w')
username_label.pack(side = LEFT)
username_input = Entry(username_container, width = 25, borderwidth = 1,
    font = 'Calibri, 12')
username_input.pack(side = RIGHT)
username_input.focus()
sep2 = Frame(main_frame, height = 10)
sep2.pack(side = BOTTOM)
password_label = Label(password_container, width=15, height=1,
    text="Github password", anchor='w')
password_label.pack(side = LEFT)
password_input = Entry(password_container, show='*',width = 25,
    borderwidth = 1, font = 'Calibri, 12')
password_input.pack(side = RIGHT)
repo_label = Label(repo_container, width=15, height=1,
    text="Repository name", anchor='w')
repo_label.pack(side = LEFT)
repo_input = Entry(repo_container, width = 25,
    borderwidth = 1, font = 'Calibri, 12')
repo_input.pack(side = RIGHT)
email_container = Frame(main_frame, width = 30)
email_container.pack()
email_pwd_container = Frame(main_frame, width = 30)
email_pwd_container.pack()
recipent_container = Frame(main_frame, width = 30)
recipent_container.pack()
sep1 = Frame(main_frame, height = 10)
sep1.pack()
radio_butt_frame = Frame(main_frame, width = 30)
radio_butt_frame.pack()
start_date_container = Frame(main_frame, width = 30)
end_date_container = Frame(main_frame, width = 30)
sprint_weeks_container = Frame(main_frame, width = 35)
sprint_override_container = Frame(main_frame, width = 35)
start_date_input = Entry(start_date_container, width = 15, borderwidth = 1,
    font = 'Calibri, 12')
end_date_input = Entry(end_date_container, width = 15, borderwidth = 1,
    font = 'Calibri, 12')
sprint_weeks_input = Entry(sprint_weeks_container, width = 20,
    borderwidth = 1, font = 'Calibri, 12')
sprint_override_input = Entry(sprint_override_container, width = 20,
    borderwidth = 1, font = 'Calibri, 12')


def sprint_toggle_callback():
    start_date_input.config(state='disabled')
    end_date_input.config(state='disabled')
    sprint_weeks_input.config(state = 'normal')
    sprint_override_input.config(state = 'normal')


def date_toggle_callback():
    start_date_input.config(state='normal')
    end_date_input.config(state='normal')
    sprint_weeks_input.config(state = 'disabled')
    sprint_override_input.config(state = 'disabled')


rad1 = Radiobutton(radio_butt_frame, text="Report by sprint",
    variable=issue_retrieval_method_var, value=1, padx = 5, command = sprint_toggle_callback)
rad1.pack(side = LEFT)
rad1.select()
rad2 = Radiobutton(radio_butt_frame, text="Report by dates",
    variable=issue_retrieval_method_var, value=2, padx = 5, command = date_toggle_callback)
rad2.pack(side = LEFT)
sep1 = Frame(main_frame, height = 10)
sep1.pack()
sprint_override_container.pack()
sprint_override_label = Label(sprint_override_container, width = 20,
    height = 1, text="Sprint title", anchor='w')
sprint_override_label.pack(side = LEFT)
sprint_weeks_container.pack()
sprint_weeks_label = Label(sprint_weeks_container, width = 20,
    height = 1, text="Sprint weeks", anchor='w')
sprint_weeks_label.pack(side = LEFT)
start_date_container.pack()
start_date_label = Label(start_date_container, width = 25, height = 1,
    text="Start date [ YYYY-MM-DD ]", anchor='w')
start_date_label.pack(side = LEFT)
start_date_input.pack(side = RIGHT)
end_date_container.pack()
end_date_label = Label(end_date_container, width = 25, height = 1,
    text="End date [ YYYY-MM-DD ]", anchor='w')
end_date_label.pack(side = LEFT)
sprint_override_input.pack(side = RIGHT)
isscount_override_container = Frame(main_frame, width = 35)
isscount_override_container.pack()
isscount_override_label = Label(isscount_override_container, width = 20,
    height = 1, text="Issue count override", anchor='w')
isscount_override_label.pack(side = LEFT)
isscount_override_input = Entry(isscount_override_container, width = 20,
    borderwidth = 1, font = 'Calibri, 12')
isscount_override_input.pack(side = RIGHT)
sprint_weeks_input.insert(0, '2')
sprint_weeks_input.pack(side = RIGHT)
end_date_input.pack(side = RIGHT)
team_container = Frame(main_frame, width = 35)
team_container.pack()
team_label = Label(team_container, width = 20,
    height = 1, text="Filter by team label", anchor='w')
team_label.pack(side = LEFT)
team_input = Entry(team_container, width = 20,
    borderwidth = 1, font = 'Calibri, 12')
team_input.pack(side = RIGHT)

issue_term_container = Frame(main_frame, width = 35)
issue_term_container.pack()
issue_term_label = Label(issue_term_container, width = 20,
    height = 1, text="Terminate at issue #", anchor='w')
issue_term_label.pack(side = LEFT)
issue_term_input = Entry(issue_term_container, width = 20,
    borderwidth = 1, font = 'Calibri, 12')
issue_term_input.pack(side = RIGHT)

status_label = Label(main_frame, width=35, height=1, text="")
status_label.pack(side = BOTTOM)
email_label = Label(email_container, width=15, height=1,
    text="Sender Email", anchor='w')
email_label.pack(side = LEFT)
email_input = Entry(email_container, width = 25, borderwidth = 1,
    font = 'Calibri, 12')
email_input.pack(side = RIGHT)
email_pwd_label = Label(email_pwd_container, width=15, height=1,
    text="Sender Password", anchor='w')
email_pwd_label.pack(side = LEFT)
email_pwd_input = Entry(email_pwd_container, width = 25,
    borderwidth = 1, font = 'Calibri, 12')
email_pwd_input.pack(side = RIGHT)
recipent_label = Label(recipent_container, width=15, height=1,
    text="Recipent Email", anchor='w')
recipent_label.pack(side = LEFT)
recipent_input = Entry(recipent_container, width = 25,
    borderwidth = 1, font = 'Calibri, 12')
recipent_input.pack(side = RIGHT)
sep2 = Frame(main_frame, height = 10)
sep2.pack(side = BOTTOM)
# exit_button = Button(main_frame, width = 35, bd = 2, text="Quit", command = quit)
# exit_button.pack(side = BOTTOM)
sprint_report_button = Button(main_frame, width = 35, bd = 2,
    text="Generate Report", command = sprint_report_main)
sprint_report_button.pack(side = BOTTOM)
# test_button = Button(main_frame, width = 35, bd = 2,
#     text="[ test button ]", command = test_func)
# test_button.pack(side = BOTTOM)
right_margin = Frame(commits_frame, width = 20)
right_margin.pack(side = RIGHT)
left_margin = Frame(commits_frame, width = 20)
left_margin.pack(side = LEFT)
bot_margin = Frame(commits_frame, height = 30)
bot_margin.pack(side = BOTTOM)
top_margin = Frame(commits_frame, height = 20)
top_margin.pack(side = TOP)
sep2 = Frame(commits_frame, height = 10)
sep2.pack(side = BOTTOM)
issue_criteria_container = Frame(commits_frame, width = 30)
issue_criteria_container.pack()
issue_criteria_label = Label(issue_criteria_container, width=15, height=1,
    text="Issue ref. criteria", anchor='w')
issue_criteria_label.pack(side = LEFT)
issue_criteria_input = Entry(issue_criteria_container, width = 25, borderwidth = 1,
    font = 'Calibri, 12')
issue_criteria_input.pack(side = RIGHT)
commits_date_container = Frame(commits_frame, width = 30)
commits_date_container.pack()
commits_date_label = Label(commits_date_container, width = 25, height = 1,
    text="Start date [ YYYY-MM-DD ]", anchor='w')
commits_date_label.pack(side = LEFT)
commits_date_input = Entry(commits_date_container, width = 15, borderwidth = 1,
    font = 'Calibri, 12')
commits_date_input.pack(side = RIGHT)
commits_status_label = Label(commits_frame, width=35, height=1, text="", anchor='w')
commits_status_label.pack(side = BOTTOM)
sep2 = Frame(commits_frame, height = 20)
sep2.pack(side = BOTTOM)
commits_sender_email_container = Frame(commits_frame, width = 30)
commits_sender_email_container.pack()
commits_sender_email_label = Label(commits_sender_email_container, width = 15, height = 1,
    text="Sender Email", anchor='w')
commits_sender_email_label.pack(side = LEFT)
commits_sender_email_input = Entry(commits_sender_email_container, width = 25, borderwidth = 1,
    font = 'Calibri, 12')
commits_sender_email_input.pack(side = RIGHT)
commits_sender_pwd_container = Frame(commits_frame, width = 30)
commits_sender_pwd_container.pack()
commits_sender_pwd_label = Label(commits_sender_pwd_container, width = 15, height = 1,
    text="Sender Password", anchor='w')
commits_sender_pwd_label.pack(side = LEFT)
commits_sender_pwd_input = Entry(commits_sender_pwd_container, width = 25, borderwidth = 1,
    font = 'Calibri, 12')
commits_sender_pwd_input.pack(side = RIGHT)
commits_admin_email_container = Frame(commits_frame, width = 30)
commits_admin_email_container.pack()
commits_admin_email_label = Label(commits_admin_email_container, width = 15, height = 1,
    text="BCC Admin Email", anchor='w')
commits_admin_email_label.pack(side = LEFT)
commits_admin_email_input = Entry(commits_admin_email_container, width = 25, borderwidth = 1,
    font = 'Calibri, 12')
commits_admin_email_input.pack(side = RIGHT)
commits_button = Button(commits_frame, width = 35, bd = 2,
    text="Commit Messages Report", command = commits_report)
commits_button.pack(side = BOTTOM)

start_date_input.config(state='disabled')
end_date_input.config(state='disabled')

root.title("Github Project Reporting")
root.resizable(width = FALSE, height = FALSE)
root.lift()
root.focus()
root.attributes('-topmost',True)
root.after_idle(root.attributes,'-topmost',False)
root.mainloop(0)