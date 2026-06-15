import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================================
# 1. CONFIGURATION DE LA PAGE
# =====================================================================
st.set_page_config(
    page_title="Tableau de bord commercial — LBFI", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# 2. FONCTIONS DE RENDU GRAPHIQUE (HTML/CSS PERSONNALISÉ)
# =====================================================================
def render_kpi_card(title, value, delta_n_minus_1, delta_n_plus_1=None, is_positive_n1=True, icon=""):
    """
    Génère une carte KPI dont tout le fond change de couleur en fonction de l'indicateur N-1.
    Vert doux si positif, Rouge doux si négatif.
    """
    # Couleurs de fonds et de bordures adaptées (pastels professionnels)
    bg_color = "#eaf5e5" if is_positive_n1 else "#fce8e6"
    border_color = "#81c995" if is_positive_n1 else "#f28b82"
    
    card_html = f"""
    <div style="
        background-color: {bg_color};
        border: 1px solid {border_color};
        padding: 18px;
        border-radius: 6px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.02);
        text-align: left;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        height: 100%;
    ">
        <div style="color: #5f6368; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">
            {icon} {title}
        </div>
        <div style="color: #202124; font-size: 1.85rem; font-weight: bold; margin: 0 0 12px 0; white-space: nowrap;">
            {value}
        </div>
    """
    
    # Gestion des couleurs pour les deltas inférieurs
    delta_style_n1 = "color: #137333;" if is_positive_n1 else "color: #c5221f;"
    card_html += f"<div style='font-size: 0.8rem; font-weight: 500; white-space: nowrap;'>"
    card_html += f"<span style='{delta_style_n1}'>{delta_n_minus_1}</span>"
    
    if delta_n_plus_1:
        # Couleur dynamique pour le delta N+1 s'il est présent
        is_pos_n2 = "+" in delta_n_plus_1 or "↗" in delta_n_plus_1 or "pts" in delta_n_plus_1 and "-" not in delta_n_plus_1
        if "↘" in delta_n_plus_1 or "-" in delta_n_plus_1:
            is_pos_n2 = False
        delta_style_n2 = "color: #137333;" if is_pos_n2 else "color: #c5221f;"
        card_html += f" <span style='color: #bdc1c6;'>|</span> <span style='{delta_style_n2}'>{delta_n_plus_1}</span>"
        
    card_html += "</div></div>"
    st.markdown(card_html, unsafe_allow_html=True)

def render_operator(symbol, height="120px", font_size="2.8rem"):
    """
    Affiche un opérateur mathématique parfaitement centré verticalement dans sa colonne.
    """
    st.markdown(
        f"""
        <div style="
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: {height}; 
            font-size: {font_size}; 
            font-weight: bold; 
            color: #202124;
            margin: 0;
            padding: 0;
        ">
            {symbol}
        </div>
        """, 
        unsafe_allow_html=True
    )

# =====================================================================
# 3. CHARGEMENT ET TRAITEMENT DES DONNÉES ORIGINELLES
# =====================================================================
@st.cache_data
def load_data():
    # Simulation du chargement de données réelles présent dans votre script
    # Remplacer cette section par vos fonctions réelles de lecture de fichiers (ex: pd.read_excel, SQL etc.)
    np.random.seed(42)
    years = [2024, 2025, 2026]
    months = list(range(1, 13))
    
    data_list = []
    for y in years:
        for m in months:
            devis_emis = np.random.randint(80, 150)
            taux_vol = np.random.uniform(0.35, 0.55)
            commandes = int(devis_emis * taux_vol)
            panier_tout = np.random.randint(3500, 5000)
            panier_signe = np.random.randint(2200, 3200)
            
            ca_devise = devis_emis * panier_tout
            ca_commandes = commandes * panier_signe
            taux_ca = ca_commandes / ca_devise if ca_devise > 0 else 0
            
            data_list.append({
                "Année": y, "Mois": m, "Nb_Devis": devis_emis, "Taux_Succes_Vol": taux_vol,
                "Nb_Commandes": commandes, "Panier_Moyen_Tout": panier_tout,
                "Panier_Moyen_Signe": panier_signe, "CA_Devise": ca_devise,
                "CA_Commandes": ca_commandes, "Taux_Succes_CA": taux_ca
            })
    return pd.DataFrame(data_list)

df_perf = load_data()

# =====================================================================
# 4. STRUCTURE DE LA NAVIGATION / FILTRES (Vue Annuelle et Mensuelle)
# =====================================================================
st.title("📊 Tableau de bord commercial — LBFI")
st.markdown("## Performance Commerciale")

# Liste des années dynamiques basées sur vos données
liste_annees = sorted(list(df_perf["Année"].unique()), reverse=True)

# Onglets d'années calqués sur votre première capture d'écran
tabs_annees = st.tabs([f"Année {ans}" for ans in liste_annees])

for idx_tab, ans_selectionnee in enumerate(liste_annees):
    with tabs_annees[idx_tab]:
        
        # Filtre optionnel des mois pour basculer en vue mensuelle
        liste_mois = ["Janvier à Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                      "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        
        col_select_mois, _ = st.columns([3, 7])
        with col_select_mois:
            mois_selectionne = st.selectbox(
                "Période temporelle :", 
                liste_mois, 
                key=f"select_mois_{ans_selectionnee}"
            )
            
        st.markdown(f"#### 📌 Indicateurs Clés — {ans_selectionnee} ({mois_selectionne})")
        st.write("---")
        
        # --- FILTRAGE DYNAMIQUE DES DONNÉES (N, N-1, N+1) ---
        def filtrer_data(an, ms):
            df_sub = df_perf[df_perf["Année"] == an]
            if ms != "Janvier à Décembre":
                m_idx = liste_mois.index(ms)
                df_sub = df_sub[df_sub["Mois"] == m_idx]
            return df_sub

        df_courant = filtrer_data(ans_selectionnee, mois_selectionne)
        df_n_moins_1 = filtrer_data(ans_selectionnee - 1, mois_selectionne)
        df_n_plus_1 = filtrer_data(ans_selectionnee + 1, mois_selectionne)
        
        # --- AGREGATION DES COMPOSANTS (N) ---
        val_nb_devis = df_courant["Nb_Devis"].sum()
        val_nb_cmd = df_courant["Nb_Commandes"].sum()
        val_tx_vol = (val_nb_cmd / val_nb_devis * 100) if val_nb_devis > 0 else 0
        val_ca_devise = df_courant["CA_Devise"].sum()
        val_ca_cmd = df_courant["CA_Commandes"].sum()
        val_tx_ca = (val_ca_cmd / val_ca_devise * 100) if val_ca_devise > 0 else 0
        val_pm_tout = df_courant["Panier_Moyen_Tout"].mean() if not df_courant.empty else 0
        val_pm_signe = df_courant["Panier_Moyen_Signe"].mean() if not df_courant.empty else 0
        
        # --- AGREGATION DES COMPOSANTS (N-1) ---
        old_nb_devis = df_n_moins_1["Nb_Devis"].sum() if not df_n_moins_1.empty else 0
        old_nb_cmd = df_n_moins_1["Nb_Commandes"].sum() if not df_n_moins_1.empty else 0
        old_tx_vol = (old_nb_cmd / old_nb_devis * 100) if old_nb_devis > 0 else 0
        old_ca_devise = df_n_moins_1["CA_Devise"].sum() if not df_n_moins_1.empty else 0
        old_ca_cmd = df_n_moins_1["CA_Commandes"].sum() if not df_n_moins_1.empty else 0
        old_tx_ca = (old_ca_cmd / old_ca_devise * 100) if old_ca_devise > 0 else 0
        old_pm_tout = df_n_moins_1["Panier_Moyen_Tout"].mean() if not df_n_moins_1.empty else 0
        old_pm_signe = df_n_moins_1["Panier_Moyen_Signe"].mean() if not df_n_moins_1.empty else 0

        # --- AGREGATION DES COMPOSANTS (N+1) ---
        next_nb_devis = df_n_plus_1["Nb_Devis"].sum() if not df_n_plus_1.empty else 0
        next_nb_cmd = df_n_plus_1["Nb_Commandes"].sum() if not df_n_plus_1.empty else 0
        next_tx_vol = (next_nb_cmd / next_nb_devis * 100) if next_nb_devis > 0 else 0
        next_ca_devise = df_n_plus_1["CA_Devise"].sum() if not df_n_plus_1.empty else 0
        next_ca_cmd = df_n_plus_1["CA_Commandes"].sum() if not df_n_plus_1.empty else 0
        next_tx_ca = (next_ca_cmd / next_ca_devise * 100) if next_ca_devise > 0 else 0
        next_pm_tout = df_n_plus_1["Panier_Moyen_Tout"].mean() if not df_n_plus_1.empty else 0
        next_pm_signe = df_n_plus_1["Panier_Moyen_Signe"].mean() if not df_n_plus_1.empty else 0

        # --- CALCULS LOGIQUES DES DELTAS (TEXTES ET ETATS POSITIFS) ---
        diff_devis_n1 = val_nb_devis - old_nb_devis
        txt_devis_n1 = f"{'↗' if diff_devis_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_devis_n1:+} devis"
        diff_devis_n2 = val_nb_devis - next_nb_devis
        txt_devis_n2 = f"{'↗' if diff_devis_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_devis_n2:+} devis"

        diff_vol_n1 = val_tx_vol - old_tx_vol
        txt_vol_n1 = f"{'↗' if diff_vol_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_vol_n1:+.2f} pts"
        diff_vol_n2 = val_tx_vol - next_tx_vol
        txt_vol_n2 = f"{'↗' if diff_vol_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_vol_n2:+.2f} pts"

        diff_cmd_n1 = val_nb_cmd - old_nb_cmd
        txt_cmd_n1 = f"{'↗' if diff_cmd_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_cmd_n1:+} signés"
        diff_cmd_n2 = val_nb_cmd - next_nb_cmd
        txt_cmd_n2 = f"{'↗' if diff_cmd_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_cmd_n2:+} signés"

        diff_pmt_n1 = val_pm_tout - old_pm_tout
        txt_pmt_n1 = f"{'↗' if diff_pmt_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_pmt_n1:+.0f} €"
        diff_pmt_n2 = val_pm_tout - next_pm_tout
        txt_pmt_n2 = f"{'↗' if diff_pmt_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_pmt_n2:+.0f} €"

        diff_pms_n1 = val_pm_signe - old_pm_signe
        txt_pms_n1 = f"{'↗' if diff_pms_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_pms_n1:+.0f} €"
        diff_pms_n2 = val_pm_signe - next_pm_signe
        txt_pms_n2 = f"{'↗' if diff_pms_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_pms_n2:+.0f} €"

        diff_cadev_n1 = val_ca_devise - old_ca_devise
        txt_cadev_n1 = f"{'↗' if diff_cadev_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_cadev_n1:+} €"
        diff_cadev_n2 = val_ca_devise - next_ca_devise
        txt_cadev_n2 = f"{'↗' if diff_cadev_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_cadev_n2:+} €"

        diff_txca_n1 = val_tx_ca - old_tx_ca
        txt_txca_n1 = f"{'↗' if diff_txca_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_txca_n1:+.2f} pts"
        diff_txca_n2 = val_tx_ca - next_tx_ca
        txt_txca_n2 = f"{'↗' if diff_txca_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_txca_n2:+.2f} pts"

        diff_cacmd_n1 = val_ca_cmd - old_ca_cmd
        txt_cacmd_n1 = f"{'↗' if diff_cacmd_n1 >= 0 else '↘'} vs {ans_selectionnee-1} : {diff_cacmd_n1:+} €"
        diff_cacmd_n2 = val_ca_cmd - next_ca_cmd
        txt_cacmd_n2 = f"{'↗' if diff_cacmd_n2 >= 0 else '↘'} vs {ans_selectionnee+1} : {diff_cacmd_n2:+} €"

        # =====================================================================
        # 5. MISE EN FORME VISUELLE DE LA "FORMULE MAGIQUE"
        # =====================================================================
        
        # --- INDICATEUR ISOLÉ TOP : Commande moyenne (tous devis) ---
        col_top1, _ = st.columns([3, 7])
        with col_top1:
            render_kpi_card(
                title="Commande moyenne (tous devis)", 
                value=f"{val_pm_tout:,.0f} €".replace(",", " "), 
                delta_n_minus_1=txt_pmt_n1, 
                delta_n_plus_1=txt_pmt_n2, 
                is_positive_n1=(diff_pmt_n1 >= 0),
                icon="🛒"
            )
        
        st.write("") # Espace de respiration respiratoire

        # Définition précise des ratios horizontaux pour aligner les équations
        # [Bloc Métrique, Signe, Bloc Métrique, Signe, Bloc Métrique]
        grid_ratios = [3, 0.4, 3, 0.4, 3]

        # --- LIGNE ÉQUATION N°1 : LOGIQUE VOLUME ---
        # Nombre de devis émis X Taux de Succès (Volume) = Nombre de commandes
        row1_col1, row1_op1, row1_col2, row1_op2, row1_col3 = st.columns(grid_ratios)
        
        with row1_col1:
            render_kpi_card(
                title="Nombre de devis émis", 
                value=f"{val_nb_devis:,.0f}".replace(",", " "), 
                delta_n_minus_1=txt_devis_n1, 
                delta_n_plus_1=txt_devis_n2, 
                is_positive_n1=(diff_devis_n1 >= 0)
            )
        with row1_op1:
            render_operator("✕")
        with row1_col2:
            render_kpi_card(
                title="% Succès (Volume)", 
                value=f"{val_tx_vol:.2f} %".replace(".", ","), 
                delta_n_minus_1=txt_vol_n1, 
                delta_n_plus_1=txt_vol_n2, 
                is_positive_n1=(diff_vol_n1 >= 0)
            )
        with row1_op2:
            render_operator("＝")
        with row1_col3:
            render_kpi_card(
                title="Nombre de commandes", 
                value=f"{val_nb_cmd:,.0f}".replace(",", " "), 
                delta_n_minus_1=txt_cmd_n1, 
                delta_n_plus_1=txt_cmd_n2, 
                is_positive_n1=(diff_cmd_n1 >= 0)
            )

        # --- INTERCONNEXION DES DEUX LIGNES (LIAISON COMMANDE MOYENNE SIGNÉS) ---
        # On utilise la 5ème colonne pour placer la transition descendante directement sous le "Nombre de commandes"
        _, _, _, _, row_trans_col = st.columns(grid_ratios)
        
        with row_trans_col:
            # Sous-colonnes internes pour ajuster l'alignement des icônes de liaison et de la carte
            sub_arrow, sub_x, sub_card = st.columns([0.6, 0.6, 3.8])
            with sub_arrow:
                render_operator("⬇️", height="110px", font_size="2rem")
            with sub_x:
                render_operator("✕", height="110px", font_size="2rem")
            with sub_card:
                render_kpi_card(
                    title="Commande moyenne (signés)", 
                    value=f"{val_pm_signe:,.0f} €".replace(",", " "), 
                    delta_n_minus_1=txt_pms_n1, 
                    delta_n_plus_1=txt_pms_n2, 
                    is_positive_n1=(diff_pms_n1 >= 0),
                    icon="✅"
                )

        # --- LIGNE ÉQUATION N°2 : LOGIQUE VALEUR (€) ---
        # CA Devisé X Taux de Succès (€) = CA Commandes
        row2_col1, row2_op1, row2_col2, row2_op2, row2_col3 = st.columns(grid_ratios)
        
        with row2_col1:
            render_kpi_card(
                title=f"CA Devisé {ans_selectionnee}", 
                value=f"{val_ca_devise:,.0f} €".replace(",", " "), 
                delta_n_minus_1=txt_cadev_n1, 
                delta_n_plus_1=txt_cadev_n2, 
                is_positive_n1=(diff_cadev_n1 >= 0)
            )
        with row2_op1:
            render_operator("✕")
        with row2_col2:
            render_kpi_card(
                title="% Succès (€)", 
                value=f"{val_tx_ca:.2f} %".replace(".", ","), 
                delta_n_minus_1=txt_txca_n1, 
                delta_n_plus_1=txt_txca_n2, 
                is_positive_n1=(diff_txca_n1 >= 0)
            )
        with row2_op2:
            render_operator("＝")
        with row2_col3:
            render_kpi_card(
                title=f"CA Commandes {ans_selectionnee}", 
                value=f"{val_ca_cmd:,.0f} €".replace(",", " "), 
                delta_n_minus_1=txt_cacmd_n1, 
                delta_n_plus_1=txt_cacmd_n2, 
                is_positive_n1=(diff_cacmd_n1 >= 0)
            )
