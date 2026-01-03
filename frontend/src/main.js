import './style.css'

document.querySelector('#app').innerHTML = `
  <div>
    <h1>MoneyLayer 2.0 💸</h1>
    
    <div class="card" style="display: flex; flex-direction: column; gap: 10px; max-width: 300px; margin: 0 auto;">
      <input type="text" id="input-desc" placeholder="Ex: Coxinha" style="padding: 10px; border-radius: 5px; border: 1px solid #ccc;">
      
      <input type="text" id="input-valor" placeholder="Ex: 10.50" style="padding: 10px; border-radius: 5px; border: 1px solid #ccc;">
      
      <button id="btn-salvar" type="button" style="background-color: #646cff; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">Trancar no Backend</button>
    </div>

    <p id="resultado" style="margin-top: 20px; font-weight: bold; color: #888;">
      Aguardando...
    </p>
  </div>
`

// Lógica Inteligente
document.querySelector('#btn-salvar').addEventListener('click', async () => {
  const display = document.querySelector('#resultado');
  
  // 1. PEGAR OS DADOS DA TELA
  const desc = document.querySelector('#input-desc').value;
  let valorTexto = document.querySelector('#input-valor').value;

  // 2. CORRIGIR A VÍRGULA (Transforma 0,21 em 0.21)
  valorTexto = valorTexto.replace(',', '.');
  const valorFinal = parseFloat(valorTexto);

  // Validação simples
  if (!desc || isNaN(valorFinal)) {
    display.innerText = "❌ Erro: Preencha descrição e valor (número) corretamente!";
    display.style.color = "red";
    return;
  }

  display.innerText = "Enviando...";
  display.style.color = "#FFD700"; // Amarelo (Gold)

  try {
    // 3. ENVIAR PARA O PYTHON (LINK DA NUVEM CORRIGIDO)
    // ATENÇÃO: Estou usando o link que vimos nos logs do seu deploy anterior
    const resposta = await fetch('https://moneylayer-2-0.onrender.com/transacoes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        descricao: desc,
        valor: valorFinal,
        tipo: "despesa" 
      })
    });

    // 4. VERIFICAR A RESPOSTA
    if (resposta.ok) {
      const dados = await resposta.json();
      display.innerText = `✅ Sucesso! ID: ${dados.dados.id} salvo no banco!`;
      display.style.color = "#00ff88";
      
      // Limpar os campos
      document.querySelector('#input-desc').value = "";
      document.querySelector('#input-valor').value = "";
    } else {
      display.innerText = "❌ Erro no Backend: " + resposta.status;
      display.style.color = "red";
    }

  } catch (erro) {
    display.innerText = "❌ Erro de Conexão (Verifique CORS ou Backend)";
    display.style.color = "red";
    console.error(erro);
  }
});
