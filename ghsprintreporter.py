from github3 import login
import datetime
import calendar
import re
from string import digits
from string import letters
from openpyxl import Workbook
from openpyxl import load_workbook
from Tkinter import *
import ttk
import time
import threading

root = Tk()
canvas_height = 400
canvas_width = 600

# verify that the milestone assigned to the issue is in the on-going sprint
# this will be done by getting the current sprint, extracting the date from
# the current sprint, and comparing against milestone assigned to the issue
def verify_milestone( issue, repo ):
    is_within_sprint = False
    is_month_valid = False
    is_date_valid = False
    curr_sprint = ''
    sprint_due_date = None
    open_stones = repo.milestones( 'open' )
    for stone in open_stones:
        if ( 'Sprint' in str( stone ) ):
            curr_sprint = str( stone )
            if ( stone.due_on ):
                sprint_due_date = stone.due_on.date()
    curr_date = datetime.date.today()
    if ( curr_date <= sprint_due_date ):
        is_within_sprint = True
    else:
        is_within_sprint = False
    return is_within_sprint

def get_repo_by_index( gh, index ):
    repos = gh.repositories()
    reparr = [ ]
    repo_index = 0
    for repo in repos:
        reparr.append( repo )
    return reparr[ index ]

def get_repo_by_name( gh, name ):
    repos = gh.repositories()
    reparr = [ ]
    count = 0
    repo_index = 0
    ret_repo = None
    for repo in repos:
        if ( repo.name == name ):
            ret_repo = repo
    return ret_repo

# this will return a dictionary containing the actual sprint object,
# the number of issues within the sprint, and the due date.
def get_curr_sprint_info( repo ):
    curr_sprint = None
    open_stones = repo.milestones( 'open' )
    closed_stones = repo.milestones( 'closed' )
    criteria = 'Sprint'
    if ( sprint_override_input.get() != '' ):
        criteria = sprint_override_input.get()
    for stone in open_stones:
        if ( criteria in str( stone ) ):
            curr_sprint = stone
    for stone in closed_stones:
        if ( criteria in str( stone ) ):
            curr_sprint = stone
    sprint_issues_count = curr_sprint.open_issues_count + \
        curr_sprint.closed_issues_count
    sprint_end_date = curr_sprint.due_on.date()
    sprint_info = { 'object': curr_sprint, 'issue-count': sprint_issues_count, \
        'end-date': sprint_end_date }
    return sprint_info

def is_date_within_sprint( sprint_info, verify_date ):
    if ( verify_date <= sprint_info[ 'end-date' ] ):
        return True
    else:
        return False

def is_date_within_range( start_date, end_date, verify_date ):
    if ( verify_date >= start_date ) and ( verify_date <= end_date ):
        return True
    else:
        return False

def get_date_from_input( date_str ):
    date_year = int( date_str[ 0:4 ] )
    date_month = int( date_str[ 5:7 ] )
    date_day = int( date_str[ 8:10 ] )
    created_date = datetime.date( date_year, date_month, date_day )
    if ( type( created_date ) == datetime.date ):
        return created_date
    else:
        return None

# returns the github username of the person who made the comment
# on the sprint issue
def get_comment_author( comment ):
    author = comment.user
    return author

# hours can be written as a part of the comment body as
# '8hrs' or '8 hrs' or even '8 hours'. the numeric value
# will be extracted and recorded for the resource against
# the issue, along with additional development notes provided
# inside the issue. how cool is that?
def parse_comment( text ):
    data = [ None, None ]
    loc = None
    full_hours_text = ''
    splt = text.split( ' ' )
    breakout = False
    for item in splt:
        if ( breakout == False ):
            if ( 'hrs' in item ):
                splt_yet_again = item.split( "\n" )
                for sub_item in splt_yet_again:
                    if ( 'hrs' in sub_item ):
                        loc = sub_item.find( 'hrs' )
                        full_hours_text = str( sub_item )
                        breakout = True
                        break
    if ( loc != None ):
        prefix_cleaned = full_hours_text[ :-3 ]
        prefix_cleaned = prefix_cleaned.translate( None, letters )
        if ( prefix_cleaned.isdigit() ):
            data[ 0 ] = int( prefix_cleaned )
            data[ 1 ] = text.split( full_hours_text )[ 1 ]
    return data

