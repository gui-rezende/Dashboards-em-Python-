import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import numpy as np
from scipy.stats import gaussian_kde
import os

cores = ['#2E86AB', '#F6C85F', '#6F4E7C', '#9FD356', '#CA472F']

# --- CARREGAMENTO DE DADOS REAIS ---
try:
	df = pd.read_csv("ecommerce_estatistica.csv")
except FileNotFoundError:
	print("ERRO: Arquivo 'ecommerce_estatistica.csv' não encontrado.")
	# Em um ambiente real, você poderia ter uma mensagem de erro mais robusta
	# ou um fallback, mas aqui forçamos a leitura do arquivo fornecido.
	exit()
# --- FIM CARREGAMENTO DE DADOS ---

# Pré-processamento inicial
df = df.drop(columns=['Unnamed: 0'])
df = df.drop_duplicates()
df["Preço"] = pd.to_numeric(df["Preço"], errors="coerce")
df["Desconto"] = pd.to_numeric(df["Desconto"], errors="coerce")
df = df.dropna(subset=["Preço", "Desconto"])  # Remove linhas com Preço ou Desconto nulo

# Valores de Preço para o Slider (
MIN_PRICE = 25
MAX_PRICE = 327  # Arredondado para cima
STEP = 10


# filtra colunas minmax ou _cod para correlação
def get_corr_df(df):
	num_cols = [c for c in df.select_dtypes(include="number").columns
				if c != "unnamed: 0" and not (c.endswith("MinMax") or c.endswith("_Cod"))]
	return df[num_cols]


# Gráfico de Dispersão (fig2) o alvo da interatividade
def cria_dispersao_dinamica(df_filtered, min_p, max_p):
	fig2 = px.scatter(
		df_filtered,
		x="Preço",
		y="Nota",
		color="Gênero",
		hover_data=["Título"],
		labels={"Preço": "Preço$", "Nota": "Nota média"},
		title=f"Dispersão Preço vs Nota (Filtrado: R${min_p:.2f} a R${max_p:.2f})",
		template="plotly"
	)
	fig2.update_layout(
		plot_bgcolor="white",
		xaxis=dict(showgrid=True, gridcolor="lightgreen"),
		yaxis=dict(showgrid=True, gridcolor="lightgreen"),
		legend_title_text="Gênero",
	)
	return fig2


# Função para criar o gráfico de Histograma (fig1) dinamicamente
def cria_histograma_dinamico(df_filtered):
	fig1 = px.histogram(
		df_filtered,
		x='Nota',
		nbins=20,
		color_discrete_sequence=cores,
		color="Gênero",
		title='Distribuição das notas dos produtos',
		labels={"Nota": "Nota do produto", "count": "frequência"},
		barmode='overlay',
		template="simple_white"
	)
	fig1.update_layout(
		bargap=0.5,
		plot_bgcolor="white",
		xaxis=dict(showgrid=True, gridcolor="lightgray"),
		yaxis=dict(showgrid=True, gridcolor="lightgray"),
	)
	return fig1


# Criação dos gráficos estáticos (fig3, fig4, fig5, fig6, fig7)
def cria_graficos_estaticos(df):
	# fig3 - Matriz de Correlação
	corr_df = get_corr_df(df)
	corr = corr_df.corr().round(2)
	fig3 = px.imshow(corr, text_auto=True, aspect="auto",
					 color_continuous_scale="Viridis",
					 title="Matriz de Correlação", )

	# fig4 - Top 10 Marcas
	rank = (df.groupby("Marca", as_index=False)["Qtd_Vendidos_Cod"].sum().sort_values("Qtd_Vendidos_Cod",
																					  ascending=False).head(10))
	fig4 = px.bar(
		rank,
		x="Marca",
		y="Qtd_Vendidos_Cod",
		text="Qtd_Vendidos_Cod",
		color="Marca",
		title="Top 10 marcas por quantidade vendida",
		labels={"Qtd_Vendidos_Cod": "Quantidade vendida (proxy)", "Marca": "Marca"}
	)
	fig4.update_traces(texttemplate="%{text:.0f}", textposition="outside")
	fig4.update_layout(
		plot_bgcolor="white",
		xaxis=dict(showgrid=False),
		yaxis=dict(showgrid=True, gridcolor="lightgray"),
		showlegend=False,
	)

	# fig5 - Distribuição de Preços (Pizza)
	preco_max = df["Preço"].max(skipna=True)
	bins_base = [0, 50, 100, 150, 200, 300, 500, preco_max]
	bins = sorted(set(bins_base))
	if len(bins) >= 2 and np.isclose(bins[-1], bins[-2]):
		bins[-1] = bins[-1] + 1
	labels = [
		f"R${bins[i]:.0f}–R${bins[i + 1]:.0f}" if i < len(bins) - 2 else f"Acima de R${bins[i]:.0f}"
		for i in range(len(bins) - 1)
	]
	df["Faixa_Preço"] = pd.cut(df["Preço"], bins=bins, labels=labels, include_lowest=True)
	dist = df["Faixa_Preço"].value_counts().reset_index()
	dist.columns = ["Faixa_Preço", "Qtd_Produtos"]

	fig5 = px.pie(
		dist,
		names="Faixa_Preço",
		values="Qtd_Produtos",
		title="Distribuição de produtos por faixa de preço",
		color_discrete_sequence=px.colors.qualitative.Set2,
		hole=0.4,
	)
	fig5.update_traces(textinfo="percent+label", textfont_size=13)

	# fig6 - Densidade dos Descontos
	dados = df["Desconto"].dropna()
	kde = gaussian_kde(dados)
	x_vals = np.linspace(dados.min(), dados.max(), 200)
	y_vals = kde(x_vals)
	densidade_df = pd.DataFrame({"Desconto": x_vals, "Densidade": y_vals})

	fig6 = px.line(
		densidade_df,
		x="Desconto",
		y="Densidade",
		title="Densidade dos descontos dos produtos",
		labels={"Desconto": "Desconto %", "Densidade": "Densidade"}
	)
	fig6.add_scatter(
		x=x_vals, y=y_vals,
		fill="tozeroy", mode="none",
		fillcolor="rgba(99, 110, 250, 0.4)"
	)
	fig6.update_layout(
		plot_bgcolor="white",
		xaxis=dict(showgrid=True, gridcolor="lightgray"),
		yaxis=dict(showgrid=True, gridcolor="lightgray"),
	)

	# fig7 - Regressão Preço vs Desconto
	df_reg = df.dropna(subset=["Preço", "Desconto"])
	fig7 = px.scatter(
		df_reg,
		x="Preço",
		y="Desconto",
		trendline="ols",
		trendline_color_override="red",
		title="Relação entre preço e desconto dos produtos",
		labels={"Preço": "Preço $", "Desconto": "Desconto %"},
		color_discrete_sequence=["#1f77b4"]
	)
	fig7.update_layout(
		plot_bgcolor="white",
		xaxis=dict(showgrid=True, gridcolor="lightgray"),
		yaxis=dict(showgrid=True, gridcolor="lightgray"),
	)

	return fig3, fig4, fig5, fig6, fig7


