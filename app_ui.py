from Tkinter import *
import ttk
import ghsprintreporter


def disable_process_buttons(sprint_report_button):
    sprint_report_button.config(state='disabled')


def enable_process_buttons(sprint_report_button):
    sprint_report_button.config(state='normal')


def disable_commit_buttons(commits_button):
    commits_button.config(state='disabled')


def enable_commit_buttons(commits_button):
    commits_button.config(state='normal')


def update_status_message(msg, ui_obj, code=0):
    if code == 0:
        ui_obj.status_label.configure(foreground="blue")
        enable_process_buttons(ui_obj.sprint_report_button)
        ui_obj.status_label['text'] = msg
    elif code == 1:
        ui_obj.status_label.configure(foreground="orange")
        disable_process_buttons(ui_obj.sprint_report_button)
        ui_obj.status_label['text'] = msg
    elif code == 2:
        ui_obj.status_label.configure(foreground="red")
        enable_process_buttons(ui_obj.sprint_report_button)
        enable_commit_buttons(ui_obj.commits_button)
        ui_obj.status_label['text'] = msg
    elif code == 4:
        ui_obj.commits_status_label.configure(foreground="orange")
        disable_commit_buttons(ui_obj.commits_button)
        ui_obj.commits_status_label['text'] = msg
    elif code == 5:
        ui_obj.commits_status_label.configure(foreground="blue")
        enable_commit_buttons(ui_obj.commits_button)
        ui_obj.commits_status_label['text'] = msg
    elif code == 6:
        ui_obj.commits_status_label.configure(foreground="red")
        ui_obj.commits_status_label['text'] = msg


