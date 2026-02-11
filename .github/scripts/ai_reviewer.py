import os
import google.generativeai as genai
from github import Github

def ai_code_review():
    # Configurações
    gemini_key = os.getenv("GEMINI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    
    if not gemini_key or not github_token:
        print("Erro: GEMINI_API_KEY ou GITHUB_TOKEN não configurados.")
        return

    # Configurar Gemini
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Conectar ao GitHub
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    
    try:
        pr = repo.get_pull(int(pr_number))
    except Exception as e:
        print(f"Erro ao obter PR: {e}")
        return

    # Obter Diff
    diff_content = ""
    for file in pr.get_files():
        if file.patch:
            diff_content += f"File: {file.filename}\nDiff:\n{file.patch}\n\n"
    
    if not diff_content:
        print("Nenhum diff encontrado para analisar.")
        return

    # Prompt
    prompt = f"""
    Aja como um Engenheiro de Segurança Sênior (DevSecOps).
    Analise o seguinte código (diff de um Pull Request) em busca de:
    1. Vulnerabilidades de Segurança (OWASP Top 10), especialmente SQL Injection.
    2. Erros de lógica ou bugs potenciais.
    3. Code Smells e melhorias de qualidade.

    Se encontrar uma vulnerabilidade CRÍTICA (como SQL Injection), destaque-a claramente.
    Se o código estiver bom, apenas confirme.

    Código para análise:
    {diff_content}
    """

    # Gerar Review
    try:
        response = model.generate_content(prompt)
        review_comment = response.text
        
        # Postar Comentário no PR
        pr.create_issue_comment(f"## 🤖 AI Security Review\n\n{review_comment}")
        print("Review postado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao gerar/postar review: {e}")

if __name__ == "__main__":
    ai_code_review()
