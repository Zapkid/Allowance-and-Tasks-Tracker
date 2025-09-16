import streamlit as st
from data_manager import load_data, save_data

st.set_page_config(page_title="Child Allowance Tracker", layout="centered")

st.title("👶 Child Allowance & Tasks Tracker")

# Load existing data
data = load_data()

# Sidebar for child settings
st.sidebar.header("⚙️ Settings")
child_name = st.sidebar.text_input("Child's Name", value=data.get("child_name", "My Child"))
weekly_allowance = st.sidebar.number_input("Weekly Allowance ($)", value=data.get("weekly_allowance", 10), step=1)

# Save updated settings
data["child_name"] = child_name
data["weekly_allowance"] = weekly_allowance

st.subheader(f"Allowance for {child_name}")

# Task input
with st.form("task_form"):
    task_name = st.text_input("Task Name")
    task_reward = st.number_input("Reward ($)", step=1, value=1)
    submitted = st.form_submit_button("➕ Add Task")

    if submitted and task_name:
        data["tasks"].append({"task": task_name, "reward": task_reward, "done": False})
        save_data(data)
        st.success(f"Added task: {task_name} (${task_reward})")

# Task list
st.subheader("📋 Task List")
if data["tasks"]:
    for i, task in enumerate(data["tasks"]):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"- {task['task']} (${task['reward']})")
        with col2:
            if st.button("✅ Done", key=f"done_{i}"):
                data["tasks"][i]["done"] = True
                save_data(data)
        with col3:
            if st.button("❌ Delete", key=f"delete_{i}"):
                del data["tasks"][i]
                save_data(data)
                st.experimental_rerun()
else:
    st.info("No tasks yet. Add one above!")

# Calculate balance
earned = sum(task["reward"] for task in data["tasks"] if task["done"])
total = data["weekly_allowance"] + earned
st.subheader("💰 Balance")
st.metric("Total Available", f"${total}")

# Save updated state
save_data(data)