def cria_app(df):
	app = Dash(__name__)

	# Opções para o Dropdown de Gênero
	genero_options = [{'label': 'Todos', 'value': 'Todos'}] + \
					 [{'label': g, 'value': g} for g in df['Gênero'].unique() if pd.notna(g)]

	# Gráficos estáticos (todos, exceto o fig1 e fig2)
	fig3, fig4, fig5, fig6, fig7 = cria_graficos_estaticos(df)

	# Gráfico de Dispersão inicial (fig2)
	fig2_initial = cria_dispersao_dinamica(df, MIN_PRICE, MAX_PRICE)

	app.layout = html.Div(
		children=[
			html.H1("Dashboard Interativo de E-commerce", style={'textAlign': 'center'}),

			# --- INTERAÇÃO 1: FILTRO POR GÊNERO (Histograma - fig1) ---
			html.Div([
				html.H3("Filtro 1: Distribuição de Notas por Gênero/Categoria"),
				html.Label("Selecione um Gênero/Categoria para filtrar o Histograma de Notas:"),
				dcc.Dropdown(
					id='genero-dropdown',
					options=genero_options,
					value='Todos',
					clearable=False
				),
				html.Div(id='histograma-container', style={'width': '100%'}),
			], style={'padding': '20px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

			# --- INTERAÇÃO 2: FILTRO POR PREÇO (Slider - Afeta Dispersão - fig2) ---
			html.Div([
				html.H3("Filtro 2: Relação Preço vs Nota por Faixa de Preço"),
				html.Label(f"Selecione uma Faixa de Preço (R$):"),
				dcc.RangeSlider(
					id='preco-slider',
					min=MIN_PRICE,
					max=MAX_PRICE,
					step=STEP,
					value=[MIN_PRICE, MAX_PRICE],
					marks={i: f'R${i}' for i in range(MIN_PRICE, MAX_PRICE + STEP, 50)},
					tooltip={"placement": "bottom", "always_visible": True}
				),
				html.Div(id='dispersao-container', children=[dcc.Graph(figure=fig2_initial)]),
			], style={'padding': '20px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

			# --- GRÁFICOS ESTÁTICOS ---
			html.Div([
				dcc.Graph(figure=fig3, style={'width': '50%', 'display': 'inline-block'}),
				dcc.Graph(figure=fig4, style={'width': '50%', 'display': 'inline-block'}),
			], style={'display': 'flex'}),

			html.Div([
				dcc.Graph(figure=fig5, style={'width': '50%', 'display': 'inline-block'}),
				dcc.Graph(figure=fig6, style={'width': '50%', 'display': 'inline-block'}),
			], style={'display': 'flex'}),

			html.Div([
				dcc.Graph(figure=fig7, style={'width': '50%', 'display': 'inline-block'}),
			], style={'display': 'flex'}),
		])

	# --- CALLBACK 1: FILTRO POR GÊNERO (Histograma) ---
	@app.callback(
		Output('histograma-container', 'children'),
		[Input('genero-dropdown', 'value')]
	)
	def update_histograma(selected_genero):
		if selected_genero == 'Todos':
			df_filtered = df
		else:
			df_filtered = df[df['Gênero'] == selected_genero]

		fig1_updated = cria_histograma_dinamico(df_filtered)

		if selected_genero != 'Todos':
			fig1_updated.update_layout(title=f'Distribuição das notas dos produtos - Filtrado por: {selected_genero}')

		return dcc.Graph(figure=fig1_updated)

	# --- CALLBACK 2: FILTRO POR PREÇO (Dispersão) ---
	@app.callback(
		Output('dispersao-container', 'children'),
		[Input('preco-slider', 'value')]
	)
	def update_dispersao(price_range):
		min_p, max_p = price_range

		# Filtra o DataFrame
		df_filtered = df[(df['Preço'] >= min_p) & (df['Preço'] <= max_p)]

		# Cria o novo gráfico
		fig2_updated = cria_dispersao_dinamica(df_filtered, min_p, max_p)

		return dcc.Graph(figure=fig2_updated)

	return app


app = cria_app(df)
server = app.server

if __name__ == '__main__':
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050))
    )
