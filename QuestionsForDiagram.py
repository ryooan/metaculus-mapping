import requests
import csv

def process_results(results, seen_ids):

    for row in results:
            # Extract information
            page_url = row.get("page_url", "N/A")
            title = row.get("title", "N/A")
            q_type = row.get("type", "N/A")
            question_id = row.get("id", "N/A")
            forecast_type = row.get("possibilities", {}).get("type", {}) if row.get("possibilities", {}) else {}
            activity = row.get("activity", "N/A")
            active_state = row.get("active_state", "N/A")
            community_prediction = row.get("community_prediction", {}).get("full", {}) if row.get("community_prediction", {}) else {}
            q2 = community_prediction.get("q2", "N/A") if community_prediction else "N/A"
            scale = row.get("possibilities", {}).get("scale", {}) if row.get("possibilities", {}) else {}
            range_min = scale.get("min", {}) if scale else {}
            range_max = scale.get("max", {}) if scale else {}
            deriv_ratio = scale.get("deriv_ratio", {}) if scale else {}
            
            # get resolution criteria and other details for all non-subquestions.
            # since this appends to csv_data need to check to make sure id hasn't already been looked at.
            if question_id not in seen_ids:
                seen_ids.add(question_id)
                
                q_response = requests.get("https://www.metaculus.com/api2/questions/"+str(question_id))
                if q_response.status_code == 200:
                    q_data = q_response.json()
                    resolution_text = q_data.get("resolution_criteria", "N/A")
                    fine_print_text = q_data.get("fine_print", "N/A")
                    fan_graph = q_data.get("has_fan_graph", "N/A")
                    custom_group = q_data.get("group", "N/A")
                else:
                    print(f"Failed to get q_response data. HTTP status code: {q_response.status_code}")
                    resolution_text = "failed"
                    fine_print_text = "failed"
                    
                csv_data.append([page_url, title, q_type, question_id, forecast_type, activity, "", "", active_state, q2, resolution_text, fine_print_text, fan_graph, custom_group, range_min, range_max, deriv_ratio])

            sub_questions = row.get("sub_questions", [])
            
            # Add data
            for sub_question in sub_questions:
                if sub_question is None:
                    continue
                else:
                    sub_question_id = sub_question.get("id", "N/A")
                    subquestion_type = sub_question.get("possibilities", {}).get("type", {}) if sub_question.get("possibilities", {}) else {}
                    sub_question_label = sub_question.get("sub_question_label", "N/A")
                    conditioned_on = sub_question.get("conditioned_on_resolution", {})
                    active_state = sub_question.get("active_state", "N/A")
                    community_prediction = sub_question.get("community_prediction", {}) if sub_question is not None else {}
                    full_prediction = community_prediction.get("full", {}) if community_prediction is not None else {}
                    q2 = full_prediction.get("q2", "N/A") if full_prediction else {}
                    scale = sub_question.get("possibilities", {}).get("scale", {}) if sub_question.get("possibilities", {}) else {}
                    range_min = scale.get("min", {}) if scale else {}
                    range_max = scale.get("max", {}) if scale else {}
                    deriv_ratio = scale.get("deriv_ratio", {}) if scale else {}
                    
                    if sub_question_id not in seen_ids:
                        seen_ids.add(sub_question_id)
                        csv_data.append([page_url, title, "", sub_question_id, subquestion_type, "", sub_question_label, conditioned_on, active_state, q2, "", "", "", "", range_min, range_max, deriv_ratio])

# Initialize API URL for set of questions
base_url = 'https://www.metaculus.com/api2/questions/'

#create list of seen ids
seen_ids = set()

# Prepare data for CSV
csv_data = []
# Write header
csv_data.append(["page_url", "title", "type", "question_id", "forecast_type", "activity", "sub_question_label", "conditioned_on", "active", "median", "resolution_criteria", "fine_print", "fan_graph", "custom_group", "lower_bound", "upper_bound", "deriv_ratio"])

#get specific questions
specific_url = base_url + "11480"

response = requests.get(specific_url)
if response.status_code == 200:
    data = response.json()
else:
    print(f"Failed to get data. HTTP status code: {response.status_code}")

process_results([data], seen_ids)

#get list of questions
loopcounter = 0
offset = 0  # Initialize offset
limit = 100  # Number of records per request

while True:
    if loopcounter == 0:
        url = f"{base_url}?limit={limit}&project=2673"
        print("Fetching data with no offset")
    else:
        url = f"{base_url}?limit={limit}&offset={offset}&project=2673"
        print(f"Fetching data with offset {offset}")
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to get data. HTTP status code: {response.status_code}")
        break
    
    results = data.get("results", [])
    if not results:
        print("No more results.")
        break  # Exit the loop if no more results are returned
    
    process_results(results, seen_ids)

    offset += limit  # Increment the offset for the next batch
    loopcounter += 1


# Write to CSV
csv_filename = "questions_list.csv"
with open(csv_filename, "w", newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(csv_data)

print(f"CSV file has been written.")