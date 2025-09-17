import streamlit as st
import json
from pathlib import Path
import datetime

def get_current_week_start():
    today = datetime.date.today()
    # Assuming week starts on Monday (weekday 0)
    start = today - datetime.timedelta(days=today.weekday())
    return start.isoformat()

# Data file path
data_file = Path("data.json")

# Load or initialize data with error handling
try:
    with data_file.open("r") as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    st.warning("Data file not found or corrupted. Initializing new data.")
    data = {
        "tasks": [],  # list of {"id": int, "name": str, "value": float}
        "next_id": 1,
        "completions": [],  # list of completed task ids for current week
        "week": get_current_week_start(),
        "allowance_history": []  # list of {"week": str, "total": float}
    }

# Check if week has changed
current_week = get_current_week_start()
if data["week"] != current_week:
    # Calculate previous total
    previous_completions = set(data["completions"])
    previous_total = sum(
        t["value"] for t in data["tasks"] if t["id"] in previous_completions
    )
    # Archive
    data["allowance_history"].append({
        "week": data["week"],
        "total": previous_total
    })
    # Reset for new week
    data["completions"] = []
    data["week"] = current_week

# App title
st.title("Task & Weekly Allowance Tracker")

# Sidebar for adding and managing tasks
with st.sidebar:
    st.header("Add New Task")
    new_name = st.text_input("Task Name")
    new_value = st.number_input("Allowance Value ($)", min_value=0.0, step=0.5)
    if st.button("Add Task"):
        if new_name.strip():
            new_task = {
                "id": data["next_id"],
                "name": new_name.strip(),
                "value": new_value
            }
            data["tasks"].append(new_task)
            data["next_id"] += 1
            st.success(f"Added task: {new_name}")
        else:
            st.error("Task name cannot be empty.")

    st.header("Manage Tasks")
    if data["tasks"]:
        task_options = {t['name']: t['id'] for t in data["tasks"]}
        selected_name = st.selectbox("Select Task to Edit/Delete", [""] + list(task_options.keys()))
        if selected_name:
            task_id = task_options[selected_name]
            task = next(t for t in data["tasks"] if t["id"] == task_id)
            edit_name = st.text_input("Edit Name", task['name'])
            edit_value = st.number_input("Edit Value ($)", value=task['value'], min_value=0.0, step=0.5)
            if st.button("Save Changes"):
                if edit_name.strip():
                    task['name'] = edit_name.strip()
                    task['value'] = edit_value
                    st.success("Task updated.")
                else:
                    st.error("Task name cannot be empty.")
            if st.button("Delete Task"):
                data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
                if task_id in data["completions"]:
                    data["completions"].remove(task_id)
                st.success("Task deleted.")
    else:
        st.info("No tasks to manage.")

# Main section: Current week tasks
st.header(f"Tasks for Week Starting {data['week']}")
if not data["tasks"]:
    st.info("No tasks added yet. Use the sidebar to add tasks.")
else:
    completions = set(data["completions"])
    # Sort tasks by name for display
    sorted_tasks = sorted(data["tasks"], key=lambda t: t["name"].lower())
    for task in sorted_tasks:
        label = f"{task['name']} (${task['value']:.2f})"
        is_done = task["id"] in completions
        if st.checkbox(label, value=is_done):
            if not is_done:
                data["completions"].append(task["id"])
        else:
            if is_done:
                data["completions"].remove(task["id"])

# Calculate and display current totals
potential_total = sum(t["value"] for t in data["tasks"])
current_total = sum(t["value"] for t in data["tasks"] if t["id"] in completions)
remaining = potential_total - current_total
st.subheader(f"Current Weekly Allowance: ${current_total:.2f}")
st.write(f"Potential Total: ${potential_total:.2f} | Remaining: ${remaining:.2f}")

# Display history if available
if data["allowance_history"]:
    st.header("Allowance History")
    for entry in reversed(data["allowance_history"]):  # Most recent first
        st.write(f"Week {entry['week']}: ${entry['total']:.2f}")

# Save data back to file with error handling
try:
    with data_file.open("w") as f:
        json.dump(data, f, indent=4)  # Added indent for readability
except Exception as e:
    st.error(f"Error saving data: {str(e)}")
