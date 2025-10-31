# 📊 Dashboard Interativo de E-commerce

Este projeto apresenta um **dashboard interativo** desenvolvido em **Python**, utilizando **Dash** e **Plotly**, para análise exploratória de dados de e-commerce.  
O objetivo é permitir a visualização dinâmica de métricas de produtos, como **preço, nota, desconto e vendas**, de forma intuitiva e responsiva.

---

## 🚀 Demonstração Online

Acesse o app publicado no Render:  
👉 https://dashboards-em-python.onrender.com

> ⚠️ *Nota:* no plano gratuito do Render, o app pode levar até **1 minuto** para “acordar” no primeiro acesso.

---

## 🧩 Tecnologias Utilizadas

- **Python 3.12**
- **Dash** – Criação da interface web interativa  
- **Plotly** – Visualizações gráficas  
- **Pandas** – Manipulação e tratamento de dados  
- **NumPy / SciPy** – Cálculos estatísticos e densidades  
- **Statsmodels** – Regressões lineares  
- **Gunicorn** – Servidor WSGI para deploy no Render  

---

## 📁 Estrutura do Projeto

Dashboards-em-Python-/
├── graficos_interativos.py # Código principal do dashboard
├── ecommerce_estatistica.csv # Base de dados usada na análise
├── requirements.txt # Lista de dependências do projeto
├── Procfile # Comando usado para inicializar o servidor no Render
└── README.md # Este arquivo

🧠 Principais Funcionalidades

✅ Filtros Interativos:

Filtro de gênero/categoria para o histograma de notas

Slider de faixa de preço para o gráfico de dispersão

✅ Gráficos Estáticos e Dinâmicos:

Dispersão Preço vs Nota

Histograma de Notas

Matriz de Correlação

Top 10 Marcas mais vendidas

Distribuição de produtos por faixa de preço

Densidade dos descontos

Regressão entre Preço e Desconto

✅ Visual Clean e Responsivo

Layout organizado com dcc.Graph e componentes Dash

🧾 Licença

Este projeto é distribuído sob a licença MIT, permitindo uso livre para fins acadêmicos e profissionais.
Sinta-se à vontade para clonar, testar e expandir o dashboard!

👨‍💻 Autor

Guilherme Rezende
📬 github.com/gui-rezende

💡 Projeto desenvolvido para fins acadêmicos e aprendizado de Dash + Plotly + Deploy no Render.
