import subprocess, sys, os, glob
import numpy as np
from tqdm import tqdm
python_executable = "/home/sasha/miniconda3/envs/cs336_basics/bin/python"
script_path = "/home/sasha/classes/cs336/spring2024-assignment1-basics/cs336_basics/scripts/gen_data.py"

def merge_text_files(file_paths, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for file_path in tqdm(file_paths):
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n")  # Add a newline between files
                else:
                    print(f"Warning: {file_path} does not exist or is not a file.")
        print(f"Files merged successfully into {output_file}")
    except Exception as e:
        print(f"An error occurred while merging files: {e}")

def run_tokenizer(save_folder, input_path):
  args = ["--save_folder", save_folder,
          "--input_path", input_path]
  command = [python_executable, script_path] + args
  try:
    print("running subprocess!")
    result = subprocess.run(
        command,
        check=True,
#        capture_output=True,
        text=True
    )
    print("Output:\n", result.stdout)
    if result.stderr:
      print("Errors:\n", result.stderr)
  except subprocess.CalledProcessError as e:
    print(f"Execution failed with return code {e.returncode}")
    print(f"Output:\n{e.stdout}")
    print(f"Errors:\n{e.stderr}")

if __name__=="__main__":
    cleaned_folder = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/cleaned"
    txt_file_paths = glob.glob("%s/*" % cleaned_folder)
    data_path = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/cleaned_text.txt"
    print(txt_file_paths)
    merge_text_files(txt_file_paths, data_path)
    save_folder = "/home/sasha/classes/cs336/spring2024-assignment1-basics/project_data/data/TinyStoriesV2-GPT4-train-10000"
    run_tokenizer(save_folder=save_folder, input_path=data_path)
