import streamlit as st
import ezdxf
import io

# --- 1. BIBLIOTHÈQUE ARCHITECTURALE DES MATÉRIAUX ---
# Chaque matériau a des propriétés pour la Coupe/Plan (motif, echelle, angle)
# et des propriétés pour l'Élévation de façade (motif_elev, echelle_elev, angle_elev)
MATERIAUX = {
    # STRUCTURE LOURDE / MAÇONNERIE
    "Béton armé": {"motif": "AR-CONC", "echelle": 0.5, "angle": 0, "couleur": 1, "motif_elev": "AR-CONC", "echelle_elev": 1.0, "angle_elev": 0},
    "Bloc béton (Parpaing)": {"motif": "AR-B816", "echelle": 0.5, "angle": 0, "couleur": 8, "motif_elev": "AR-B816", "echelle_elev": 1.0, "angle_elev": 0},
    "Brique creuse": {"motif": "ANSI32", "echelle": 1.0, "angle": 0, "couleur": 12, "motif_elev": "AR-BRSTD", "echelle_elev": 1.0, "angle_elev": 0},
    "Brique Monomur": {"motif": "ANSI32", "echelle": 2.0, "angle": 45, "couleur": 12, "motif_elev": "AR-BRSTD", "echelle_elev": 1.0, "angle_elev": 0},
    "Bois massif / Ossature": {"motif": "ANSI31", "echelle": 1.5, "angle": 0, "couleur": 32, "motif_elev": "LINE", "echelle_elev": 2.0, "angle_elev": 90},
    
    # ISOLANTS
    "Isolant rigide (PSE/XPS/PUR)": {"motif": "ANSI38", "echelle": 1.0, "angle": 0, "couleur": 3, "motif_elev": "ANSI38", "echelle_elev": 2.0, "angle_elev": 0},
    "Isolant souple (Laine minérale)": {"motif": "HONEY", "echelle": 2.0, "angle": 0, "couleur": 3, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Isolant naturel (Fibre bois/Ouate)": {"motif": "FLEX", "echelle": 1.5, "angle": 0, "couleur": 50, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    
    # REVÊTEMENTS EXTÉRIEURS (FAÇADES)
    "Enduit extérieur": {"motif": "AR-SAND", "echelle": 0.2, "angle": 0, "couleur": 40, "motif_elev": "AR-SAND", "echelle_elev": 0.5, "angle_elev": 0},
    "Bardage bois (Horizontal)": {"motif": "ANSI31", "echelle": 1.0, "angle": 0, "couleur": 34, "motif_elev": "LINE", "echelle_elev": 15.0, "angle_elev": 0},
    "Bardage bois (Vertical)": {"motif": "ANSI31", "echelle": 1.0, "angle": 0, "couleur": 34, "motif_elev": "LINE", "echelle_elev": 15.0, "angle_elev": 90},
    "Zinc (Joint debout)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 30.0, "angle_elev": 90},
    "Céramique / Terre cuite": {"motif": "AR-BRSTD", "echelle": 0.5, "angle": 0, "couleur": 14, "motif_elev": "NET", "echelle_elev": 15.0, "angle_elev": 0},
    "Acier nervuré (Bac acier)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 20.0, "angle_elev": 90},
    "Panneau Fibre-ciment": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 250, "motif_elev": "AR-SAND", "echelle_elev": 2.0, "angle_elev": 0},
    
    # REVÊTEMENTS INTÉRIEURS & PANNEAUX
    "Plaque de plâtre (BA13/Fermacell)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 4, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Panneau OSB / Contreplaqué": {"motif": "ANSI31", "echelle": 0.5, "angle": 90, "couleur": 36, "motif_elev": "AR-SAND", "echelle_elev": 1.0, "angle_elev": 0},
    "Carrelage": {"motif": "NET", "echelle": 1.0, "angle": 0, "couleur": 2, "motif_elev": "NET", "echelle_elev": 15.0, "angle_elev": 0},
    
    # MEMBRANES & VIDES
    "Pare-pluie / Pare-vapeur": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 6, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Vide / Lame d'air": {"motif": None, "echelle": 1.0, "angle": 0, "couleur": 7, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0}
}

# Fonction sécurisée pour ajouter des hachures sans planter si le motif est "Vide"
def dessiner_hachure(msp, points, layer, motif, echelle, angle):
    if motif is not None:
        try:
            hatch = msp.add_hatch(color=256, dxfattribs={'layer': layer})
            hatch.set_pattern_fill(motif, scale=echelle, angle=angle)
            hatch.paths.add_polyline_path(points, is_closed=True)
        except Exception:
            pass # Ignore les erreurs si un motif n'est pas supporté