# need to check whether the comment we are processing for hours
# has already has its hours recorded in the Google Sheet. this
# will be done by checking the comment ID against the ID column
# in the sheet for the current sprint.
def comment_id_check( gs, comment ):
    pass

# write information passed through the array into the xlsx
def process_sheet( ws, wb, arr, sheet_data_arr ):
    ws.append( arr )
    sheet_data_arr.append( arr )
    wb.save( 'lifeprint-reporting.xlsx' )
    return sheet_data_arr

def is_item_in_sheet_test( sheet_data_arr, item, col_num ):
    return False

def is_item_in_sheet( sheet_data_arr, item, col_num ):
    found = False
    rownum = 1
    inc = 0
    if ( sheet_data_arr ):
        for row in sheet_data_arr:
            if ( row[ col_num ] == item ):
                print( item )
                found = True
                break
    return found

# function checks whether an issue within the sprint or the date range
# has comments or not, then parses any available comments to check for
# hours which are appended to the worksheet array as well as the sheet
# itself.
def process_comments_and_report( ws, wb, sheet_data_arr, issue, comments, \
        sprint_info = None, start_date = None, end_date = None ):
    processed_count = 0
    cmnt_count = 0
    some_hours_found = False
    for comment in comments:
        cmnt_count += 1
        comment_body = comment.body
        hours, notes = parse_comment( comment_body )
        if ( hours != None ):
            some_hours_found = True
    if ( cmnt_count > 0 ) and ( some_hours_found ):
        for comment in comments:
            comment_date = comment.created_at.date()
            process = False
            sprint_obj_title = None
            if ( sprint_info ):
                if ( is_date_within_sprint( sprint_info, comment_date ) ):
                    process = True
            elif ( start_date ) and ( end_date ):
                if ( is_date_within_range( start_date, end_date, comment_date ) ):
                    process = True
            if ( process ):
                comment_body = comment.body
                comment_id = comment.id
                hours, notes = parse_comment( comment_body )
                if ( hours != None ):
                    if ( not is_item_in_sheet( sheet_data_arr, comment_id, 1 ) ):
                        if ( sprint_info ):
                            sprint_obj_title = sprint_info[ 'object' ].title
                        arr = [ issue.number, comment_id, str( comment.user ), \
                            sprint_obj_title, hours, comment_date, \
                            notes ]
                        sheet_data_arr = process_sheet( ws, wb, arr, sheet_data_arr )
                        processed_count += 1
    else:
        # put the issue in the list anyway even if it doesn't have any comments
        if ( sprint_info ):
            if ( not is_item_in_sheet( sheet_data_arr, issue.number, 0 ) ):
                arr = [ issue.number, None, None, None, \
                    None, None, None ]
                sheet_data_arr = process_sheet( ws, wb, arr, sheet_data_arr )
                processed_count += 1
    if ( processed_count > 0 ):
        return True, sheet_data_arr
    else:
        return False, sheet_data_arr
            
def planning_report():
    pass

def disable_process_buttons():
    sprint_report_button.config( state='disabled' )
    # planning_report_button.config( state='disabled' )
    # commits_report_button.config( state='disabled' )

def enable_process_buttons():
    sprint_report_button.config( state='normal' )
    # planning_report_button.config( state='normal' )
    # commits_report_button.config( state='normal' )

def update_status_message( msg, code = 0 ):
    if ( code == 0 ):
        status_label.configure( foreground = "blue" )
        enable_process_buttons()
    elif ( code == 1 ):
        status_label.configure( foreground = "orange" )
        disable_process_buttons()
    elif( code == 2 ):
        status_label.configure( foreground = "red" )
        enable_process_buttons()
    status_label[ 'text' ] = msg

issue_retrieval_method_var = IntVar()

# checks we need to consider in commit:
# 1) check if pcosgrove/Lifeprint#999 format is present in the commit
# 2) check if 'what, why, impact' are present in the commit message
# 3) 
def is_commit_format( cmt ):
    pass

