# 💰 Sistema Financeiro – Amazônia Engenharia

Sistema web completo para **gestão financeira de empresas**, desenvolvido com **Django + HTML + CSS + JavaScript**, focado em **Clientes, Jobs, Cobranças e Automação de Lembretes**.

Projeto desenvolvido com foco em **organização, controle financeiro e escalabilidade**.

🔗 Ideal para:
- Empresas de engenharia
- Prestadores de serviço
- Escritórios técnicos
- Freelancers

---

## 🚀 Funcionalidades

✅ Cadastro e gestão de **Clientes**  
✅ Controle de **Jobs / Serviços**  
✅ Sistema completo de **Cobranças**  
✅ Dashboard financeiro  
✅ Filtros por status (Pago, Pendente, Vencido)  
✅ Vínculo de Cliente ↔ Job ↔ Cobrança  
✅ Sistema de **modais interativos**  
✅ Estrutura pronta para **automação de WhatsApp e Email**  
✅ Área de **Configurações do sistema**  
🚧 Relatórios (em desenvolvimento)

---

## 🧱 Arquitetura do Projeto

- Backend: **Django 5+**
- Frontend: **HTML + CSS + JavaScript**
- Banco de dados: **SQLite (local)**
- Autenticação: **Sistema de usuários do Django**
- Organização por apps:
  - `clientes`
  - `jobs`
  - `cobrancas`
  - `dashboard`
  - `configuracoes`

---

## 🖼️ Interface do Sistema

✔️ Layout moderno  
✔️ Sidebar fixa  
✔️ Cards financeiros  
✔️ Modais interativos  
✔️ Filtros rápidos  
✔️ Feedback visual por status  

> Layout totalmente responsivo e preparado para evolução futura.

---

## ✅ Requisitos

- Python **3.10+**
- Pip

Verifique se estão instalados:

```bash
python --version
pip --version

🛠️ Como rodar o projeto localmente
1️⃣ Clonar o repositório
git clone https://github.com/GuilhermeSSantana/Controle_Amazonia.git
cd projeto_financeiro

2️⃣ Instalar dependências
pip install django

🗄️ Banco de dados

Execute exatamente nesta ordem:

python manage.py makemigrations
python manage.py migrate

👤 Criar usuário admin automaticamente
python manage.py loaddata admin_user.json

▶️ Rodar o servidor
python manage.py runserver



⚠️ Possíveis Erros Comuns

Se aparecer erro:

Invalid block tag 'endblock'


Verifique se o template segue exatamente esta estrutura:

{% extends "components/layout.html" %}
{% load static %}

{% block page_title %}Título{% endblock %}

{% block extra_head %}{% endblock %}

{% block content %}
{% endblock %}