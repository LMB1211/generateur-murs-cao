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
    "Céramique / Terre cuite": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 14, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Acier nervuré (Bac acier)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 20.0, "angle_elev": 90},
    "Panneau Fibre-ciment": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 250, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Plaque de plâtre (BA13/Fermacell)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 4, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Panneau OSB / Contreplaqué": {"motif": "ANSI31", "echelle": 0.5, "angle": 90, "couleur": 36, "motif_elev": "AR-SAND", "echelle_elev": 1.0, "angle_elev": 0},
    "Carrelage": {"motif": "NET", "echelle": 1.0, "angle": 0, "couleur": 2, "motif_elev": "NET", "echelle_elev": 15.0, "angle_elev": 0},
    "Pare-pluie / Pare-vapeur": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 6, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    "Vide / Lame d'air": {"motif": None, "echelle": 1.0, "angle": 0, "couleur": 7, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Colle / Mortier": {"motif": "AR-SAND", "echelle": 0.1, "angle": 0, "couleur": 252, "motif_elev": "AR-SAND", "echelle_elev": 1.0, "angle_elev": 0}
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
    longueur_mur = 2400 
    ep_joint = 8 
    
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
        
        if couche.get('calepinage_l', 0) > 0:
            cal_l = couche['calepinage_l']
            x_plan = 0
            while x_plan < longueur_mur:
                pan_l = min(cal_l - ep_joint, longueur_mur - x_plan)
                if pan_l > 0:
                    pts = [(x_plan, y_plan), (x_plan + pan_l, y_plan), (x_plan + pan_l, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                x_plan += cal_l
                
        elif couche['type'] == "Continue" or couche.get('orientation') == "Horizontale":
            pts = [(0, y_plan), (longueur_mur, y_plan), (longueur_mur, y_plan + ep), (0, y_plan + ep)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            
        elif couche['type'] == "Ossature Métallique (Équerres)":
            x_plan = 0
            while x_plan < longueur_mur:
                largeur_prof = 40
                ep_metal = 3
                pts_eq = [(x_plan + largeur_prof/2 - ep_metal/2, y_plan), (x_plan + largeur_prof/2 + ep_metal/2, y_plan), (x_plan + largeur_prof/2 + ep_metal/2, y_plan + ep), (x_plan + largeur_prof/2 - ep_metal/2, y_plan + ep)]
                pts_face = [(x_plan, y_plan + ep - ep_metal), (x_plan + largeur_prof, y_plan + ep - ep_metal), (x_plan + largeur_prof, y_plan + ep), (x_plan, y_plan + ep)]
                msp.add_lwpolyline(pts_eq, close=True, dxfattribs={'layer': nom_calque})
                msp.add_lwpolyline(pts_face, close=True, dxfattribs={'layer': nom_calque})
                x_plan += couche.get('entraxe', 600)

        elif couche['type'] == "Structure / Lattage" and couche['orientation'] == "Verticale":
            x_plan = 0
            while x_plan < longueur_mur:
                larg_m = couche.get('largeur_montant', 45)
                pts_m = [(x_plan, y_plan), (x_plan + larg_m, y_plan), (x_plan + larg_m, y_plan + ep), (x_plan, y_plan + ep)]
                msp.add_lwpolyline(pts_m, close=True, dxfattribs={'layer': nom_calque})
                dessiner_hachure(msp, pts_m, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
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
        
        if couche.get('calepinage_h', 0) > 0:
            cal_h = couche['calepinage_h']
            y_c = y_coupe_base
            while y_c < y_coupe_base + hauteur_mur:
                pan_h = min(cal_h - ep_joint, (y_coupe_base + hauteur_mur) - y_c)
                if pan_h > 0:
                    pts = [(x_coupe, y_c), (x_coupe + ep, y_c), (x_coupe + ep, y_c + pan_h), (x_coupe, y_c + pan_h)]
                    msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                y_c += cal_h

        elif couche['type'] in ["Continue", "Ossature Métallique (Équerres)"] or (couche['type'] == "Structure / Lattage" and couche['orientation'] == "Verticale"):
            pts = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            if couche['type'] != "Ossature Métallique (Équerres)":
                 dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
        
        elif couche['type'] == "Structure / Lattage" and couche['orientation'] == "Horizontale":
            y_tass = y_coupe_base
            while y_tass < (y_coupe_base + hauteur_mur):
                h_tass = min(couche.get('largeur_montant', 45), (y_coupe_base + hauteur_mur) - y_tass)
                pts_tass = [(x_coupe, y_tass), (x_coupe + ep, y_tass), (x_coupe + ep, y_tass + h_tass), (x_coupe, y_tass + h_tass)]
                msp.add_lwpolyline(pts_tass, close=True, dxfattribs={'layer': nom_calque})
                dessiner_hachure(msp, pts_tass, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                y_tass += couche.get('entraxe', 400)
        x_coupe += ep

    # --- VUE EN ÉLÉVATION (DE FACE) ---
    if len(couches) > 0:
        couche_ext = couches[-1]
        mat_ext = MATERIAUX[couche_ext['materiau']]
        x_elev = x_coupe + 1000 
        msp.add_text("VUE EN ELEVATION (Façade)", dxfattribs={'height': 50}).set_placement((x_elev, y_coupe_base - 150))
        doc.layers.add(name="VUE_ELEVATION", color=mat_ext['couleur'])
        
        if 'calepinage_l' in couche_ext and couche_ext['calepinage_l'] > 0:
            cal_l = couche_ext['calepinage_l']
            cal_h = couche_ext['calepinage_h']
            
            cal_x = x_elev
            while cal_x < x_elev + longueur_mur:
                pan_l = min(cal_l - ep_joint, (x_elev + longueur_mur) - cal_x)
                cal_y = y_coupe_base
                while cal_y < y_coupe_base + hauteur_mur:
                    pan_h = min(cal_h - ep_joint, (y_coupe_base + hauteur_mur) - cal_y)
                    if pan_l > 0 and pan_h > 0:
                        pts_pan = [(cal_x, cal_y), (cal_x + pan_l, cal_y), (cal_x + pan_l, cal_y + pan_h), (cal_x, cal_y + pan_h)]
                        msp.add_lwpolyline(pts_pan, close=True, dxfattribs={'layer': "VUE_ELEVATION"})
                        dessiner_hachure(msp, pts_pan, "VUE_ELEVATION", mat_ext['motif_elev'], mat_ext['echelle_elev'], mat_ext['angle_elev'])
                    cal_y += cal_h
                cal_x += cal_l
                
        else:
            pts_elev = [(x_elev, y_coupe_base), (x_elev + longueur_mur, y_coupe_base), (x_elev + longueur_mur, y_coupe_base + hauteur_mur), (x_elev, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts_elev, close=True, dxfattribs={'layer': "VUE_ELEVATION"})
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
        st.subheader("Intérieur")
        mat_par_int = st.selectbox("Parement", ["Plaque de plâtre (BA13/Fermacell)", "Panneau OSB / Contreplaqué", "Bois massif", "Carrelage"])
        ep_par_int = st.number_input("Épaisseur (mm)", value=13, key="ep_int")
        
    with c_ext:
        st.subheader("Extérieur")
        mat_par_ext = st.selectbox("Façade", ["Enduit extérieur", "Bardage bois (Horizontal)", "Bardage bois (Vertical)", "Zinc (Joint debout)", "Céramique / Terre cuite", "Panneau Fibre-ciment", "Acier nervuré (Bac acier)"])
        ep_par_ext = st.number_input("Épaisseur (mm)", value=20, key="ep_ext")
        type_pose = st.radio("Type de pose", ["Ventilée (avec lame d'air)", "Non ventilée (Directe / collée)"])
        
        calepinage_l, calepinage_h = 0, 0
        if mat_par_ext in ["Céramique / Terre cuite", "Panneau Fibre-ciment"]:
            st.markdown("📏 **Calepinage**")
            sc1, sc2 = st.columns(2)
            calepinage_l = sc1.number_input("Largeur (mm)", value=600, step=50)
            calepinage_h = sc2.number_input("Hauteur (mm)", value=300, step=50)

with col2:
    st.header("Export & Bilan")
    hauteur_mur = st.number_input("Hauteur sous plafond (mm)", value=3000, step=100)
    
    if st.button("🔧 Générer le complexe mural", type="primary"):
        couches = []
        
        # INTÉRIEUR (Désormais dynamique !)
        couches.append({"type": "Continue", "materiau": mat_par_int, "epaisseur": ep_par_int})
        
        # PORTEUR & ISOLATION
        if type_mur == "ITI" and mat_structure != "Ossature Bois (MOB)":
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Métal (Acier/Alu)", "materiau_remplissage": mat_isolant, "epaisseur": ep_isolant, "largeur_montant": 45, "entraxe": 600})
            
        if mat_structure == "Ossature Bois (MOB)":
            couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": mat_isolant, "epaisseur": ep_structure, "largeur_montant": 45, "entraxe": 600})
            couches.append({"type": "Continue", "materiau": "Panneau OSB / Contreplaqué", "epaisseur": 12})
        else:
            couches.append({"type": "Continue", "materiau": mat_structure, "epaisseur": ep_structure})
            
        if type_mur == "ITE":
            couches.append({"type": "Continue", "materiau": mat_isolant, "epaisseur": ep_isolant})

        # --- INTELLIGENCE DE L'ACCROCHE ---
        if "Ventilée" in type_pose:
            ep_lame_air = 30
            if mat_par_ext in ["Bardage bois (Horizontal)", "Bardage bois (Vertical)", "Acier nervuré (Bac acier)"]:
                couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
                if "Vertical" in mat_par_ext:
                    couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": 27, "largeur_montant": 45, "entraxe": 600})
                    couches.append({"type": "Structure / Lattage", "orientation": "Horizontale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": 27, "largeur_montant": 45, "entraxe": 400})
                else:
                    couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": ep_lame_air, "largeur_montant": 45, "entraxe": 600})
            elif mat_par_ext == "Zinc (Joint debout)":
                couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
                couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": ep_lame_air, "largeur_montant": 45, "entraxe": 600})
                couches.append({"type": "Continue", "materiau": "Bois massif", "epaisseur": 18}) 
            elif mat_par_ext in ["Céramique / Terre cuite", "Panneau Fibre-ciment"]:
                entraxe_v = calepinage_l if calepinage_l > 0 else 600
                entraxe_h = calepinage_h if calepinage_h > 0 else 300
                couches.append({"type": "Ossature Métallique (Équerres)", "materiau": "Métal (Acier/Alu)", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": ep_lame_air, "entraxe": entraxe_v})
                couches.append({"type": "Structure / Lattage", "orientation": "Horizontale", "materiau": "Métal (Acier/Alu)", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": 15, "largeur_montant": 30, "entraxe": entraxe_h})
        else:
            if mat_par_ext in ["Céramique / Terre cuite", "Enduit extérieur", "Carrelage"]:
                couches.append({"type": "Continue", "materiau": "Colle / Mortier", "epaisseur": 5})

        # LA FINITION EXTÉRIEURE
        couche_finition = {"type": "Continue", "materiau": mat_par_ext, "epaisseur": ep_par_ext}
        if calepinage_l > 0:
            couche_finition['calepinage_l'] = calepinage_l
            couche_finition['calepinage_h'] = calepinage_h
        couches.append(couche_finition)
        
        st.session_state.couches_generees = couches
        st.success("Complexe assemblé avec succès !")

    if 'couches_generees' in st.session_state:
        ep_totale = sum(c['epaisseur'] for c in st.session_state.couches_generees)
        st.info(f"Épaisseur totale réelle : **{ep_totale} mm**")
        dxf_data = generer_dxf(st.session_state.couches_generees, hauteur_mur)
        st.download_button(label="💾 Télécharger les Plans (.dxf)", data=dxf_data, file_name="mur_complet.dxf", mime="application/dxf", use_container_width=True)