# --- 2. MOTEUR DE GÉNÉRATION 3 VUES ---
def generer_dxf(couches, hauteur_mur=2800):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    longueur_mur = 1500 # Mur de 1.50m de long pour l'exemple
    
    # Création de tous les calques nécessaires
    for i, couche in enumerate(couches):
        mat_nom = couche['materiau']
        nom_calque = f"MUR_COUCHE_{i+1}_{mat_nom.upper().replace(' ', '_').replace('/', '_')}"
        if nom_calque not in doc.layers:
            doc.layers.add(name=nom_calque, color=MATERIAUX[mat_nom]['couleur'])
            doc.layers.add(name=f"{nom_calque}_HACH", color=MATERIAUX[mat_nom]['couleur'])
            
        if couche['type'] == "Ossature":
            mat_r_nom = couche['materiau_remplissage']
            nom_calque_r = f"MUR_COUCHE_{i+1}_REMP_{mat_r_nom.upper().replace(' ', '_').replace('/', '_')}"
            if nom_calque_r not in doc.layers:
                doc.layers.add(name=nom_calque_r, color=MATERIAUX[mat_r_nom]['couleur'])
                doc.layers.add(name=f"{nom_calque_r}_HACH", color=MATERIAUX[mat_r_nom]['couleur'])

    # --- VUE 1 : EN PLAN (Dessinée à Y=0) ---
    msp.add_text("VUE EN PLAN (Coupe Horizontale)", dxfattribs={'height': 50}).set_placement((0, -150))
    y_plan = 0
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_COUCHE_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        if couche['type'] == "Continue":
            pts = [(0, y_plan), (longueur_mur, y_plan), (longueur_mur, y_plan + ep), (0, y_plan + ep)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            
        elif couche['type'] == "Ossature":
            mat_r = MATERIAUX[couche['materiau_remplissage']]
            nom_calque_r = f"MUR_COUCHE_{i+1}_REMP_{couche['materiau_remplissage'].upper().replace(' ', '_').replace('/', '_')}"
            x_plan = 0
            while x_plan < longueur_mur:
                # Montant
                larg_m = min(couche['largeur_montant'], longueur_mur - x_plan)
                if larg_m > 0:
                    pts_m = [(x_plan, y_plan), (x_plan + larg_m, y_plan), (x_plan + larg_m, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts_m, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts_m, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                x_plan += larg_m
                
                # Isolant/Vide
                larg_v = min(couche['entraxe'] - couche['largeur_montant'], longueur_mur - x_plan)
                if larg_v > 0:
                    pts_r = [(x_plan, y_plan), (x_plan + larg_v, y_plan), (x_plan + larg_v, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts_r, close=True, dxfattribs={'layer': nom_calque_r})
                    dessiner_hachure(msp, pts_r, f"{nom_calque_r}_HACH", mat_r['motif'], mat_r['echelle'], mat_r['angle'])
                x_plan += larg_v
        y_plan += ep

    # --- VUE 2 : EN COUPE VERTICALE (Dessinée plus bas) ---
    y_coupe_base = - (hauteur_mur + 1000)
    msp.add_text("VUE EN COUPE (Verticale)", dxfattribs={'height': 50}).set_placement((0, y_coupe_base - 150))
    x_coupe = 0
    
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_COUCHE_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        if couche['type'] == "Continue":
            pts = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), 
                   (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            
        elif couche['type'] == "Ossature":
            mat_r = MATERIAUX[couche['materiau_remplissage']]
            nom_calque_r = f"MUR_COUCHE_{i+1}_REMP_{couche['materiau_remplissage'].upper().replace(' ', '_').replace('/', '_')}"
            
            # Dessin de l'isolant continu sur toute la hauteur
            pts = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), 
                   (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque_r})
            dessiner_hachure(msp, pts, f"{nom_calque_r}_HACH", mat_r['motif'], mat_r['echelle'], mat_r['angle'])
            
            # Lisses (haut et bas) pour l'ossature
            lisse_bas = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), 
                         (x_coupe + ep, y_coupe_base + couche['largeur_montant']), (x_coupe, y_coupe_base + couche['largeur_montant'])]
            lisse_haut = [(x_coupe, y_coupe_base + hauteur_mur - couche['largeur_montant']), (x_coupe + ep, y_coupe_base + hauteur_mur - couche['largeur_montant']), 
                          (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(lisse_bas, close=True, dxfattribs={'layer': nom_calque})
            msp.add_lwpolyline(lisse_haut, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, lisse_bas, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            dessiner_hachure(msp, lisse_haut, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
        x_coupe += ep

    # --- VUE 3 : ÉLÉVATION / FAÇADE (Dessinée à droite de la coupe) ---
    if len(couches) > 0:
        couche_ext = couches[-1] # La façade est la dernière couche
        mat_ext = MATERIAUX[couche_ext['materiau']]
        x_elev = x_coupe + 1000 # Décalage visuel d'1 mètre
        
        msp.add_text("VUE EN ELEVATION (Façade Extérieure)", dxfattribs={'height': 50}).set_placement((x_elev, y_coupe_base - 150))
        pts_elev = [(x_elev, y_coupe_base), (x_elev + longueur_mur, y_coupe_base), 
                    (x_elev + longueur_mur, y_coupe_base + hauteur_mur), (x_elev, y_coupe_base + hauteur_mur)]
        
        doc.layers.add(name="VUE_ELEVATION", color=mat_ext['couleur'])
        msp.add_lwpolyline(pts_elev, close=True, dxfattribs={'layer': "VUE_ELEVATION"})
        dessiner_hachure(msp, pts_elev, "VUE_ELEVATION", mat_ext['motif_elev'], mat_ext['echelle_elev'], mat_ext['angle_elev'])

    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue()


# --- 3. INTERFACE UTILISATEUR STREAMLIT ---
st.set_page_config(page_title="Configurateur BIM & CAO", layout="wide")
st.title("🏗️ Configurateur de Murs Paramétriques PRO")

if 'couches' not in st.session_state:
    st.session_state.couches = []

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. Composition (Intérieur ➡️ Extérieur)")
    
    c1, c2 = st.columns(2)
    if c1.button("➕ Ajouter Couche Continue"):
        st.session_state.couches.append({"type": "Continue", "epaisseur": 100, "materiau": "Béton armé"})
        st.rerun()
    if c2.button("➕ Ajouter Ossature (MOB/Cloison)"):
        st.session_state.couches.append({"type": "Ossature", "epaisseur": 145, "materiau": "Bois massif / Ossature", 
                                         "materiau_remplissage": "Isolant souple (Laine minérale)", "largeur_montant": 45, "entraxe": 600})
        st.rerun()

    for i, couche in enumerate(st.session_state.couches):
        with st.expander(f"Couche {i+1} : {couche['materiau']} ({couche['epaisseur']}mm)", expanded=True):
            cols = st.columns([3, 2, 1])
            
            couche['materiau'] = cols[0].selectbox("Matériau", list(MATERIAUX.keys()), index=list(MATERIAUX.keys()).index(couche['materiau']), key=f"mat_{i}")
            couche['epaisseur'] = cols[1].number_input("Épaisseur (mm)", min_value=1, value=couche['epaisseur'], key=f"ep_{i}")
            if cols[2].button("🗑️ Supprimer", key=f"del_{i}"):
                st.session_state.couches.pop(i)
                st.rerun()

            if couche['type'] == "Ossature":
                sc1, sc2, sc3 = st.columns(3)
                couche['materiau_remplissage'] = sc1.selectbox("Remplissage", list(MATERIAUX.keys()), index=list(MATERIAUX.keys()).index(couche['materiau_remplissage']), key=f"remp_{i}")
                couche['largeur_montant'] = sc2.number_input("Largeur montant (mm)", value=couche['largeur_montant'], key=f"larg_{i}")
                couche['entraxe'] = sc3.number_input("Entraxe (mm)", value=couche['entraxe'], key=f"ent_{i}")

with col2:
    st.subheader("2. Bilan & Export")
    hauteur_mur = st.number_input("Hauteur sous plafond (mm)", value=2800, step=100)
    
    if not st.session_state.couches:
        st.info("Ajoutez des couches pour commencer la conception.")
    else:
        epaisseur_totale = sum(c['epaisseur'] for c in st.session_state.couches)
        st.success(f"**Épaisseur du complexe : {epaisseur_totale} mm**")
        st.write(f"Nombre de couches : {len(st.session_state.couches)}")
        st.write("Le fichier généré inclura : \n - 📐 Vue en Plan \n - 📏 Vue en Coupe \n - 🏢 Vue en Élévation")
        
        dxf_data = generer_dxf(st.session_state.couches, hauteur_mur)
        st.download_button(
            label="💾 Télécharger les Plans (.dxf)",
            data=dxf_data,
            file_name="mur_complet_3vues.dxf",
            mime="application/dxf",
            use_container_width=True
        )
