import subprocess
import pandas as pd

repo_path = "/home/carlos/tcc/linux"
csv_output_path = "linux_kernel_commits_detailed.csv"

git_log_command = [
    "git", "log", "--pretty=format:%H,%an,%ae,%ad,%s", "--numstat"
]

def run_git_log_command(command, path):
    try:
        return subprocess.check_output(command, cwd=path, encoding='latin1')
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando git log: {e}")
        exit(1)

def parse_commit_line(line):
    fields = line.split(',')
    return {
        'hash': fields[0] if len(fields) > 0 else "NO_HASH",
        'author': fields[1] if len(fields) > 1 else "NO_AUTHOR",
        'email': fields[2] if len(fields) > 2 else "NO_EMAIL",
        'date': fields[3] if len(fields) > 3 else "NO_DATE",
        'message': fields[4] if len(fields) > 4 else "NO_MESSAGE",
        'insertions': 0,
        'deletions': 0,
        'modified_files': 0,
        'files_changed': []  
    }

def process_commit(commit, commits_data):
    print(f"Commit processado: {commit['hash']}")
    commits_data.append(commit)

def main():
    log_output = run_git_log_command(git_log_command, repo_path)
    if not log_output:
        print("Nenhum dado foi retornado pelo comando git log")
        exit(1)
    commits_data = []
    current_commit = None
    lines = log_output.splitlines()
    commit_count = 0
    print(f"Processando o arquivo de log com {len(lines)} linhas...")

    for line in lines:
        if line.strip() == "":
            continue
        
        if ',' in line:
            if current_commit is not None:
                process_commit(current_commit, commits_data)
                current_commit = None
            current_commit = parse_commit_line(line)
            commit_count += 1
            print(f"Processando o commit {commit_count}...")

        elif current_commit:
            stats = [value for value in line.split() if value]
            if len(stats) == 3:
                insertions, deletions, file_path = stats
                current_commit['insertions'] += int(insertions) if insertions.isdigit() else 0
                current_commit['deletions'] += int(deletions) if deletions.isdigit() else 0
                current_commit['files_changed'].append(file_path)
                current_commit['modified_files'] += 1

            if line == lines[-1]:
                process_commit(current_commit, commits_data)
                current_commit = None
    print(f"Total de commits processados: {commit_count}")

    if not commits_data:
        print("Nenhum commit foi processado.")
        exit(1)

    df_commits = pd.DataFrame(commits_data)
    print(df_commits.head())
    df_commits.to_csv(csv_output_path, index=False)
    print(f"Total de commits: {commit_count}")

if __name__ == "__main__":
    main()