content = """flask
gunicorn
stripe
psycopg2-binary
"""
with open("requirements.txt", "w") as f:
    f.write(content)
print("✅ Lista de dependências atualizada!")
