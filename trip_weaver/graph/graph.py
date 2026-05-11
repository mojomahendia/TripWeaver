from langgraph.graph import START, END, StateGraph
from trip_weaver.graph.state import TripweverState
from trip_weaver.graph.nodes.query_parser import query_parser
from trip_weaver.graph.nodes.researcher import researcher
from trip_weaver.graph.nodes.planner import planner

graph = StateGraph(TripweverState)

graph.add_node("query_parser", query_parser)
graph.add_node("researcher", researcher)
graph.add_node("planner", planner)

graph.add_edge(START, "query_parser")
graph.add_edge("query_parser", "researcher")
graph.add_edge("researcher", "planner")
graph.add_edge("planner", END)

workflow = graph.compile()
