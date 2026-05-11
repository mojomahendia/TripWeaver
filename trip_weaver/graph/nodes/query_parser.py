import json
from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from trip_weaver.models.gpt_model import model_client
from trip_weaver.prompts.query_parser_prompt import QUERY_PARSER_PROMPT
from trip_weaver.graph.state import TripweverState

_parser = JsonOutputParser()
_chain = model_client | _parser


def query_parser(state: TripweverState) -> TripweverState:
    today = date.today().isoformat()
    prompt = f"Today's date is {today}.\n\n" + QUERY_PARSER_PROMPT
    result = _chain.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state["query"]),
    ])
    return {"parsed_params": result}
