# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 15:26:01 2018

@author: user
"""
############################# LA FONTAINE: THE SOCIAL NETWORK

import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 50)
import os
import seaborn
from seaborn import color_palette, set_style

os.chdir(r"C:\Users\user\Desktop\fontaine")

df     = pd.read_excel('la fontaine stats v2 - toupload.xlsx', sheet_name="fables")
taxons = pd.read_excel('la fontaine stats v2 - toupload.xlsx', sheet_name="taxons")

# vecteurs pour les subsets de personnages
personnages = df.columns[4:]
animaux     = personnages[2:]
hommes      = ['homme']
inanimes    = ['chene', 'roseau', 'arbre', 'pot', 'montagne', 'lime', 'cierge', 'buisson']


# classement des animaux par total ou score
df[personnages].sum(axis=0).sort_values() # on a aussi sort_index() pour trier les noms de lignes
df[animaux].count().sort_values()
# classement des livres de fables par nombre de fables
df.groupby("livre").agg({'num':lambda x:max(x)})
# df.groupby("livre").max().num # autre option plus simple!
# nombre total
df.id.max()
len(personnages)-10 # exceptions: HOMME DIEUX CHENE ROSEAU ARBRE POT MONTAGNE LIME CIERGE BUISSON 
# mediane du nombre de personnages principaux par fable
df[animaux].count(axis=1).describe()
df[animaux].count(axis=1)
nan=np.nan
# le nombre moyen de persos dans les fables qui ne comprennent pas d'hommes ou de dieux
df.query("homme!=homme")[animaux].count(axis=1).describe() # asture pour filtrer les NaNon veut les fables ou il n'y a pas d'homme

# function that sums only positive numbers
def pos_sum(array):
    temp = array[~np.isnan(array)]
    return temp[temp>0].sum()
def neg_sum(array):
    temp = array[~np.isnan(array)]
    return temp[temp<0].sum()
# scores d'animaux et taxons


df2 = df[animaux]
result = df2.count(axis=0).to_frame("citations")
result["score"] = df2.sum(axis=0)
result["pos_score"] = df2.apply(pos_sum)
result["neg_score"] = df2.apply(neg_sum)
result.reset_index(inplace=True)
result.rename(columns={'index':'animal'}, inplace=True)
scores = pd.merge(result, taxons, how='left', left_on='animal', right_on='animal')
scores.groupby('carnivore').sum()
# convertir les scores en categories
scores["score_cat"]=pd.cut(scores.score, [-100,-0.1,0.1,100], labels=["negative", "neutral", "positive"])
scores["score_cat"]=pd.cut(scores.score, [-100,-5,-2,-0.1,0.1,2,5,100], labels=["01_veryneg", "02_mediumneg", "03_littleneg", "04_neutral", "05_littlepos", "06_mediumpos", "07_verypos"])
############ PLOT AVEC R Desole...
#scores.to_csv("scores.csv")
#library(tidyverse); library(RColorBrewer)
#setwd("C:/Users/user/Desktop/fontaine")
#scores=read.csv('scores.csv', stringsAsFactors = FALSE)
#scores %>% arrange(desc(citations)) %>% slice(1:50) %>% ggplot(.) +
#  aes(x=animal, y=citations, fill=taxon_classe) +
#  geom_bar(stat='identity') + theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
#  xlim(scores %>% arrange(desc(citations)) %>% slice(1:50) %>% pull(animal)) + ylab("Nombre d'apparitions dans les fables") +
#  scale_fill_manual(values = colorRampPalette(brewer.pal(8, "Set3"))(8))
### graphs?
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import networkx as nx
import csv


# create the graph dataset
    # fonction pour transformer toutes nos relations en 0 et 1 (0=pas de relation, 1=relation)
def transform01(dataframe):
    return round(((dataframe+10)/100)+1).fillna(0)
def sortdict(dico, reverse_choice=True):
    return sorted(dico.items(), key=lambda x:x[1], reverse=reverse_choice)
def colormap(g, attribute, seaborn_palette='RdBu_r'):
    attributes = [g.node[label][attribute] for label in g.node]
    attributes_unique = sorted(list(set(attributes)), reverse=True)
    num_values=len(attributes_unique)
    palette=color_palette(seaborn_palette, num_values).as_hex()
    # remplacé par:
    # palette = ["#9ee314", "#B9B9B9", "#a22309"]
    color_map = dict(zip(attributes_unique, palette))
    node_colors = [color_map[attribute] for attribute in attributes]
    return node_colors, color_map, palette
#### CHOIX SUBET D'ANIMAUX
choix_personnages = animaux
df2 = df[choix_personnages]    

# PREPARE ADJECENCY MATRIX
dfg  = transform01(df2)
# dfgw = get_weights(dfg).query('Weights>0') # not used in this version
from itertools import combinations
l = len(dfg.columns)
# empty matrice
mat = np.zeros((l,l))
for i, row in dfg.iterrows():
    positions = np.where(row)[0]
    if len(positions)>1:
        for comb in combinations(positions,2):
            i,j = comb
            mat[i,j] += 1
            mat[j,i] += 1
mat2=pd.DataFrame(mat)
mat2.columns = choix_personnages
mat2.set_index(choix_personnages, inplace=True)

################## CREATE GRAPH
G = nx.from_pandas_adjacency(mat2)
print(nx.info(G))
import random
random.seed(123)
pos=nx.spring_layout(G, iterations=100)
label_mapping = dict(zip(G.nodes(), scores.score_cat))
label_mapping_taxons = dict(zip(G.nodes(), scores.taxon_classe))
weights = [G[u][v]['weight']**1.5 for u,v in G.edges()] # pour epaisseur des edges
nx.set_node_attributes(G, name='score_cat', values=label_mapping)
nx.set_node_attributes(G, name='taxon_classe', values=label_mapping_taxons)
node_colors, color_map, palette = colormap(G, "taxon_classe", seaborn_palette="muted")
node_colors, color_map, palette = colormap(G, "score_cat")
%matplotlib qt
set_style('white'); plt.figure(figsize=(10,10)); plt.axis('off')
nx.draw(G, pos=pos, with_labels = True, 
        font_size=18, 
        alpha=0.8, 
        edge_color="grey",
        # node_size = [v * 100 for v in dict(nx.degree(G)).values()], # lier taille au degré
        node_size = scores.citations*100, # lier taille au nombre de citations
        node_color = node_colors,
        width = weights)

#### analysis of the graph

for elt in sortdict(nx.closeness_centrality(G))[:10]:
    print(elt)
print("\n")
for elt in sortdict(nx.degree_centrality(G))[:10]:
    print(elt)
print("\n")
for elt in sortdict(nx.betweenness_centrality(G))[:10]:
    print(elt)
print("\n")
for elt in sortdict(nx.eigenvector_centrality(G))[:10]:
    print(elt)

########## prediction liens futurs
jac = nx.jaccard_coefficient(G)
pred_jac = {}
for u, v, p in jac:
    pred_jac[(u, v)] = p
sortdict(pred_jac)[0:50]

############################### 
# retour aux analyses sur le modele lineaire d'explication du score net
import statsmodels.formula.api as smf
import statsmodels.api as sm
scores.score.hist()
# check normality of y


pd.get_dummies(scores.taxon_classe).sum(axis=0)
dummies = pd.get_dummies(scores.taxon_classe)[["insectes", "mammiferes", "objet", "oiseaux", "vegetaux", "reptiles"]]
scores_tomodel = scores.join(dummies)
scores_tomodel = scores # si on gere les facteurs avec C()
myformula = 'score ~ citations + domestique + carnivore + herbivore + insectes + mammiferes + objet + oiseaux + vegetaux + reptiles'
myformula = 'score ~ domestique + carnivore + herbivore + insectes + mammiferes + oiseaux + vegetaux + reptiles'
myformula = 'score ~ domestique*herbivore + carnivore + C(taxon_classe) - 1'
myformula = 'score ~ domestique:herbivore + carnivore'
myformula = 'score ~ domestique*herbivore + carnivore + taxon_classe'
model1 = smf.ols(formula=myformula, data=scores_tomodel).fit()
print(model1.summary2())


from sklearn.datasets import load_boston
import pandas as pd
import numpy as np
import statsmodels.api as sm
import patsy # model matrices for interactions and stuff

y, X =patsy.dmatrices(myformula, scores, return_type="dataframe")

####################### chiant...
def stepwise_selection(X, y, 
                       initial_list=[], 
                       threshold_in=0.01, 
                       threshold_out = 0.05, 
                       verbose=True):
    """ Perform a forward-backward feature selection 
    based on p-value from statsmodels.api.OLS
    Arguments:
        X - pandas.DataFrame with candidate features
        y - list-like with the target
        initial_list - list of features to start with (column names of X)
        threshold_in - include a feature if its p-value < threshold_in
        threshold_out - exclude a feature if its p-value > threshold_out
        verbose - whether to print the sequence of inclusions and exclusions
    Returns: list of selected features 
    Always set threshold_in < threshold_out to avoid infinite looping.
    See https://en.wikipedia.org/wiki/Stepwise_regression for the details
    """
    included = list(initial_list)
    while True:
        changed=False
        # forward step
        excluded = list(set(X.columns)-set(included))
        new_pval = pd.Series(index=excluded)
        for new_column in excluded:
            model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included+[new_column]]))).fit()
            new_pval[new_column] = model.pvalues[new_column]
        best_pval = new_pval.min()
        if best_pval < threshold_in:
            best_feature = new_pval.argmin()
            included.append(best_feature)
            changed=True
            if verbose:
                print('Add  {:30} with p-value {:.6}'.format(best_feature, best_pval))

        # backward step
        model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included]))).fit()
        # use all coefs except intercept
        pvalues = model.pvalues.iloc[1:]
        worst_pval = pvalues.max() # null if pvalues is empty
        if worst_pval > threshold_out:
            changed=True
            worst_feature = pvalues.argmax()
            included.remove(worst_feature)
            if verbose:
                print('Drop {:30} with p-value {:.6}'.format(worst_feature, worst_pval))
        if not changed:
            break
    return included


X.rename(columns={'domestique:herbivore':'domestiqueXherbivore'}, inplace=True)
X.rename(columns={'domestique:carnivore':'domestiqueXcarnivore'}, inplace=True)
X.rename(columns={'domestique:herbivore:carnivore':'triple'}, inplace=True)

result = stepwise_selection(X, y, threshold_out=0.1, threshold_in=0.1)

print('resulting features:')
print(result)

#final model
myformula = 'score ~ domestique:herbivore + carnivore'
model2= smf.ols(formula=myformula, data=scores_tomodel).fit()
print(model2.summary2())

from scipy import stats
stats.shapiro((model2.fittedvalues-scores.score))









