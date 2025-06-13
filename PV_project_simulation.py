import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ===================
# CONFIGURATION
# ===================
st.set_page_config(page_title="Simulation Photovoltaïque ☀️", layout="centered")

# ===================
# Titre
# ===================
st.title("☀️ Simulation d’un Système Photovoltaïque Résidentiel")

st.markdown("Simulez la production, le rendement et les coûts selon vos choix de panneaux, météo et nombre de modules.")

# ===================
# Entrées utilisateur
# ===================
panneau = st.selectbox(
    "🧱 Type de panneau solaire",
    ["Monocristallin", "Polycristallin", "Amorphe", "Hétérojonction", "Bifacial"]
)

meteo = st.radio("🌤️ Conditions météorologiques", ["Ensoleillé", "Nuageux", "Pluvieux"])

nb_panneaux = st.slider("🔢 Nombre de panneaux installés", 0, 25, 20)

# ===================
# Données de base
# ===================
surface_par_module = 1.7  # m²
surface_totale = surface_par_module * nb_panneaux
irradiation_marseille = 1824  # kWh/m²/an

facteur_meteo = {
    "Ensoleillé": 1.0,
    "Nuageux": 0.75,
    "Pluvieux": 0.55
}[meteo]

data = {
    "Monocristallin": {"rendement": 20.0, "prix": 1.20},
    "Polycristallin": {"rendement": 17.5, "prix": 1.00},
    "Amorphe": {"rendement": 10.0, "prix": 0.80},
    "Hétérojonction": {"rendement": 21.5, "prix": 1.50},
    "Bifacial": {"rendement": 19.5, "prix": 1.40}
}

# ===================
# Calculs
# ===================
rendement = data[panneau]["rendement"]
prix_watt = data[panneau]["prix"]

puissance_kWp = (rendement / 100) * surface_totale
production = puissance_kWp * irradiation_marseille * facteur_meteo
efficacite = production / (surface_totale or 1)
cout_total = puissance_kWp * 1000 * prix_watt

# Hypothèse de conso
conso_batiment = 8260  # kWh/an
autoconso = min(conso_batiment, production) * 0.9
injecte = max(0, production - autoconso)
reprise = max(0, conso_batiment - autoconso)

# ===================
# Résultats
# ===================
st.subheader("🔎 Résultats de simulation")

col1, col2 = st.columns(2)
col1.metric("Production estimée", f"{production:.0f} kWh/an")
col2.metric("Puissance installée", f"{puissance_kWp:.2f} kWc")

col1, col2 = st.columns(2)
col1.metric("Efficacité", f"{efficacite:.1f} kWh/m²/an")
col2.metric("Coût total", f"{cout_total:,.0f} €")

# ===================
# Graph 1 : Répartition de l’énergie
# ===================
st.subheader("⚡ Répartition énergétique")

fig1, ax1 = plt.subplots()
labels = ["Autoconsommée", "Injectée au réseau", "Reprise réseau"]
values = [autoconso, injecte, reprise]
colors = ["green", "orange", "red"]

ax1.bar(labels, values, color=colors)
ax1.set_ylabel("Énergie (kWh)")
ax1.set_title("Répartition annuelle de l'énergie")
ax1.grid(axis='y')
st.pyplot(fig1)

# ===================
# Graph 2 : Comparaison (optionnel)
# ===================
st.subheader("📊 Comparaison par type de panneau")

df = pd.DataFrame({
    'Type': list(data.keys()),
    'Rendement (%)': [v["rendement"] for v in data.values()],
    'kWp installable': [(v["rendement"] / 100) * surface_totale for v in data.values()],
    'Coût total (€)': [(v["rendement"] / 100) * surface_totale * 1000 * v["prix"] for v in data.values()],
})

df["Production (kWh/an)"] = df["kWp installable"] * irradiation_marseille * facteur_meteo
df["Efficacité (kWh/m²/an)"] = df["Production (kWh/an)"] / (surface_totale or 1)

tab1, tab2, tab3 = st.tabs(["Production", "Efficacité", "Coût"])

with tab1:
    fig, ax = plt.subplots()
    ax.bar(df["Type"], df["Production (kWh/an)"], color="seagreen")
    ax.set_title("Production annuelle")
    ax.set_ylabel("kWh/an")
    ax.grid(axis='y')
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots()
    ax.bar(df["Type"], df["Efficacité (kWh/m²/an)"], color="darkorange")
    ax.set_title("Efficacité énergétique")
    ax.set_ylabel("kWh/m²/an")
    ax.grid(axis='y')
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots()
    ax.bar(df["Type"], df["Coût total (€)"], color="steelblue")
    ax.set_title("Coût estimé")
    ax.set_ylabel("€")
    ax.grid(axis='y')
    st.pyplot(fig)

# ===================
# Footer
# ===================
st.markdown("---")
st.caption("📍 Simulation basée sur les données réelles de Marseille et les résultats PVsyst du projet S8.")

