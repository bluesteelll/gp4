from graph.builder import build_graph


def main():
    app = build_graph()
    result = app.invoke({"data": ""})
    print(result["data"])


main()
