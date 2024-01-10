import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import requests

class CommitSearcher:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Commit Searcher")
        self.root.geometry("500x300")

        self.create_interface()

        self.is_lister_open = False
        
    def create_interface(self):
        ttk.Label(self.root, text="GitHub Token:").grid(row=0, column=0, padx=5, pady=5)
        self.token_entry = ttk.Entry(self.root, show='*')
        self.token_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self.root, text="GitHub repository owner:").grid(row=1, column=0, padx=5, pady=5)
        self.repo_owner = ttk.Entry(self.root)
        self.repo_owner.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self.root, text="GitHub repository:").grid(row=2, column=0, padx=5, pady=5)
        self.repo = ttk.Entry(self.root)
        self.repo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self.root, text="Listar Commits", command=self.list_commits).grid(row=3, column=0, columnspan=2, pady=10)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        for i in range(4):
            self.root.rowconfigure(i, weight=1)

    def list_commits(self):
        token = self.token_entry.get()
        repo_owner = self.repo_owner.get()
        repo = self.repo.get()

        if token and repo_owner and repo:
            try:
                headers = {
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {token}',
                    'X-GitHub-Api-Version': '2022-11-28',
                }

                response = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo}/commits', headers=headers)

                if response.status_code == 404:
                    messagebox.showerror("Erro", "Repositório não encontrado.\nVerifique se o nome e o nome do dono do repositório estão devidamente inseridos.")
                    return
                elif response.status_code == 401:
                    messagebox.showerror("Erro", "Token inválido.")
                    return

                commits = response.json()
                commits.sort(key=lambda x: x["commit"]["committer"]["date"], reverse=False)
                self.open_lister(commits)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao pesquisar commits:\n{str(e)}")
        else:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")

    def open_lister(self, commits):
        if not self.is_lister_open:
            commits_window = tk.Toplevel(self.root)
            GitHubCommitsLister(commits_window, self, commits)
            self.is_lister_open = True
            print('Inserting malware.... OK .... BACKDOOR CREATED')
        else:
            messagebox.showwarning("Aviso", "A janela de commits já está aberta.\n")
    
    def lister_closed(self):
        self.is_lister_open = False

class GitHubCommitsLister:
    def __init__(self, root, commit_searcher, commits):
        self.root = root
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("GitHub Commits Lister")
        self.root.geometry("650x600")
        self.commit_searcher = commit_searcher
        self.commits = commits

        self.create_search_interface()

        self.text_box = tk.Text(root, height=25, width=80)
        self.text_box.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        self.update_text_box()

    def create_search_interface(self):
        ttk.Label(self.root, text="Start Date (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = ttk.Entry(self.root)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        ttk.Label(self.root, text="End Date (DD-MM-YYYY):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_date_entry = ttk.Entry(self.root)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        ttk.Label(self.root, text="Committer Name:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.committer_name_entry = ttk.Entry(self.root)
        self.committer_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        ttk.Button(self.root, text="Search Commits", command=self.search_commits).grid(row=3, column=0, pady=10, sticky="we")
        ttk.Button(self.root, text="Clear Filters", command=self.clear_filters).grid(row=3, column=1, pady=10, sticky="we")

    def clear_filters(self):
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.committer_name_entry.delete(0, tk.END)
        self.search_commits()  # Trigger a search to display all commits

    def search_commits(self):
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        committer_name = self.committer_name_entry.get()

        try:
            start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date() if end_date_str else None

            if end_date and start_date and end_date < start_date:
                messagebox.showwarning("Aviso", "A data de fim não pode ser anterior à data de início.")
                return

        except ValueError:
            messagebox.showwarning("Aviso", "Formato de data inválido. Utilize o formato DD/MM/YYYY.")
            return

        filtered_commits = []
        for commit in self.commits:
            commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ").date()
            if (not start_date or commit_date >= start_date) and \
               (not end_date or commit_date <= end_date) and \
               (not committer_name or committer_name.lower() in commit["commit"]["committer"]["name"].lower()):
                filtered_commits.append(commit)

        self.text_box.delete(1.0, tk.END)

        if not filtered_commits:
            self.text_box.insert(tk.END, "Nenhum commit correspondente encontrado.\n")
        else:
            self.update_text_box(filtered_commits)

    def update_text_box(self, commits=None):
        commits_to_display = commits or self.commits
        text = ""
        for commit in commits_to_display:
            commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = commit_date.strftime("%d/%m/%Y %H:%M:%S")
            text += f'Commiter name: {commit["commit"]["committer"]["name"]}\n'
            text += f'Commit message: {commit["commit"]["message"]}\n'
            text += f'Commit date: {formatted_date}\n\n'
        self.text_box.insert(tk.END, text + '\n')
        self.text_box.yview(tk.END)

    def on_close(self):
        self.commit_searcher.lister_closed()
        self.root.destroy()
            

if __name__ == "__main__":
    root = tk.Tk()
    app = CommitSearcher(root)
    root.mainloop()
