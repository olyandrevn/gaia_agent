from src.graph import build_graph
from dotenv import load_dotenv
import logging
import pandas as pd
import json


load_dotenv()


class ReActAgent:
    def __init__(self):
        # print("ReActAgent initialized.")
        self.graph = build_graph()
        with open("prompts/system_prompt_short.txt", "r", encoding="utf-8") as f:
            self.system_message = f.read()

        self.result_file = open('results/result7.jsonl', 'a')

    def __call__(self, task) -> str:
        initial_state = {
            'system_message': self.system_message,
            'question': task.get("question"),
            'file_name': task.get("file_name"),
        }
        final_state = self.graph.invoke(initial_state)
        final_answer = final_state.get("final_answer", None)

        row = {'task_id': task.get("task_id"), 'question': task.get("question"), 'agent_answer': final_answer}
        json.dump(row, self.result_file)
        self.result_file.write('\n')

        return final_answer

def main():
    agent = ReActAgent()

    gaia_bench_1_test = pd.read_json('../gaia_bench_1_test.jsonl', lines=True)

    for i, task in gaia_bench_1_test.iterrows():
        agent(task.question, task.file_name)

if __name__ == "__main__":
    main()