from src.graph import build_graph
from dotenv import load_dotenv
import logging
import pandas as pd
import json


load_dotenv()


class ReActAgent:
    def __init__(self):
        print("ReActAgent initialized.")
        self.graph = build_graph()
        with open("prompts/system_prompt_short.txt", "r", encoding="utf-8") as f:
            self.system_message = f.read()

        self.result_file = open('results/result6.jsonl', 'a')

    def __call__(self, question: str, file_name: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")

        initial_state = {
            'system_message': self.system_message,
            'question': question,
            'file_name': file_name,
        }
        final_state = graph.invoke(initial_state)
        final_answer = final_state.get("final_answer", None)

        row = {'task_id': task.task_id, 'question': task.question, 'gt': task['Final answer'], 'agent_answer': final_answer}
        json.dump(row, self.result_file)
        self.result_file.write('\n')

        print(f"Agent returning fixed answer: {fixed_answer}")
        return fixed_answer

def main():
    agent = ReActAgent()

    gaia_bench_1_test = pd.read_json('../gaia_bench_1_test.jsonl', lines=True)

    for i, task in gaia_bench_1_test.iterrows():
        agent(task.question, task.file_name)

if __name__ == "__main__":
    main()