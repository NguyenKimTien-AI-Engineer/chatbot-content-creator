from dotenv import load_dotenv
import threading
import time
import ast

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from controllers.data import clean, context_reduce
from controllers.llm import token as _token

from configs import environment, constant
from configs.prompts.suggestion import prompt_suggestion

load_dotenv()


############################################################################################################
def chatbot_suggestion(user_id, query, answer, context=""):
    start_time = time.time()

    context, num_token_input = context_reduce.context_reduce(context, constant.MODEL_CHATBOT_SUGGESTION)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_suggestion.CHATBOT),
        ]
    )

    chain = (
            prompt | environment.get_llm(model=constant.MODEL_CHATBOT_SUGGESTION) | StrOutputParser()
    )

    results = chain.invoke({"question": str(query), "answer": str(answer), "context": str(context)})

    answer = clean.clean_special_characters(results)

    num_tokens_output = _token.calculate_tokens(answer, model=constant.MODEL_CHATBOT_SUGGESTION, name="chatbot_suggestion")
    response_time = time.time() - start_time

    threading.Thread(
        target=_token.save_tokens,
        args=(user_id, "Response", num_token_input, num_tokens_output, constant.MODEL_CHATBOT_SUGGESTION, round(response_time, 2)),
    ).start()

    try:
        # Bọc chuỗi thành literal của list
        sug_list = ast.literal_eval("[" + answer + "]")
    except Exception as e:
        sug_list = answer
        print(f"Đã có lỗi khi chuyển đổi: {e}")

    return sug_list


