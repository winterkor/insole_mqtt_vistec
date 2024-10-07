import json

def check_sequential_counts(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    previous_count = None
    missing_counts = []
    total_messages = 0

    messages = data['data']['insole']['data']

    for message in messages:
        try:
            current_count = message['count']
            total_messages += 1

            if previous_count is not None and current_count != previous_count + 1:
                # Add all missing counts between previous_count and current_count
                missing_counts.extend(range(previous_count + 1, current_count))

            previous_count = current_count

        except KeyError:
            print(f"Warning: No 'count' field found in message: {message}")

    if missing_counts:
        print("Missing counts:", missing_counts)
    else:
        print("No missing counts found. All data is sequential.")

    print(f"Total number of messages: {total_messages}")
    print(f"Loss percentage: {(1-(int(total_messages))/total_num)*100} %")

json_file_path = "/Users/winter.__.kor/Desktop/test15.json"
total_num = int(input("Total num: "))
check_sequential_counts(json_file_path)