import re
import threading
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import time

from configs import constant, environment
from configs.prompts import prompt_summary
from controllers.llm import token as _token
from controllers.data import context_reduce


def image_summary(user_id, image_url):
    start_time = time.time()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", prompt_summary.IMAGE_SUMMARY,
            ),
            ("human", [
                {"type": "image_url", "image_url": {"url": image_url}},
            ],),
        ]
    )
    chain = (
            prompt
            | environment.get_llm(model=constant.MODEL_SUMMARY, temperature=0)
            | StrOutputParser()
    )

    answer = chain.invoke({"question": ""})

    num_tokens_output = _token.calculate_tokens(answer, model=constant.MODEL_SUMMARY, name="image_summary")
    response_time = time.time() - start_time

    threading.Thread(
        target=_token.save_tokens,
        args=(user_id, "Image Summary", 0, num_tokens_output, constant.MODEL_SUMMARY, round(response_time, 2)),
    ).start()

    return answer


def text_summary(user_id, contexts):
    start_time = time.time()
    contexts, num_token_input = context_reduce.context_reduce(contexts, constant.MODEL_SUMMARY)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompt_summary.TEXT_SUMMARY.format(
                    context=str(contexts),
                ),
            ),
        ]
    )

    chain = (
            prompt
            | environment.get_llm(model=constant.MODEL_SUMMARY, temperature=0)
            | StrOutputParser()
    )

    answer = chain.invoke({"input": ""})

    num_tokens_output = _token.calculate_tokens(answer, model=constant.MODEL_SUMMARY, name="image_summary")
    response_time = time.time() - start_time

    threading.Thread(
        target=_token.save_tokens,
        args=(user_id, "Text Summary", num_token_input, num_tokens_output, constant.MODEL_SUMMARY, round(response_time, 2)),
    ).start()

    result = re.split(r'</think>\s*', answer, maxsplit=1)[-1]
    result = result.replace("*", "")

    return result


