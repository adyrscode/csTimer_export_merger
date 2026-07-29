from pathlib import Path
import json

files = []

# look for .txt files in script dir
script_dir = Path(__file__).parent
for file in script_dir.iterdir():
    if file.name.endswith(".txt"):
        files.append(file.name)
print("Found files:",files)

all_dates = {} # dict of all dates by any solve, for fast lookup
all_properties = []
sessions_by_event = {} # initial sorting of solves per event
sorted_sessions = {} # final sessions, sorted by count for rank, and by date for solve.

def main():
    for file_num, file in enumerate(files):
        with open(files[file_num], "r") as file:
            print("Starting file:",files[file_num])
            data = json.load(file)

            # let's get properties (user settings) out of the way first
            session_data = json.loads(data["properties"]["sessionData"])
            properties = data["properties"]
            properties.pop("sessionData")
            all_properties.append([files[file_num], properties])

            # go through sessions and sort into events
            sesh_num = 0
            for session in data:
                sesh_num += 1
                if (len(data[session]) != 0) and (session != "properties"):
                    print("Starting",session,"in file",files[file_num])
                    parse_session(data[session], str(sesh_num), session_data)
                else:
                    print(session, "is empty or irrelevant")

    # sort solves per event by date
    counts = [] # [[21343, '3x3']]
    for event in sessions_by_event:
        sessions_by_event[event]["solves"].sort(key=lambda x: x[3])
        counts.append([sessions_by_event[event]["data"]["stat"][0], event]) # store total solve count for later

    # assign ranks based on total solve count
    counts.sort(reverse=True) # sort descending
    for i, counted_event in enumerate(counts, start=1):
        sessions_by_event[counted_event[1]]["data"]["rank"] = i

    # now go through counted/sorted events and add them to sorted_sessions
    new_session_data = {}
    for i, counted_event in enumerate(counts, start=1):
        session = "session" + str(i)
        sorted_sessions[session] = sessions_by_event[counted_event[1]]["solves"]

        # prepare the sessionData too!
        counted_event_name = counted_event[1]
        new_session_data[i] = sessions_by_event[counted_event_name]["data"]

    sorted_sessions["properties"] = {"sessionData":json.dumps(new_session_data)}

    for i, file in enumerate(all_properties, start=1):
        print(i,". ", file[0], sep="")
    result = 1
    while result == 1:
        result = resolve_properties()


def parse_session(session, sesh_num, session_data):
    sesh_name = session_data[sesh_num]["name"]

    if sesh_name not in sessions_by_event: # sesh num should not be definite yet
        sessions_by_event[sesh_name] = {"data":session_data[sesh_num],"solves":[]}

    # check for each solve if it's not already been added, if not, add
    for solve in session:
        date = solve[3]

        if date not in all_dates:
            sessions_by_event[sesh_name]["solves"].append(solve)
            all_dates[date] = 0

    resolve_event_data(session_data[sesh_num], sesh_name)

def resolve_event_data(b, sesh_name):
    a = sessions_by_event[sesh_name]["data"]

    if len(a) == 0:
        a = b
        return

    # i've only ever seen scrType in opt, but this should be more nuanced
    if len(a["opt"]) < len(b["opt"]):
        a["opt"] = b["opt"]

    a["stat"][0] += b["stat"][0] # total count
    a["stat"][2] = (a["stat"][2] + b["stat"][2]) / 2

    if a["date"][0] > b["date"][0]: a["date"][0] = b["date"][0]
    if a["date"][1] < b["date"][1]: a["date"][1] = b["date"][1]

def resolve_properties():
    choice = input("Please type the number of the file from which to keep your settings.")

    if not choice.isdigit():
        print("Please type a number.")
        return 1

    elif int(choice) not in range(1, len(all_properties) + 1):
        print("Please choose one of the options above.")
        return 1

    else:
        user_data = (all_properties[int(choice) - 1][1])
        for setting in user_data:
            if setting == "sessionN": # we need to change 1 more thing!
                session_no = len(sorted_sessions) - 1
                sorted_sessions["properties"][setting] = session_no
            else:
                sorted_sessions["properties"][setting] = user_data[setting]
        return 0

main()

with open("merged.json", "w") as f:
    json.dump(sorted_sessions, f, separators=(",", ":"))