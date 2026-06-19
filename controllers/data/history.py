import json
import os
import uuid

from configs import constant, environment
from controllers.data import clean

############################################################################################################
# Save history
def save_history(user_id, history_id, session_id, query, answer, feedback, feedback_status, references, chart):
    try:
        path = f"{constant.DATA_HISTORY}/{user_id}"
        os.makedirs(path, exist_ok=True)

        if not history_id:
            history_id = str(uuid.uuid4())
        if not session_id:
            session_id = str(uuid.uuid4())

        user_history_file = os.path.join(
            path, f"{session_id}.json"
        )
        history = []
        if os.path.exists(user_history_file):
            with open(user_history_file, "r", encoding="utf-8") as file:
                try:
                    history = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {user_history_file}")
                    pass

        # Append new query and answer
        history.append({"history_id": history_id, "query": query, "answer": answer, "feedback": feedback, "feedback_status": feedback_status, "reference": references, "chart": chart})

        # Save history back to file
        with open(user_history_file, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

        try:
            if environment.memory is not None:
                messages = [{"role": "user", "content": query}, {"role": "assistant", "content": str(answer)}]
                environment.memory.add(messages, user_id=session_id)
            
        except Exception as e:
            print("Error saving to memory: ", e)

        return
    except Exception as e:
        print("Error saving history: ", e)
        return



def save_history_v2(user_id, history_id, session_id, query, answer, feedback, feedback_status, references, chart):
    try:
        path = f"{constant.DATA_HISTORY}/{user_id}"
        os.makedirs(path, exist_ok=True)

        if not history_id:
            history_id = str(uuid.uuid4())
        if not session_id:
            session_id = str(uuid.uuid4())

        user_history_file = os.path.join(
            path, f"{session_id}.json"
        )
        history = []
        if os.path.exists(user_history_file):
            with open(user_history_file, "r", encoding="utf-8") as file:
                try:
                    history = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {user_history_file}")
                    pass

        # Append new query and answer
        history.append({"history_id": history_id, "query": query, "answer": answer, "feedback": feedback, "feedback_status": feedback_status, "reference": references, "chart": chart})

        # Save history back to file
        with open(user_history_file, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

        return
    except Exception as e:
        print("Error saving history: ", e)
        return
    
    
############################################################################################################
# Load history
def get_history(user_id, session_id):
    try:
        path = f"{constant.DATA_HISTORY}/{user_id}"

        user_history_file = os.path.join(
            path, f"{session_id}.json"
        )

        if not os.path.exists(user_history_file):
            return []

        if os.path.getsize(user_history_file) == 0:
            return []

        with open(user_history_file, "r", encoding="utf-8") as file:
            try:
                history = json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {user_history_file}")
                return []

        return history
    except Exception as e:
        print("Error getting history: ", e)
        return []


def get_all_history_user(user_id):
    histories = []
    try:
        folder_path = f"{constant.DATA_HISTORY}/{user_id}"

        # Nếu thư mục không tồn tại, trả về mảng rỗng
        if not os.path.exists(folder_path):
            return histories

        # Duyệt qua tất cả các file trong thư mục
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)

                # Nếu file rỗng, bỏ qua
                if os.path.getsize(file_path) == 0:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        histories.append(data)
                except json.JSONDecodeError:
                    print(f"Lỗi giải mã JSON từ file: {file_path}")
                    continue

        return histories
    except Exception as e:
        print("Lỗi khi lấy lịch sử: ", e)
        return []


############################################################################################################
def update_feedback(user_id, history_id, new_feedback, new_feedback_status, session_id=None):
    try:
        user_directory = f"{constant.DATA_HISTORY}/{user_id}"

        if not os.path.exists(user_directory):
            print(f"Thư mục {user_directory} không tồn tại!")
            return False, []

        for file_name in os.listdir(user_directory):
            if file_name.endswith(".json"):
                if session_id and f"{session_id}.json" not in file_name:
                    continue

                user_history_file = os.path.join(user_directory, file_name)
                try:
                    with open(user_history_file, "r", encoding="utf-8") as file:
                        history = json.load(file)
                except json.JSONDecodeError:
                    print(f"Lỗi khi đọc file JSON: {user_history_file}")
                    continue

                updated_entries = []
                if history:
                    for entry in history:
                        if entry.get("history_id") == history_id:
                            if new_feedback_status is not None:
                                entry["feedback_status"] = new_feedback_status
                            if new_feedback is not None:
                                entry["feedback"] = new_feedback
                            updated_entries.append(entry)

                    if updated_entries:
                        with open(user_history_file, "w", encoding="utf-8") as file:
                            json.dump(history, file, indent=4)
                        return True, updated_entries

        print(f"Not found history in {user_directory}!")
        return False, []

    except Exception as e:
        print("Error updating feedback: ", e)
        return False, []


def get_history_context(user_id, query, session_id):
    history_context = ""

    history = get_history(user_id, session_id)
    if len(history) > 15:
        history = history[-15:]

    for entry in history[:-3]:
        entry["answer"] = ""
        # entry["reference"] = ""

    for item in history:
        if item['query']:
            history_context += f"- User: [{item['query']}]"
        if item['answer']:
            history_context += f"\n- You: [{item['answer']}]"
        # if item['reference']:
        #     history_context += f"\n- References to previous question (for reference only when asking previous question): [{str(clean_json_data(item['reference']))}]"

    history_context += f"\n\n- User: {query}\n"
    if environment.memory is not None:
        try:
            relevant_memories = environment.memory.search(query=query, user_id=session_id, limit=5)
            history_context_ = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
            if history_context_:
                history_context += "⚙️ Relevant Memories: " + str(history_context_)
                print("⚙️ Relevant Memories: ", history_context_)
        except Exception as e:
            print("Error searching memory: ", e)

    history_context = clean.clean_special_characters(history_context)

    return history_context


def get_history_context_v2(user_id, query, session_id):
    history_context = ""

    history = get_history(user_id, session_id)
    if len(history) > 5:
        history = history[-5:]

    for entry in history[:-1]:
        entry["answer"] = ""

    for item in history:
        if item['query']:
            history_context += f"- User: [{item['query']}]"
        if item['answer']:
            history_context += f"\n- You: [{item['answer']}]"

    history_context += f"\n\n- User: {query}\n"

    history_context = clean.clean_special_characters(history_context)

    return history_context