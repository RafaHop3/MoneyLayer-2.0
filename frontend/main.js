    const API_URL = "https://psychic-fiesta-q76v46q4rq96fw54-8000.app.github.dev";

    document.getElementById('btnSalvar').addEventListener('click', async () => {
        const desc = document.getElementById('desc').value;
        const valor = document.getElementById('valor').value;

        // Envia os dados para o seu servidor Python (main.py)
        const res = await fetch(`${API_URL}/transacoes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                descricao: desc, 
                valor: parseFloat(valor), 
                tipo: 'saida' 
            })
        });

        if (res.ok) {
            alert("✅ Dado enviado! O Python já encriptou sua descrição.");
            document.getElementById('desc').value = '';
            document.getElementById('valor').value = '';
        }
    });