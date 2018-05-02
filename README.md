# gh_sprint_report
This is a minimal Github to .xlsx reporting tool to track sprint activity that uses github3.py

This tool assumes that Github Milestones are being used as Sprints, with the title of the Sprint Milestone in the format:

[ Sprint ] 23rd April

The end date for the Sprint also needs to be defined in the Milestone settings prior to using this tool.

Issues need to be assigned those Milestones to be considered within a sprint. The tool will only write information for issues in the .xlsx which are within the end date for the Sprint.

Developers are required to log their hours for each issue every day of the sprint in the format inside the issue comment box:

8hrs

The developer can also add dev. notes in their comment which the tool will parse and write to the .xlsx separately.

UPCOMING DEVELOPMENT:

- Burndown charts
- Sprint selection
- Commits tracking
