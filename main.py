from trip_weaver.graph.graph import workflow


def main():
    query = input("Where do you want to go? ").strip()
    if not query:
        print("No query provided.")
        return
    print("\nPlanning your trip...\n")
    state = workflow.invoke({"query": query})
    print(state["plan"])


if __name__ == "__main__":
    main()
