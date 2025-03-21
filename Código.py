import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import mplcursors
import matplotlib

# Configurar backend interativo
matplotlib.use("TkAgg")

#Carregar os dados
df = pd.read_csv('violencia_mulher.csv', delimiter=';')

#Analisando os dados 
df.columns
df['Frequência'].unique()
df['Relação_vítima_suspeito'].unique()

# Categorizar a relação como 'Familiar' ou 'Não Familiar'
familiar_relations = [
    'EX-COMPANHEIRO(A)', 'ESPOSA(O)', 'TIO(A)', 'COMPANHEIRO(A)',
    'FILHO(A)', 'IRMÃO(Ã)', 'MÃE', 'PAI', 'NETO(A)', 'SOBRINHO(A)',
    'GENRO/NORA', 'CUNHADO(A)', 'PADRASTO/MADRASTA', 'PRIMO(A)', 'AVÔ(Ó)',
    'SOGRO(A)', 'ENTEADO(A)', 'PADRINHO/MADRINHA', 'BISAVÔ(Ó)'
]

df['Tipo_de_relacao'] = df['Relação_vítima_suspeito'].apply(
    lambda x: 'Familiar' if x in familiar_relations else 'Não Familiar'
)

# Filtrar dados e organizar frequências
filtered_df = df[['Relação_vítima_suspeito', 'Tipo_de_relacao', 'Frequência']].dropna()

# Contar frequências por categoria
frequency_categories = ['DIARIAMENTE', 'SEMANALMENTE', 'MENSALMENTE', 'OUTROS']
filtered_df['Frequencia_categoria'] = filtered_df['Frequência'].apply(
    lambda x: next((freq for freq in frequency_categories if freq in x.upper()), 'OUTROS')
)

# Agrupar e calcular frequências detalhadas
frequency_count = filtered_df.groupby(['Relação_vítima_suspeito', 'Frequencia_categoria']).size().unstack(fill_value=0)

# Criar hover_text com detalhes de frequência
hover_text = {
    rel: ', '.join([f"{cat}: {count}" for cat, count in frequency_count.loc[rel].items() if count > 0])
    for rel in filtered_df['Relação_vítima_suspeito'].unique()
}

# Obter contagem total por relação
relacao_frequencia = filtered_df['Relação_vítima_suspeito'].value_counts()

# Dividir as relações em familiares e não familiares
familiares = [rel for rel in relacao_frequencia.index if rel in familiar_relations]
nao_familiares = [rel for rel in relacao_frequencia.index if rel not in familiar_relations]

# Função para criar e exibir grafos
def exibir_grafo(interativo):
    grafo_relacao = nx.Graph()

    # Adicionar nós ao grafo
    for relacao, frequencia in relacao_frequencia.items():
        grafo_relacao.add_node(relacao, weight=frequencia, hover_info=hover_text.get(relacao, ''))

    # Adicionar arestas entre nós do mesmo grupo
    for i, relacao1 in enumerate(relacao_frequencia.index):
        for relacao2 in relacao_frequencia.index[i + 1:]:
            if (relacao1 in familiares and relacao2 in familiares) or (relacao1 in nao_familiares and relacao2 in nao_familiares):
                grafo_relacao.add_edge(relacao1, relacao2, weight=1)

    # Visualizar o grafo
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(grafo_relacao, seed=42, k=1.3)

    # Tamanho e cor dos nós
    node_weights = nx.get_node_attributes(grafo_relacao, 'weight')
    node_size = [node_weights[node] * 0.2 for node in grafo_relacao.nodes()]
    node_colors = ['lightcoral' if node in familiares else 'lightblue' for node in grafo_relacao.nodes()]

    # Desenhar o grafo
    nodes = nx.draw_networkx_nodes(
        grafo_relacao, pos, node_size=node_size, node_color=node_colors, alpha=0.8
    )
    nx.draw_networkx_edges(grafo_relacao, pos, edge_color='gray', alpha=0.7)
    nx.draw_networkx_labels(grafo_relacao, pos, font_size=8, font_weight='bold')

    # Adicionar legenda
    legend_labels = {'lightcoral': 'Familiar', 'lightblue': 'Não Familiar'}
    for color, label in legend_labels.items():
        plt.scatter([], [], c=color, alpha=0.7, s=100, label=label)
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, loc='upper right', fontsize=10)

    # Adicionar título
    title_suffix = 'Interativo' if interativo else 'Não Interativo'
    plt.title(f'"Grafo da Frequência das Agressões contra Mulher: Agressor Familiar vs. Não Familiar" ({title_suffix})', fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Configurar interatividade
    if interativo:
        cursor = mplcursors.cursor(nodes, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            node_index = list(grafo_relacao.nodes())[sel.index]
            sel.annotation.set_text(
                f"Relação: {node_index}\nFrequências: {grafo_relacao.nodes[node_index]['hover_info']}"
            )

    # Exibir o gráfico sem bloquear o código
    plt.show(block=False)

# Abrir os dois grafos em janelas separadas
exibir_grafo(interativo=False)  # Primeiro o não interativo
exibir_grafo(interativo=True)  # Depois o interativo

# Finalizar a execução sem fechar as janelas
exit()
