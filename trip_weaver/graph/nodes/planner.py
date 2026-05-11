import json
from langchain_core.messages import SystemMessage
from trip_weaver.models.gpt_model import model_client
from trip_weaver.prompts.planner_prompt import PLANNER_PROMPT
from trip_weaver.graph.state import TripweverState


def planner(state: TripweverState) -> TripweverState:
    system_prompt = (
        PLANNER_PROMPT
        + "\n\nTravel parameters:\n"
        + json.dumps(state["parsed_params"], indent=2)
        + "\n\nResearch data:\n"
        + json.dumps(state["research"], indent=2)
    )
    result = model_client.invoke([SystemMessage(content=system_prompt)])
    return {"plan": result.content}
