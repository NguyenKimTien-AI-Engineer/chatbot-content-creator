from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import time
import threading

from configs import environment, constant
from configs.prompts.chart import prompt_chatbot_chart

from controllers.data import clean, context_reduce
from controllers.llm import token as _token


def get_chart(user_id, query, retrievers):
    try:
        contexts = clean.clean_special_characters(retrievers)
        code = answer_char_plotly(user_id, contexts, query)
        code_string = process_string_char_plot(code)
        html_code = save_plotly_to_html(code_string)

        return html_code
    except Exception as e:
        print(f"Error in get_chart: {e}")
        return None


def answer_char_plotly(user_id, contexts, query):
    start_time = time.time()

    contexts, num_token_input = context_reduce.context_reduce(contexts, constant.MODEL_CHATBOT_CHART)

    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_chatbot_chart.GENERATE_CHART_PLOTLY),
            ]
        )

        chain = (
            prompt
            | environment.get_llm(model=constant.MODEL_CHATBOT_CHART)
            | StrOutputParser()
        )

        answer = chain.invoke({"context": str(contexts), "query": str(query)})

        num_tokens_output = _token.calculate_tokens(answer, model=constant.MODEL_CHATBOT_CHART, name="generate_chart")
        response_time = time.time() - start_time

        threading.Thread(
            target=_token.save_tokens,
            args=(user_id, "Chart", num_token_input, num_tokens_output, constant.MODEL_CHATBOT_CHART, round(response_time, 2)),
        ).start()

        return answer

    except Exception as e:
        print(f"Error in answer_char_plotly: {e}")
        return None


# Tách đoạn mã python vừa tạo ở trên thành 1 đoạn string chỉ chứa code
def process_string_char_plot(string):
    try:
        # Tách chuỗi theo đoạn '```python' để lấy phần code
        parts = string.split("```python")
        # Kiểm tra và tách phần code bên trong nếu nó tồn tại
        if len(parts) > 1:
            string_code = parts[1].split("```")[0].strip()
        else:
            string_code = None
        return string_code
    except Exception as e:
        print(f"Error process_string_char_plot: {e}")
        return None


# Chuyển code string ở trên thành file html lưu vào folder_path được chỉ định
def save_plotly_to_html(code_string):
    try:
        # Chuẩn hóa nội dung code_string
        code_string = code_string.replace("<open_curly>", "{").replace("<close_curly>", "}")

        # Kiểm tra trước khi thực thi
        if "fig" not in code_string:
            raise ValueError("Code string must define a Plotly figure object named 'fig'.")

        # Thực thi mã
        local_context = {}
        exec(code_string, globals(), local_context)

        # print(code_string)

        # Lấy đối tượng fig
        fig = local_context.get("fig")
        if fig is None:
            raise ValueError("No 'fig' object found after executing the code string.")

        # Xuất sang HTML
        html_code = fig.to_html()

        return html_code

    except ValueError as ve:
        print(f"ValueError in save_plotly_to_html: {ve}")
    except AttributeError as ae:
        print(f"AttributeError in save_plotly_to_html: {ae}")
    except Exception as e:
        print(f"Error save_plotly_to_html: {e}")
    return None
