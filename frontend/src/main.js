import './style.css'

// 1. Monta o visual da página (HTML injetado via JS)
document.querySelector('#app').innerHTML = `
  <div>
    <h1>MoneyLayer 2.0 💸</h1>
    <div class="card">
      <button id="btn-enviar" type="button">Testar Integração com Backend</button>
    </div>
    <p id="resultado" style="margin-top: 20px; font-weight: bold; color: #646cff;">
      Aguardando ação...
    </p>
  </div>
`

// 2. Adiciona a inteligência no botão
document.querySelector('#btn-enviar').addEventListener('click', async () => {
  const display = document.querySelector('#resultado');
  display.innerText = "Enviando dados para o Python...";

  try {
    // Faz a chamada para a sua API (o mesmo que o curl fazia)
    const resposta = await fetch('http://127.0.0.1:8000/transacoes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        descricao: "Transação via Frontend",
        valor: 250.00,
        tipo: "teste_interface"
      })
    });

    const dados = await resposta.json();
    
    // Mostra a mensagem que veio do Python na tela
    display.innerText = "Sucesso: " + dados.mensagem;
    display.style.color = "#00ff88"; // Fica verde se der certo

  } catch (erro) {
    display.innerText = "Erro: O Backend parece desligado!";
    display.style.color = "red";
    console.error(erro);
  }
});