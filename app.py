import streamlit as st
import ezdxf
import io

# --- 1. BIBLIOTHÈQUE ARCHITECTURALE ---
MATERIAUX = {
    "Béton armé": {"motif": "AR-CONC", "echelle": 0.5, "angle": 0, "couleur": 1, "motif_elev": "AR-CONC", "echelle_elev": 1.0, "angle_elev": 0},
    "Bloc béton (Parpaing)": {"motif": "AR-B816", "echelle": 0.5, "angle": 0, "couleur": 8, "motif_elev": "AR-B816", "echelle_elev": 1.0, "angle_elev": 0},
    "Brique creuse": {"motif": "ANSI32", "echelle": 1.0, "angle": 0, "couleur": 12, "motif_elev": "AR-BRSTD", "echelle_elev": 1.0, "angle_elev": 0},
    "Brique Monomur": {"motif": "ANSI32", "echelle": 2.0, "angle": 45, "couleur": 12, "motif_elev": "AR-BRSTD", "echelle_elev": 1.0, "angle_elev": 0},
    "Bois massif": {"motif": "ANSI31", "echelle": 1.5, "angle": 0, "couleur": 32, "motif_elev": "LINE", "echelle_elev": 2.0, "angle_elev": 90},
    "Métal (Acier/Alu)": {"motif": "ANSI31", "echelle": 0.5, "angle": 45, "couleur": 250, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Isolant rigide (PSE/PUR)": {"motif": "ANSI38", "echelle": 1.0, "angle": 0, "couleur": 3, "motif_elev": "ANSI38", "echelle_elev": 2.0, "angle_elev": 0},
    "Isolant souple (Laine minérale)": {"motif": "HONEY", "echelle": 2.0, "angle": 0, "couleur": 3, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Isolant naturel (Fibre bois)": {"motif": "FLEX", "echelle": 1.5, "angle": 0, "couleur": 50, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Enduit extérieur": {"motif": "AR-SAND", "echelle": 0.2, "angle": 0, "couleur": 40, "motif_elev": "AR-SAND", "echelle_elev": 0.5, "angle_elev": 0},
    "Bardage bois (Horizontal)": {"motif": "ANSI31", "echelle": 1.0, "angle": 0, "couleur": 34, "motif_elev": "LINE", "echelle_elev": 15.0, "angle_elev": 0},
    "Bardage bois (Vertical)": {"motif": "ANSI31", "echelle": 1.0, "angle": 0, "couleur": 34, "motif_elev": "LINE", "echelle_elev": 15.0, "angle_elev": 90},
    "Zinc (Joint debout)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 40.0, "angle_elev": 90},
    "Céramique / Terre cuite": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 14, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0}, # Pas de hachure, on dessinera le calepinage
    "Acier nervuré (Bac acier)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 20.0, "angle_elev": 90},
    "Panneau Fibre-ciment": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 250, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Plaque de plâtre (BA13/Fermacell)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 4, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Panneau OSB / Contreplaqué": {"motif": "ANSI31", "echelle": 0.5, "angle": 90, "couleur": 36, "motif_elev": "AR-SAND", "echelle_elev": 1.0, "angle_elev": 0},
    "Pare-pluie / Pare-vapeur": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 6, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Vide / Lame d'air": {"motif": None, "echelle": 1.0, "angle": 0, "couleur": 7, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0}
}

def dessiner_hachure(msp, points, layer, motif, echelle, angle):
    if motif is not None:
        try:
            hatch = msp.add_hatch(color=256, dxfattribs={'layer': layer})
            hatch.set_pattern_fill(motif, scale=echelle, angle=angle)
            hatch.paths.add_polyline_path(points, is_closed=True)
        except Exception:
            pass 

# --- 2. MOTEUR DE DESSIN DXF ---
def generer_dxf(couches, hauteur_mur):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    longueur_mur = 2400 # Allongé pour bien voir le calepinage
    
    # [Création des calques inchangée]
    for i, couche in enumerate(couches):
        mat_nom = couche['materiau']
        nom_calque = f"MUR_{i+1}_{mat_nom.upper().replace(' ', '_').replace('/', '_')}"
        doc.layers.add(name=nom_calque, color=MATERIAUX[mat_nom]['couleur'])
        doc.layers.add(name=f"{nom_calque}_HACH", color=MATERIAUX[mat_nom]['couleur'])
        if "materiau_remplissage" in couche:
            mat_r_nom = couche['materiau_remplissage']
            doc.layers.add(name=f"{nom_calque}_REMP", color=MATERIAUX[mat_r_nom]['couleur'])

    # --- VUE EN PLAN ---
    msp.add_text("VUE EN PLAN", dxfattribs={'height': 50}).set_placement((0, -150))
    y_plan = 0
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        if couche['type'] == "Continue" or couche.get('orientation') == "Horizontale":
            pts = [(0, y_plan), (longueur_mur, y_plan), (longueur_mur, y_plan + ep), (0, y_plan + ep)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            
        elif couche['type'] == "Ossature Métallique (Équerres)":
            # Dessin d'un profilé en T simplifié et de la lame d'air
            x_plan = 0
            while x_plan < longueur_mur:
                # Équerre + Profilé (Dessiné comme un "T" de 40mm de large)
                largeur_prof = 40
                ep_metal = 3
                # Barre perpendiculaire (l'équerre)
                pts_eq = [(x_plan + largeur_prof/2 - ep_metal/2, y_plan), 
                          (x_plan + largeur_prof/2 + ep_metal/2, y_plan), 
                          (x_plan + largeur_prof/2 + ep_metal/2, y_plan + ep), 
                          (x_plan + largeur_prof/2 - ep_metal/2, y_plan + ep)]
                # Barre parallèle (la face du profilé)
                pts_face = [(x_plan, y_plan + ep - ep_metal), 
                            (x_plan + largeur_prof, y_plan + ep - ep_metal), 
                            (x_plan + largeur_prof, y_plan + ep), 
                            (x_plan, y_plan + ep)]
                
                msp.add_lwpolyline(pts_eq, close=True, dxfattribs={'layer': nom_calque})
                msp.add_lwpolyline(pts_face, close=True, dxfattribs={'layer': nom_calque})
                
                x_plan += couche.get('entraxe', 600)

        elif couche['type'] == "Structure / Lattage" and couche['orientation'] == "Verticale":
            x_plan = 0
            while x_plan < longueur_mur:
                larg_m = couche.get('largeur_montant', 45)
                pts_m = [(x_plan, y_plan), (x_plan + larg_m, y_plan), (x_plan + larg_m, y_plan + ep), (x_plan, y_plan + ep)]
                msp.add_lwpolyline(pts_m, close=True, dxfattribs={'layer': nom_calque})
                x_plan += couche.get('entraxe', 600)
        y_plan += ep

    # --- VUE EN COUPE VERTICALE ---
    y_coupe_base = - (hauteur_mur + 1000)
    msp.add_text("VUE EN COUPE", dxfattribs={'height': 50}).set_placement((0, y_coupe_base - 150))
    x_coupe = 0
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        pts = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
        
        if couche['type'] in ["Continue", "Ossature Métallique (Équerres)"]:
            # L'équerre métallique vue de côté ressemble à une ligne continue traversant l'air
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
        x_coupe += ep

    # --- VUE EN ÉLÉVATION (AVEC CALEPINAGE) ---
    if len(couches) > 0:
        couche_ext = couches[-1]
        mat_ext = MATERIAUX[couche_ext['materiau']]
        x_elev = x_coupe + 1000 
        msp.add_text("VUE EN ELEVATION (Façade)", dxfattribs={'height': 50}).set_placement((x_elev, y_coupe_base - 150))
        pts_elev = [(x_elev, y_coupe_base), (x_elev + longueur_mur, y_coupe_base), (x_elev + longueur_mur, y_coupe_base + hauteur_mur), (x_elev, y_coupe_base + hauteur_mur)]
        
        doc.layers.add(name="VUE_ELEVATION", color=mat_ext['couleur'])
        msp.add_lwpolyline(pts_elev, close=True, dxfattribs={'layer': "VUE_ELEVATION"})
        
        # SI CALEPINAGE EST ACTIF
        if 'calepinage_l' in couche_ext and couche_ext['calepinage_l'] > 0:
            doc.layers.add(name="VUE_ELEVATION_JOINTS", color=252) # Couleur grise pour les joints
            
            # Lignes verticales du calepinage
            cal_x = x_elev
            while cal_x <= x_elev + longueur_mur:
                msp.add_line((cal_x, y_coupe_base), (cal_x, y_coupe_base + hauteur_mur), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                cal_x += couche_ext['calepinage_l']
                
            # Lignes horizontales du calepinage
            cal_y = y_coupe_base
            while cal_y <= y_coupe_base + hauteur_mur:
                msp.add_line((x_elev, cal_y), (x_elev + longueur_mur, cal_y), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                cal_y += couche_ext['calepinage_h']
        else:
            # Hachure classique si pas de calepinage
            dessiner_hachure(msp, pts_elev, "VUE_ELEVATION", mat_ext['motif_elev'], mat_ext['echelle_elev'], mat_ext['angle_elev'])

    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue()


# --- 3. INTERFACE UTILISATEUR & ALGORITHME INTELLIGENT ---
st.set_page_config(page_title="Configurateur BIM & CAO", layout="wide")
st.title("🏗️ Configurateur Global de Murs")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("1. Système Constructif")
    type_mur = st.radio("Principe d'isolation", ["ITI", "ITE"], horizontal=True)
    
    st.header("2. Structure Porteuse")
    mat_structure = st.selectbox("Matériau porteur", ["Béton armé", "Bloc béton (Parpaing)", "Brique creuse", "Brique Monomur", "Ossature Bois (MOB)"])
    ep_structure = st.number_input("Épaisseur porteur (mm)", value=200 if "Bois" not in mat_structure else 145, step=10)
    
    st.header("3. Isolation Principale")
    mat_isolant = st.selectbox("Matériau isolant", ["Isolant rigide (PSE/PUR)", "Isolant souple (Laine minérale)", "Isolant naturel (Fibre bois)"])
    ep_isolant = st.number_input("Épaisseur isolant (mm)", value=120, step=10)

    st.header("4. Finitions")
    c_int, c_ext = st.columns(2)
    with c_int:
        mat_par_int = st.selectbox("Parement intérieur", ["Plaque de plâtre (BA13/Fermacell)", "Panneau OSB / Contreplaqué"])
        ep_par_int = st.number_input("Épaisseur par. int. (mm)", value=13)
    with c_ext:
        mat_par_ext = st.selectbox("Façade extérieure", ["Enduit extérieur", "Bardage bois (Horizontal)", "Bardage bois (Vertical)", "Zinc (Joint debout)", "Céramique / Terre cuite", "Panneau Fibre-ciment", "Acier nervuré (Bac acier)"])
        ep_par_ext = st.number_input("Épaisseur façade (mm)", value=20)
        
        # Option de Calepinage conditionnelle
        calepinage_l, calepinage_h = 0, 0
        if mat_par_ext in ["Céramique / Terre cuite", "Panneau Fibre-ciment"]:
            st.markdown("📏 **Dimensions du calepinage**")
            sc1, sc2 = st.columns(2)
            calepinage_l = sc1.number_input("Largeur (mm)", value=600, step=50)
            calepinage_h = sc2.number_input("Hauteur (mm)", value=300, step=50)

with col2:
    st.header("Export & Bilan")
    hauteur_mur = st.number_input("Hauteur sous plafond (mm)", value=3000, step=100)
    
    if st.button("🔧 Générer le complexe mural", type="primary"):
        couches = []
        
        # INTÉRIEUR
        couches.append({"type": "Continue", "materiau": mat_par_int, "epaisseur": ep_par_int})
        if type_mur == "ITI" and mat_structure != "Ossature Bois (MOB)":
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Métal (Acier/Alu)", "materiau_remplissage": mat_isolant, "epaisseur": ep_isolant, "largeur_montant": 45, "entraxe": 600})
            
        # PORTEUR
        if mat_structure == "Ossature Bois (MOB)":
            couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": mat_isolant, "epaisseur": ep_structure, "largeur_montant": 45, "entraxe": 600})
            couches.append({"type": "Continue", "materiau": "Panneau OSB / Contreplaqué", "epaisseur": 12})
        else:
            couches.append({"type": "Continue", "materiau": mat_structure, "epaisseur": ep_structure})
            
        # ITE
        if type_mur == "ITE":
            couches.append({"type": "Continue", "materiau": mat_isolant, "epaisseur": ep_isolant})

        # --- INTELLIGENCE DE L'ACCROCHE DE FAÇADE ---
        ep_lame_air = 30 # standard DTU
        
        if mat_par_ext in ["Bardage bois (Horizontal)", "Bardage bois (Vertical)", "Acier nervuré (Bac acier)"]:
            couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
            # Lattage bois
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale" if "Horizontal" in mat_par_ext else "Horizontale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": ep_lame_air, "largeur_montant": 45, "entraxe": 400})
            
        elif mat_par_ext == "Zinc (Joint debout)":
            couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
            # Tasseaux de ventilation puis Voligeage continu (exigence zinc)
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": ep_lame_air, "largeur_montant": 45, "entraxe": 400})
            couches.append({"type": "Continue", "materiau": "Bois massif", "epaisseur": 18}) # La volige
            
        elif mat_par_ext in ["Céramique / Terre cuite", "Panneau Fibre-ciment"]:
            # L'ossature métallique !
            entraxe_metal = calepinage_l if calepinage_l > 0 else 600
            couches.append({"type": "Ossature Métallique (Équerres)", "materiau": "Métal (Acier/Alu)", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": ep_lame_air, "entraxe": entraxe_metal})

        # LA FINITION
        couche_finition = {"type": "Continue", "materiau": mat_par_ext, "epaisseur": ep_par_ext}
        if calepinage_l > 0:
            couche_finition['calepinage_l'] = calepinage_l
            couche_finition['calepinage_h'] = calepinage_h
        couches.append(couche_finition)
        
        st.session_state.couches_generees = couches
        st.success("Complexe assemblé avec succès !")

    # Bilan
    if 'couches_generees' in st.session_state:
        ep_totale = sum(c['epaisseur'] for c in st.session_state.couches_generees)
        st.info(f"Épaisseur totale réelle : **{ep_totale} mm**")
        dxf_data = generer_dxf(st.session_state.couches_generees, hauteur_mur)
        st.download_button(label="💾 Télécharger les Plans (.dxf)", data=dxf_data, file_name="mur_calepinage.dxf", mime="application/dxf", use_container_width=True)
