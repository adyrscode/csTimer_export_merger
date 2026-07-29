#### BE CAREFUL!
I have not extensively tested this script and there could definitely be bugs still present. **Make sure you back up your files** before committing to a merge.
#### What it does
This script is made to merge multiple csTimer exports files into 1 big file for importing.
It sorts all **unique** solves into events (solves from multiple 3x3 sessions will go into 1 big session).
It sorts all solves in all sessions by **date**.
It ranks sessions based on **solve count**.
It re-calculates and fixes sessionData to be accurate.
It lets the user choose from which file they want to keep their csTimer settings (theme, text size, etc.)
It exports to `merged.json`. This can be imported into csTimer.
#### How to use
Make sure you have python installed.
Before exporting your files from csTimer, make sure that the names you use for your sessions/events are identical across devices. Example: If a session is named "3x3 + Inspection" in file 1, and "15s Inspection 3x3" in file 2, the script will detect them as seperate sessions and will sort the solves into 2 seperate sessions. Make sure to rename 1 to fit the other. This is **capitalization sensitive**.
Put the `merger.py` script in a folder together with your csTimer export files. These should be .txt files, and there should be no other .txt files in the same folder which are not for merging purposes, otherwise the script will attempt to merge them and fail.
Run the script. After it merges all the data, it will prompt you to choose one of your files from which to keep your settings (theme, text size, timer update, etc.), as these can't be merged of course. I recommend re-naming your files so you remember which one to keep your settings from.
