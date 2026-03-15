import streamlit as st
import ezdxf
import io

# --- BIBLIOTHÈQUE DES MATÉRIAUX ---
# Associe un nom à un motif AutoCAD, une échelle, et une couleur (Index ACI)
MATERIAUX = {
    "Béton": {"motif": "AR-CONC", "echelle": 0.5, "couleur": 1}, # Rouge
    "Isolant rigide (PSE)": {"motif": "ANSI38", "echelle": 1.0, "couleur": 3}, # Vert
    "Isolant souple (Laine)": {"motif": "HONEY", "echelle": 2.0, "couleur": 3},
    "Bois massif": {"motif": "ANSI31", "echelle": 1.5, "couleur": 32}, # Marron
    "Plaque de plâtre (BA13)": {"motif": "SOLID", "echelle": 1.0, "couleur": 4}, # Cyan
    "Vide / Air": {"motif": None, "echelle": 1, "couleur": 7} # Blanc/Noir
}

# --- MOTEUR DE GÉNÉRATION DXF ---
def generer_dxf(couches):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    longueur_mur = 1200 # Segment de 1,20m de long pour bien voir l'ossature
    y_courant = 0 # On empile les épaisseurs sur l'axe Y (Vue en plan)
    
    for i, couche in enumerate(couches):
        epaisseur = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        
        # Nom du calque généré automatiquement
        nom_calque = f"MUR_COUCHE_{i+1}_{couche['materiau'].upper().replace(' ', '_')}"
        doc.layers.add(name=nom_calque, color=mat['couleur'])
        doc.layers.add(name=f"{nom_calque}_HACH", color=mat['couleur'])
        
        if couche['type'] == "Continue":
            # Dessiner un grand rectangle plein
            points = [(0, y_courant), (longueur_mur, y_courant), (longueur_mur, y_courant + epaisseur), (0, y_courant + epaisseur)]
            msp.add_lwpolyline(points, close=True, dxfattribs={'layer': nom_calque})
            
            # Ajouter la hachure si ce n'est pas de l'air
            if mat['motif'] is not None:
                hatch = msp.add_hatch(color=256, dxfattribs={'layer': f"{nom_calque}_HACH"})
                hatch.set_pattern_fill(mat['motif'], scale=mat['echelle'])
                hatch.paths.add_polyline_path(points, is_closed=True)
                
        elif couche['type'] == "Ossature":
            entraxe = couche['entraxe']
            largeur_montant = couche['largeur_montant']
            mat_remplissage = MATERIAUX[couche['materiau_remplissage']]
            
            # Dessiner les montants et le remplissage
            x_courant = 0
            while x_courant < longueur_mur:
                # 1. Le montant en bois/métal
                pts_montant = [(x_courant, y_courant), (x_courant + largeur_montant, y_courant), 
                               (x_courant + largeur_montant, y_courant + epaisseur), (x_courant, y_courant + epaisseur)]
                msp.add_lwpolyline(pts_montant, close=True, dxfattribs={'layer': nom_calque})
                if mat['motif'] is not None:
                    hatch = msp.add_hatch(color=256, dxfattribs={'layer': f"{nom_calque}_HACH"})
                    hatch.set_pattern_fill(mat['motif'], scale=mat['echelle'])
                    hatch.paths.add_polyline_path(pts_montant, is_closed=True)
                
                x_courant += largeur_montant
                
                # 2. L'isolant entre les montants
                largeur_vide = entraxe - largeur_montant
                if x_courant + largeur_vide > longueur_mur:
                    largeur_vide = longueur_mur - x_courant # Couper à la fin du mur
                
                if largeur_vide > 0:
                    pts_isolant = [(x_courant, y_courant), (x_courant + largeur_vide, y_courant), 
                                   (x_courant + largeur_vide, y_courant + epaisseur), (x_courant, y_courant + epaisseur)]
                    msp.add_lwpolyline(pts_isolant, close=True, dxfattribs={'layer': nom_calque})
                    if mat_remplissage['motif'] is not None:
                        hatch2 = msp.add_hatch(color=256, dxfattribs={'layer': f"{nom_calque}_HACH"})
                        hatch2.set_pattern_fill(mat_remplissage['motif'], scale=mat_remplissage['echelle'])
                        hatch2.paths.add_polyline_path(pts_isolant, is_closed=True)
                
                x_courant += largeur_vide

        y_courant += epaisseur # Avancer pour la prochaine couche

    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue()

# --- INTERFACE UTILISATEUR STREAMLIT ---
st.set_page_config(page_title="Configurateur de Murs CAO", layout="wide")
st.title("🧱 Configurateur de Murs Paramétriques")

# Initialisation de la mémoire (Session State)
if 'couches' not in st.session_state:
    st.session_state.couches = []

# --- COLONNE GAUCHE : LE CONSTRUCTEUR ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. Assemblez vos couches (Intérieur ➡️ Extérieur)")
    
    # Boutons d'ajout
    c1, c2 = st.columns(2)
    if c1.button("➕ Ajouter Couche Continue"):
        st.session_state.couches.append({"type": "Continue", "epaisseur": 100, "materiau": "Béton"})
        st.rerun()
    if c2.button("➕ Ajouter Ossature (MOB/Cloison)"):
        st.session_state.couches.append({"type": "Ossature", "epaisseur": 145, "materiau": "Bois massif", 
                                         "materiau_remplissage": "Isolant souple (Laine)", "largeur_montant": 45, "entraxe": 600})
        st.rerun()

    # Affichage dynamique des couches
    for i, couche in enumerate(st.session_state.couches):
        with st.expander(f"Couche {i+1} : {couche['type']} - {couche['epaisseur']}mm", expanded=True):
            cols = st.columns([3, 2, 1])
            
            couche['materiau'] = cols[0].selectbox("Matériau principal", list(MATERIAUX.keys()), index=list(MATERIAUX.keys()).index(couche['materiau']), key=f"mat_{i}")
            couche['epaisseur'] = cols[1].number_input("Épaisseur (mm)", min_value=1, value=couche['epaisseur'], key=f"ep_{i}")
            
            if cols[2].button("🗑️ Supprimer", key=f"del_{i}"):
                st.session_state.couches.pop(i)
                st.rerun()

            if couche['type'] == "Ossature":
                sc1, sc2, sc3 = st.columns(3)
                couche['materiau_remplissage'] = sc1.selectbox("Remplissage", list(MATERIAUX.keys()), index=list(MATERIAUX.keys()).index(couche['materiau_remplissage']), key=f"remp_{i}")
                couche['largeur_montant'] = sc2.number_input("Largeur montant (mm)", value=couche['largeur_montant'], key=f"larg_{i}")
                couche['entraxe'] = sc3.number_input("Entraxe (mm)", value=couche['entraxe'], key=f"ent_{i}")

# --- COLONNE DROITE : EXPORT ---
with col2:
    st.subheader("2. Bilan & Export")
    if not st.session_state.couches:
        st.info("Ajoutez des couches pour commencer.")
    else:
        epaisseur_totale = sum(c['epaisseur'] for c in st.session_state.couches)
        st.success(f"**Épaisseur totale : {epaisseur_totale} mm**")
        st.write(f"Nombre de couches : {len(st.session_state.couches)}")
        
        dxf_data = generer_dxf(st.session_state.couches)
        st.download_button(
            label="💾 Télécharger le fichier .dxf",
            data=dxf_data,
            file_name="mur_sur_mesure.dxf",
            mime="application/dxf",
            use_container_width=True
        )