# this function will return the story points that are assigned to the
# issue passed to the function. The assignment is done in the form of 
# a label on Github in the format '1sp', or '5sp', etc.
def get_sp( issue ):
    pass

def process_commits():
    gh = None
    gh = login( str( username_input.get() ), str( password_input.get() ) )
    # wb = Workbook()
    # ws = wb.active
    if ( gh ):
        try:
            def process_commmit_thrd():
                repo = get_repo_by_name( gh, repo_input.get() )
                cmts = repo.commits()
                for cmt in cmts:
                    cmt = cmt.commit.message
                    violation_code = is_commit_format( cmt )
                    if ( violation_code == 1 ):
                        pass
                    elif ( violation_code == 2 ):
                        pass
                    elif ( violation_code == 3 ):
                        pass
                    elif ( violation_code == 4 ):
                        pass
            t = threading.Thread( target = process_commmit_thrd )
            t.start()
        except Exception as exc:
            update_status_message( "Incorrect username / password / repo", 2 )

def sprint_report():
    status_label[ 'text' ] = ''
    status_label.configure( foreground = "red" )
    gh = None
    gh = login( str( username_input.get() ), str( password_input.get() ) )
    wb = Workbook()
    ws = wb.active
    wb.save( 'lifeprint-reporting.xlsx' )
    sheet_data_arr = [] # spreadsheet data internal container for checking duplicates
    if ( gh ):
        def process_thread():
            try:
                update_status_message( "Processing, please wait...", 1 )
                status_label.configure( foreground = "orange" )
                repo = get_repo_by_name( gh, repo_input.get() )
                repo_issues = repo.issues( None, 'all' )
                sprint_info = get_curr_sprint_info( repo )
                issues_count_inc = 0
                is_processed = False
                processed_count = 0
                for issue in repo_issues:
                    msg = 'Processing #' + str( issue.number ) + ', please wait...'
                    update_status_message( msg, 1 )
                    parent_issue = None # to be worked on later
                    if ( issue_retrieval_method_var.get() == 1 ):
                        if ( issue.milestone ):
                            if ( issue.milestone == sprint_info[ 'object' ] ):
                                issues_count_inc += 1
                                comments = issue.comments()
                                is_processed = process_comments_and_report( ws, wb, \
                                    sheet_data_arr, issue, comments, sprint_info, None, None )
                                if ( is_processed ):
                                    processed_count += 1
                                if ( issues_count_inc == sprint_info[ 'issue-count' ] ):
                                    break
                    elif ( issue_retrieval_method_var.get() == 2 ):
                        if ( start_date_input.get() ) and ( end_date_input.get() ):
                            created_start_date = get_date_from_input( start_date_input.get() )
                            created_end_date = get_date_from_input( end_date_input.get() )
                            if ( created_start_date ) and ( created_end_date ):
                                comments = issue.comments()
                                if ( comments ):
                                    is_processed = process_comments_and_report( ws, wb, \
                                        sheet_data_arr, issue, comments, None, \
                                        created_start_date, created_end_date )
                                    if ( is_processed ):
                                        processed_count += 1
                            else:
                                update_status_message( "Please provide valid dates", 2 )
                if ( is_processed > 0 ):
                    update_status_message( "Sprint report generated!", 0 )
                else:
                    update_status_message( "Nothing to process, review criteria", 2 )
            except Exception as exc:
                update_status_message( "Incorrect username / password / repo", 2 )      
        t = threading.Thread( target=process_thread )
        t.start()
    else:
        update_status_message( "Enter valid username / password / repo", 2 )

main_frame = Frame(root, width = 30, bd = 2, relief = GROOVE)
main_frame.pack()
right_margin = Frame(main_frame, width = 20)
right_margin.pack(side = RIGHT)
left_margin = Frame(main_frame, width = 20)
left_margin.pack(side = LEFT)
bot_margin = Frame(main_frame, height = 10)
bot_margin.pack(side = BOTTOM)
top_margin = Frame(main_frame, height = 20)
top_margin.pack(side = TOP)
username_container = Frame( main_frame, width = 30 )
username_container.pack()
password_container = Frame( main_frame, width = 30 )
password_container.pack()
repo_container = Frame( main_frame, width = 30 )
repo_container.pack()
sep1 = Frame(main_frame, height = 10)
sep1.pack()
radio_butt_frame = Frame(main_frame, width = 30)
radio_butt_frame.pack()
rad1 = Radiobutton(radio_butt_frame, text="Report by curr. sprint", \
    variable=issue_retrieval_method_var, value=1, padx = 5)
