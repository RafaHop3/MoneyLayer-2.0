# --- ROTA DE RELATÓRIOS DINÂMICOS ---

@app.route('/reports')
@login_required
def reports():
    company = get_user_company(current_user.id)
    if not company:
        flash("Registre sua empresa primeiro!")
        return redirect(url_for('index'))
    
    # Mock de dados (Em breve buscaremos do banco/Stripe)
    # Se for Startup, mostramos Runway. Se for MEI, faturamento.
    labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
    
    if company.company_type == 'Startup':
        data_values = [80, 70, 65, 50, 45, 40] # Burn rate descendente
        chart_label = "Runway (%)"
    else:
        data_values = [1200, 2100, 1800, 3200, 4100, 5000]
        chart_label = "Faturamento Mensal (R$)"
    
    return render_template('reports.html', 
                           company=company, 
                           labels=labels, 
                           data_values=data_values,
                           chart_label=chart_label)