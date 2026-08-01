from pathlib import Path
import json

files = []
file_names = []

# look for .txt files in script 
script_dir = Path(__file__).parent
for file in script_dir.iterdir():
    if file.name.endswith(".txt"):
        print("Found file:", file.name)
        files.append(file)

all_properties = []
sessions_by_event = {} # initial sorting of solves per event
sorted_sessions = {} # final sessions, sorted by count for rank, and by date for solve.

def main():
    for file_num, file in enumerate(files):
        with open(files[file_num], "r") as file:
            # extract file names for nice printing :)
            s = str(files[file_num])
            file_name = s[s.rfind("/") + 1:]
            file_names.append(file_name)

            print("Starting file:",file_name)
            data = json.load(file)

            # let's get properties (user settings) out of the way first
            session_data = json.loads(data["properties"]["sessionData"])
            properties = data["properties"]
            properties.pop("sessionData")
            all_properties.append([files[file_num], properties])

            # go through sessions and sort into events
            for session in data:
                sesh_num = session[7:]
                if (len(data[session]) != 0) and (session != "properties"):
                    print("Parsing",session,"in",file_name)
                    parse_session(data[session], str(sesh_num), session_data)
                else:
                    print(session, "is empty or irrelevant in",file_name)
                    pass

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

    for i, file_name in enumerate(file_names, start=1):
        print(i,". ", file_name, sep="")

    result = 1
    msg = "Please type the number of the file from which to keep your settings."
    while result == 1:
        choice = input(msg)
        result, msg = resolve_properties(choice)
    print(msg) # success print

def parse_session(session, sesh_num, session_data):
    sesh_name = session_data[sesh_num]["name"]
    first_occurance = sesh_name not in sessions_by_event

    if first_occurance:
        sessions_by_event[sesh_name] = {"data":session_data[sesh_num],"solves":[],"dates":{}}

    # check for each solve if it's not already been added, if not, add
    for solve in session:
        date = solve[3]

        if date not in sessions_by_event[sesh_name]["dates"]:
            sessions_by_event[sesh_name]["solves"].append(solve)
            sessions_by_event[sesh_name]["dates"][date] = 0

    if not first_occurance:
        resolve_event_data(session_data[sesh_num], sesh_name)

def resolve_event_data(b, sesh_name):
    a = sessions_by_event[sesh_name]["data"]

    # i've only ever seen scrType in opt, but this should be more nuanced
    if len(a["opt"]) < len(b["opt"]):
        a["opt"] = b["opt"]

    # stat and date are not created with unused sessions. it should be impossible for an unused session to be parsed by this code, but just in case:
    if ("stat" in a) and ("stat" in b):
        a_count = a["stat"][0]
        a_avg = a["stat"][2]
        b_count = b["stat"][0]
        b_avg = b["stat"][2]
        total_count = a_count + b_count

        combined_avg = (a_avg * a_count + b_avg * b_count) / (total_count) # weighted average

        a["stat"][0] = total_count
        a["stat"][2] = combined_avg

    elif ("stat" not in a) and ("stat" in b):
        a["stat"] = b["stat"]

    if ("date" in a) and ("date" in b):
        if a["date"][0] > b["date"][0]: a["date"][0] = b["date"][0]
        if a["date"][1] < b["date"][1]: a["date"][1] = b["date"][1]
        
    elif ("date" not in a) and ("date" in b):
        a["date"] = b["date"]

def resolve_properties(choice):
    if not choice.isdigit():
        return 1, "Please type a number."

    elif int(choice) not in range(1, len(all_properties) + 1):
        return 1, "Please choose one of the options above."

    else:
        user_data = (all_properties[int(choice) - 1][1])
        for setting in user_data:
            if setting == "sessionN": # we need to change 1 more thing!
                session_no = len(sorted_sessions) - 1
                sorted_sessions["properties"][setting] = session_no
            else:
                sorted_sessions["properties"][setting] = user_data[setting]
        return 0, "Exporting as 'merged.json'..."

main()

with open("merged.json", "w") as f:
    json.dump(sorted_sessions, f, separators=(",", ":"))