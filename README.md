# gh_sprint_report
This is a minimal Github to .xlsx reporting tool to track sprint activity that uses github3.py

This tool assumes that Github Milestones are being used as Sprints, with the title of the Sprint Milestone in the format:

[ Sprint ] 23rd April

The end date for the Sprint also needs to be defined in the Milestone settings prior to using this tool.

Issues need to be assigned those Milestones to be considered within a sprint. The tool will only write information for issues in the .xlsx which are within the end date for the Sprint.

Developers are required to log their hours for each issue every day of the sprint in the format inside the issue comment box:

8hrs

The developer can also add dev. notes in their comment which the tool will parse and write to the .xlsx separately. Although repeated entry of hours by the developer in the comments section for an issue can clutter the feed, it would make more sense to have dev. notes added along with the work time log as well to update the team about daily progress on a story.

Hour estaimtes can be added in the issue's main description in the same format as above. These will be used to populate burndown ideal graph in the final sprint report.

**PRE-REQUISITES**

Prior to using this tool, make sure you get github3.py and openpyxl using the following pip commands:

```pip install github3.py```
```pip install openpyxl```

In addition to that, your Github issue management needs to follow these guidelines in order to ensure effective use of this tool:

- Sprints need to be created as Github Milestones in exactly this format: [ Sprint ] 6th August.
- Issues must be assigned to this milestone / sprint in order for them to be counted as a part of the sprint.
- For hour based burndown reporting and effort tracking, estimates need to be added in the issue main description as '16hrs'. You can add any number of estimates in the main description if there are multiple components within the story, the program will automatically add them all up to form one single estimate that will be reported in the final report.
- Again, for the hourly burndown to work, developers need to log their work done in the form of hours as '4hrs' as a comment for the issue.
- Story Point estimates need to have labels pre-defined as 1sp. 2sp, 3sp, 5sp, etc. These labels should be applied to the issue in order for them to be incorporated in the report.
- You have the option to use a label that would differentiate the issues between teams in order to generate report based on a particular label only.

**REPORTING**

This tool outputs a report.xlsx file which has information about the work done by sprint or by date range in the following format:

Issue | Assignees | Status | St. Pts | Comment ID | Author | Sprint | Hours Est. | Actual Hours | Date | Comments

- 'Issue' contains the Github issue number for the story the developer(s) has been working on.
- 'Assignees' can be multiple and all are mentioned in this cell in the report sheet.
- 'Status' is either open or closed. This is most useful to track stories completed within a sprint.
- 'St. Pts' is the story point estimate that is added as a label to the issue.
- 'Comment ID' is the unique identifier for the comment in which the developer has added their work hours. Note that each row in the report corresponds to a unique comment in a particular issue, which means that there can be multiple entries in the reprot for a single issue depending on the number of work hour comments.
- 'Sprint' is the name of the sprint (Github milestone) that the issue has been assigned.
- 'Hours Est.' is the actual estimate hours as mentioned in the issue's main description in the formed described earler.
- 'Actual Hours' is the sum of the main hours for the story.
- 'Date' is the date when the work log comment was added.
- 'Comments' can be used to manually add any comments after the report has been generated.

The tool allows report generation for the following cases:

- Report by Sprint
- Report by Dates

A toggle allows changing between the above options. Reporting by sprint reports only those issues that have been assigned the sprint milestone, whereas report by dates will include all those issues that have a valid work hour log comment added by the developer within the date range specified. The latter can be useful when you need to track what the developers have been working on other than the issues in the sprint, however it can be slower in processing since the program would need to traverse across the entire issue list in the repository to check for comments added within the dates specified.

Other additional options in the sprint reporting tab of the app allow specification of the team label filter, a count overried which terminates traversing over issues when a specified number is reached, and a break in processing when the specified issue number has been reached as the program traverses backwards from the latest issue number.

**BURNDOWN**

The burndown / burnup functionality currently allows reporting of hours based burndown and burnup in a separate 'Burndown' tab in the report.xlsx sheet in the following format:

Ideal | Burndown | Burnup

- The 'Ideal' column is a gradual decrement of the total estimated hours which is a sum of the estimates for all issues traversed in the report.
- The 'Burndown' is a decrement of the total estimate based on the hours that developers log against their stories daily.
- 'Burnup' is an accumulation of the daily work hours.

The data added under these columns can be directly used to create burndown and burnup plots using standard spreadsheet tools for visualization. Currently this process is not automated and the plots need to be manually created by the user of this tool.


