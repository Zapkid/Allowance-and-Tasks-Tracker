# app.py
import streamlit as st
import json
from pathlib import Path
import datetime

# Set page config for a fun, colorful theme
st.set_page_config(page_title="Kids' Allowance Adventure", page_icon="⭐", layout="centered")

# Streamlit theme customization
st.markdown("""
<style>
body {
    background-color: #f0f8ff;
}
h1, h2, h3 {
    font-family: 'Comic Sans MS', cursive, sans-serif;
    color: #ff4500;
}
.stButton>button {
    background-color: #32cd32;
    color: white;
    font-size: 18px;
    border-radius: 10px;
}
.stTextInput>div>input {
    font-size: 16px;
}
.stNumberInput>div>input {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

def get_current_week_start():
    today = datetime.date.today()
    # Week starts on Monday
    start = today - datetime.timedelta(days=today.weekday())
    return start.isoformat()

# Data file path
data_file = Path("data.json")

# Load or initialize data
try:
    with data_file.open("r") as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    st.warning("Oops! No data found. Starting fresh! 😊")
    data = {
        "tasks": [],  # list of {"id": int, "name": str, "value": float}
        "next_id": 1,
        "completions": [],  # list of completed task ids for current week
        "week": get_current_week_start(),
        "weekly_allowance": 5.0,  # Default fixed allowance
        "history": []  # list of {"week": str, "task_earnings": float, "allowance": float}
    }

# Check if week has changed
current_week = get_current_week_start()
if data["week"] != current_week:
    # Calculate previous task earnings
    previous_completions = set(data["completions"])
    previous_task_earnings = sum(
        t["value"] for t in data["tasks"] if t["id"] in previous_completions
    )
    # Archive
    data["history"].append({
        "week": data["week"],
        "task_earnings": previous_task_earnings,
        "allowance": data["weekly_allowance"]
    })
    # Reset for new week
    data["completions"] = []
    data["week"] = current_week

# App title with emoji
st.title("🎉 Kids' Allowance Adventure! 🤑")

# Sidebar for settings (parent controls)
with st.sidebar:
    st.header("⚙️ Grown-Up Settings")
    st.markdown("### Set Weekly Allowance")
    allowance = st.number_input("Weekly Allowance ($)", min_value=0.0, step=1.0, value=data["weekly_allowance"])
    if st.button("Save Allowance"):
        data["weekly_allowance"] = allowance
        st.success("Allowance updated! 💰")

    st.markdown("### Add a New Task")
    new_name = st.text_input("Task Name (e.g., Clean Room)")
    new_value = st.number_input("Extra Money for Task ($)", min_value=0.0, step=0.5)
    if st.button("Add Task"):
        if new_name.strip():
            new_task = {
                "id": data["next_id"],
                "name": new_name.strip(),
                "value": new_value
            }
            data["tasks"].append(new_task)
            data["next_id"] += 1
            st.success(f"Added task: {new_name} 🎈")
        else:
            st.error("Please enter a task name! 😕")

    st.markdown("### Manage Tasks")
    if data["tasks"]:
        task_options = {t['name']: t['id'] for t in data["tasks"]}
        selected_name = st.selectbox("Pick a Task to Change or Remove", [""] + list(task_options.keys()))
        if selected_name:
            task_id = task_options[selected_name]
            task = next(t for t in data["tasks"] if t["id"] == task_id)
            edit_name = st.text_input("Change Task Name", task['name'])
            edit_value = st.number_input("Change Task Money ($)", value=task['value'], min_value=0.0, step=0.5)
            if st.button("Save Changes"):
                if edit_name.strip():
                    task['name'] = edit_name.strip()
                    task['value'] = edit_value
                    st.success("Task updated! 🌟")
                else:
                    st.error("Task name can’t be empty! 😕")
            if st.button("Remove Task"):
                data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
                if task_id in data["completions"]:
                    data["completions"].remove(task_id)
                st.success("Task removed! 🗑️")
    else:
        st.info("No tasks to change yet! 😊")

# Main section: Current week's tasks
st.header(f"📅 Your Tasks for Week of {data['week']}")
if not data["tasks"]:
    st.info("No tasks yet! Ask a grown-up to add some fun tasks! 😄")
else:
    completions = set(data["completions"])
    sorted_tasks = sorted(data["tasks"], key=lambda t: t["name"].lower())
    for task in sorted_tasks:
        label = f"{task['name']} (Extra ${task['value']:.2f} 💸)"
        is_done = task["id"] in completions
        if st.checkbox(label, value=is_done):
            if not is_done:
                data["completions"].append(task["id"])
                st.balloons()
        else:
            if is_done:
                data["completions"].remove(task["id"])

# Calculate and display totals
task_earnings = sum(t["value"] for t in data["tasks"] if t["id"] in completions)
total_money = task_earnings + data["weekly_allowance"]
potential_task_earnings = sum(t["value"] for t in data["tasks"])
potential_total = potential_task_earnings + data["weekly_allowance"]

st.subheader("💰 Your Money This Week")
st.markdown(f"**Weekly Allowance**: ${data['weekly_allowance']:.2f} 🎁")
st.markdown(f"**Task Earnings**: ${task_earnings:.2f} 🏆")
st.markdown(f"**Total Money**: ${total_money:.2f} 🥳")
st.markdown(f"**You Could Earn Up To**: ${potential_total:.2f} 🚀")

# Display history
if data["history"]:
    st.header("📜 Your Money History")
    for entry in reversed(data["history"]):
        st.markdown(f"**Week {entry['week']}**: Allowance ${entry['allowance']:.2f} + Tasks ${entry['task_earnings']:.2f} = **${entry['allowance'] + entry['task_earnings']:.2f}**")

# Save data with error handling
try:
    with data_file.open("w") as f:
        json.dump(data, f, indent=4)
except Exception as e:
    st.error(f"Oops! Trouble saving: {str(e)} 😕")

# Add a fun footer
st.markdown("---")
st.markdown("Made with ❤️ for awesome kids!")