rad1.pack(side = LEFT)
rad1.select()
rad2 = Radiobutton(radio_butt_frame, text="Report by dates", \
    variable=issue_retrieval_method_var, value=2, padx = 5)
rad2.pack(side = LEFT)
sep1 = Frame(main_frame, height = 10)
sep1.pack()
sprint_override_container = Frame( main_frame, width = 30 )
sprint_override_container.pack()
sprint_override_label = Label(sprint_override_container, width = 15, height = 1, \
    text="Sprint override")
sprint_override_label.pack(side = LEFT)
sprint_override_input = Entry(sprint_override_container, width = 25, borderwidth = 1, \
    font = 'Calibri, 12')
sprint_override_input.pack(side = RIGHT)
sep1 = Frame(main_frame, height = 5)
sep1.pack()
start_date_container = Frame( main_frame, width = 30 )
start_date_container.pack()
start_date_label = Label(start_date_container, width = 25, height = 1, \
    text="Start date [ YYYY-MM-DD ]")
start_date_label.pack(side = LEFT)
start_date_input = Entry(start_date_container, width = 15, borderwidth = 1, \
    font = 'Calibri, 12')
start_date_input.pack(side = RIGHT)
sep1 = Frame(main_frame, height = 5)
sep1.pack()
end_date_container = Frame( main_frame, width = 30 )
end_date_container.pack()
end_date_label = Label(end_date_container, width = 25, height = 1, \
    text="End date [ YYYY-MM-DD ]")
end_date_label.pack(side = LEFT)
end_date_input = Entry(end_date_container, width = 15, borderwidth = 1, \
    font = 'Calibri, 12')
end_date_input.pack(side = RIGHT)
sep1 = Frame(main_frame, height = 5)
sep1.pack()
status_label = Label(main_frame, width=35, height=1, text="")
status_label.pack(side = BOTTOM)
username_label = Label(username_container, width=15, height=1, \
    text="Github username")
username_label.pack(side = LEFT)
username_input = Entry(username_container, width = 25, borderwidth = 1, \
    font = 'Calibri, 12')
username_input.pack(side = RIGHT)
username_input.focus()
sep2 = Frame(main_frame, height = 10)
sep2.pack(side = BOTTOM)
password_label = Label(password_container, width=15, height=1, \
    text="Github password")
password_label.pack(side = LEFT)
password_input = Entry(password_container, show='*',width = 25, \
    borderwidth = 1, font = 'Calibri, 12')
password_input.pack(side = RIGHT)
sep2 = Frame(main_frame, height = 10)
sep2.pack(side = BOTTOM)
repo_label = Label(repo_container, width=15, height=1, \
    text="Repository name")
repo_label.pack(side = LEFT)
repo_input = Entry(repo_container, width = 25, \
    borderwidth = 1, font = 'Calibri, 12')
repo_input.pack(side = RIGHT)
exit_button = Button(main_frame, width = 35, bd = 2, text="Quit", command = quit)
exit_button.pack(side = BOTTOM)
# planning_report_button = Button(main_frame, width = 35, bd = 2, \
#     text="Generate Planned Items List", command = planning_report)
# planning_report_button.pack(side = BOTTOM)
# commits_report_button = Button(main_frame, width = 35, bd = 2, \
#     text="Commits Report", command = process_commits)
# commits_report_button.pack(side = BOTTOM)
sprint_report_button = Button(main_frame, width = 35, bd = 2, \
    text="Generate Report", command = sprint_report)
sprint_report_button.pack(side = BOTTOM)
root.title("Github Project Reporting")
root.resizable(width = FALSE, height = FALSE)
root.lift()
root.focus()
root.attributes('-topmost',True)
root.after_idle(root.attributes,'-topmost',False)
root.mainloop(0)