class SprintReporterApp:

    def sprint_toggle_callback(self):
        self.start_date_input.config(state='disabled')
        self.end_date_input.config(state='disabled')
        self.sprint_weeks_input.config(state='normal')
        self.sprint_override_input.config(state='normal')

    def date_toggle_callback(self):
        self.start_date_input.config(state='normal')
        self.end_date_input.config(state='normal')
        self.sprint_weeks_input.config(state='disabled')
        self.sprint_override_input.config(state='disabled')

    def __init__(self):
        self.root = Tk()
        self.root.geometry('350x460')
        rows = 0
        while rows < 50:
            self.root.rowconfigure(rows, weight=1)
            self.root.columnconfigure(rows, weight=1)
            rows += 1
        style = ttk.Style()
        style.theme_create("test", parent="alt", settings={
                "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
                "TNotebook.Tab": {
                    "configure": {"padding": [5, 2]},
                    "map":       {"expand": [("selected", [1, 1, 1, 0])]}}})
        self.issue_retrieval_method_var = IntVar()
        style.theme_use("test")
        nb = ttk.Notebook(self.root)
        nb.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')
        settings_frame = ttk.Frame(nb)
        nb.add(settings_frame, text='Settings')
        main_frame = ttk.Frame(nb)
        nb.add(main_frame, text='Sprint Report')
        commits_frame = ttk.Frame(nb)
        nb.add(commits_frame, text='Commits Report')
        right_margin = Frame(main_frame, width=20)
        right_margin.pack(side=RIGHT)
        left_margin = Frame(main_frame, width=20)
        left_margin.pack(side=LEFT)
        bot_margin = Frame(main_frame, height=10)
        bot_margin.pack(side=BOTTOM)
        top_margin = Frame(main_frame, height=20)
        top_margin.pack(side=TOP)
        right_margin = Frame(settings_frame, width=20)
        right_margin.pack(side=RIGHT)
        left_margin = Frame(settings_frame, width=20)
        left_margin.pack(side=LEFT)
        bot_margin = Frame(settings_frame, height=10)
        bot_margin.pack(side=BOTTOM)
        top_margin = Frame(settings_frame, height=20)
        top_margin.pack(side=TOP)
        username_container = Frame(settings_frame, width=30)
        username_container.pack()
        password_container = Frame(settings_frame, width=30)
        password_container.pack()
        repo_container = Frame(settings_frame, width=30)
        repo_container.pack()
        username_label = Label(username_container, width=15, height=1,
                               text="Github username", anchor='w')
        username_label.pack(side=LEFT)
        self.username_input = Entry(username_container, width=25, borderwidth=1,
                                    font='Calibri, 12')
        self.username_input.pack(side=RIGHT)
        self.username_input.focus()
        sep2 = Frame(main_frame, height=10)
        sep2.pack(side=BOTTOM)
        password_label = Label(password_container, width=15, height=1,
                               text="Github password", anchor='w')
        password_label.pack(side=LEFT)
        self.password_input = Entry(password_container, show='*', width=25,
                                    borderwidth=1, font='Calibri, 12')
        self.password_input.pack(side=RIGHT)
        repo_label = Label(repo_container, width=15, height=1,
                           text="Repository name", anchor='w')
        repo_label.pack(side=LEFT)
        self.repo_input = Entry(repo_container, width=25,
                                borderwidth=1, font='Calibri, 12')
        self.repo_input.pack(side=RIGHT)
        email_container = Frame(main_frame, width=30)
        email_container.pack()
        email_pwd_container = Frame(main_frame, width=30)
        email_pwd_container.pack()
        recipent_container = Frame(main_frame, width=30)
        recipent_container.pack()
        sep1 = Frame(main_frame, height=10)
        sep1.pack()
        radio_butt_frame = Frame(main_frame, width=30)
        radio_butt_frame.pack()
        start_date_container = Frame(main_frame, width=30)
        end_date_container = Frame(main_frame, width=30)
        sprint_weeks_container = Frame(main_frame, width=35)
        sprint_override_container = Frame(main_frame, width=35)
        self.start_date_input = Entry(start_date_container, width=15, borderwidth=1,
                                      font='Calibri, 12')
        self.end_date_input = Entry(end_date_container, width=15, borderwidth=1,
                                    font='Calibri, 12')
        self.sprint_weeks_input = Entry(sprint_weeks_container, width=20,
                                        borderwidth=1, font='Calibri, 12')
        self.sprint_override_input = Entry(sprint_override_container, width=20,
                                           borderwidth=1, font='Calibri, 12')
        rad1 = Radiobutton(radio_butt_frame, text="Report by sprint",
                           variable=self.issue_retrieval_method_var,
                           value=1, padx=5, command=self.sprint_toggle_callback)
        rad1.pack(side=LEFT)
        rad1.select()
        rad2 = Radiobutton(radio_butt_frame, text="Report by dates",
                           variable=self.issue_retrieval_method_var,
                           value=2, padx=5, command=self.date_toggle_callback)
        rad2.pack(side=LEFT)
        sep1 = Frame(main_frame, height=10)
        sep1.pack()
        sprint_override_container.pack()
        sprint_override_label = Label(sprint_override_container, width=20,
                                      height=1, text="Sprint title", anchor='w')
        sprint_override_label.pack(side=LEFT)
        sprint_weeks_container.pack()
        sprint_weeks_label = Label(sprint_weeks_container, width=20,
                                   height=1, text="Sprint weeks", anchor='w')
        sprint_weeks_label.pack(side=LEFT)
        start_date_container.pack()
        start_date_label = Label(start_date_container, width=25, height=1,
                                 text="Start date [YYYY-MM-DD]", anchor='w')
        start_date_label.pack(side=LEFT)
        self.start_date_input.pack(side=RIGHT)
        end_date_container.pack()
        end_date_label = Label(end_date_container, width=25, height=1,
                               text="End date [YYYY-MM-DD]", anchor='w')
        end_date_label.pack(side=LEFT)
        self.sprint_override_input.pack(side=RIGHT)
        isscount_override_container = Frame(main_frame, width=35)
        isscount_override_container.pack()
        isscount_override_label = Label(isscount_override_container, width=20,
                                        height=1, text="Issue count override", anchor='w')
        isscount_override_label.pack(side=LEFT)
        self.isscount_override_input = Entry(isscount_override_container, width=20,
                                             borderwidth=1, font='Calibri, 12')
        self.isscount_override_input.pack(side=RIGHT)
        self.sprint_weeks_input.insert(0, '2')
        self.sprint_weeks_input.pack(side=RIGHT)
        self.end_date_input.pack(side=RIGHT)
        team_container = Frame(main_frame, width=35)
        team_container.pack()
        team_label = Label(team_container, width=20,
                           height=1, text="Filter by team label", anchor='w')
        team_label.pack(side=LEFT)
        self.team_input = Entry(team_container, width=20,
                                borderwidth=1, font='Calibri, 12')
        self.team_input.pack(side=RIGHT)
        issue_term_container = Frame(main_frame, width=35)
        issue_term_container.pack()
        issue_term_label = Label(issue_term_container, width=20,
                                 height=1, text="Terminate at issue #", anchor='w')
        issue_term_label.pack(side=LEFT)
        self.issue_term_input = Entry(issue_term_container, width=20,
                                      borderwidth=1, font='Calibri,12')
        self.issue_term_input.pack(side=RIGHT)

        self.status_label = Label(main_frame, width=35, height=1, text="")
        self.status_label.pack(side=BOTTOM)
        email_label = Label(email_container, width=15, height=1,
                            text="Sender Email", anchor='w')
        email_label.pack(side=LEFT)
        self.email_input = Entry(email_container, width=25, borderwidth=1,
                                 font='Calibri, 12')
        self.email_input.pack(side=RIGHT)
        email_pwd_label = Label(email_pwd_container, width=15, height=1,
                                text="Sender Password", anchor='w')
        email_pwd_label.pack(side=LEFT)
        email_pwd_input = Entry(email_pwd_container, width=25,
                                borderwidth=1, font='Calibri, 12')
        email_pwd_input.pack(side=RIGHT)
        recipent_label = Label(recipent_container, width=15, height=1,
                               text="Recipent Email", anchor='w')
        recipent_label.pack(side=LEFT)
        self.recipent_input = Entry(recipent_container, width=25,
                                    borderwidth=1, font='Calibri, 12')
        self.recipent_input.pack(side=RIGHT)
        sep2 = Frame(main_frame, height=10)
        sep2.pack(side=BOTTOM)
        self.commits_button = Button(commits_frame, width=35, bd=2, text="Commit Messages Report")
        self.sprint_report_button = Button(main_frame, width=35, bd=2, text="Generate Report")
        self.sprint_report_button.configure(command=lambda: ghsprintreporter.sprint_report_main(self))
        self.sprint_report_button.pack(side=BOTTOM)
        right_margin = Frame(commits_frame, width=20)
        right_margin.pack(side=RIGHT)
        left_margin = Frame(commits_frame, width=20)
        left_margin.pack(side=LEFT)
        bot_margin = Frame(commits_frame, height=30)
        bot_margin.pack(side=BOTTOM)
        top_margin = Frame(commits_frame, height=20)
        top_margin.pack(side=TOP)
        sep2 = Frame(commits_frame, height=10)
        sep2.pack(side=BOTTOM)
        issue_criteria_container = Frame(commits_frame, width=30)
        issue_criteria_container.pack()
        issue_criteria_label = Label(issue_criteria_container, width=15, height=1,
                                     text="Issue ref. criteria", anchor='w')
        issue_criteria_label.pack(side=LEFT)
        self.issue_criteria_input = Entry(issue_criteria_container, width=25, borderwidth=1,
                                          font='Calibri, 12')
        self.issue_criteria_input.pack(side=RIGHT)
        commits_date_container = Frame(commits_frame, width=30)
        commits_date_container.pack()
        commits_date_label = Label(commits_date_container, width=25, height=1,
                                   text="Start date [YYYY-MM-DD]", anchor='w')
        commits_date_label.pack(side=LEFT)
        self.commits_date_input = Entry(commits_date_container, width=15, borderwidth=1,
                                        font='Calibri, 12')
        self.commits_date_input.pack(side=RIGHT)
        self.commits_status_label = Label(commits_frame, width=35, height=1, text="", anchor='w')
        self.commits_status_label.pack(side=BOTTOM)
        sep2 = Frame(commits_frame, height=20)
        sep2.pack(side=BOTTOM)
        commits_sender_email_container = Frame(commits_frame, width=30)
        commits_sender_email_container.pack()
        commits_sender_email_label = Label(commits_sender_email_container, width=15, height=1,
                                           text="Sender Email", anchor='w')
        commits_sender_email_label.pack(side=LEFT)
        self.commits_sender_email_input = Entry(commits_sender_email_container, width=25, borderwidth=1,
                                                font='Calibri, 12')
        self.commits_sender_email_input.pack(side=RIGHT)
        commits_sender_pwd_container = Frame(commits_frame, width=30)
        commits_sender_pwd_container.pack()
        commits_sender_pwd_label = Label(commits_sender_pwd_container, width=15, height=1,
                                         text="Sender Password", anchor='w')
        commits_sender_pwd_label.pack(side=LEFT)
        self.commits_sender_pwd_input = Entry(commits_sender_pwd_container, width=25, borderwidth=1,
                                              font='Calibri, 12')
        self.commits_sender_pwd_input.pack(side=RIGHT)
        commits_admin_email_container = Frame(commits_frame, width=30)
        commits_admin_email_container.pack()
        commits_admin_email_label = Label(commits_admin_email_container, width=15, height=1,
                                          text="BCC Admin Email", anchor='w')
        commits_admin_email_label.pack(side=LEFT)
        self.commits_admin_email_input = Entry(commits_admin_email_container, width=25, borderwidth=1,
                                               font='Calibri, 12')
        self.commits_admin_email_input.pack(side=RIGHT)
        self.commits_button.configure(command=lambda: ghsprintreporter.commits_report(self))
        self.commits_button.pack(side=BOTTOM)

        self.start_date_input.config(state='disabled')
        self.end_date_input.config(state='disabled')

        self.root.title("Github Project Reporting")
        self.root.resizable(width=FALSE, height=FALSE)
        self.root.lift()
        self.root.focus()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)


if __name__ == "__main__":
    app = SprintReporterApp()
    app.root.mainloop(0)

