import json
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from trip_weaver.models.gpt_model import model_client
from trip_weaver.prompts.research_prompt import RESEARCH_PROMPT
from trip_weaver.graph.state import TripweverState

_parser = JsonOutputParser()
_chain = model_client | _parser


def researcher(state: TripweverState) -> TripweverState:
    system_content = (
        RESEARCH_PROMPT
        + "\n\nTravel parameters:\n"
        + json.dumps(state["parsed_params"], indent=2)
    )
    result = _chain.invoke([SystemMessage(content=system_content)])
    return {"research": result}
