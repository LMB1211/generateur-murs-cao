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
    "Zinc (Joint debout)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 30.0, "angle_elev": 90},
    "Céramique / Terre cuite": {"motif": "AR-BRSTD", "echelle": 0.5, "angle": 0, "couleur": 14, "motif_elev": "NET", "echelle_elev": 15.0, "angle_elev": 0},
    "Acier nervuré (Bac acier)": {"motif": "SOLID", "echelle": 1.0, "angle": 0, "couleur": 5, "motif_elev": "LINE", "echelle_elev": 20.0, "angle_elev": 90},
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

# --- 2. MOTEUR DE DESSIN DXF (Inchangé) ---
def generer_dxf(couches, hauteur_mur):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    longueur_mur = 1500 
    
    for i, couche in enumerate(couches):
        mat_nom = couche['materiau']
        nom_calque = f"MUR_{i+1}_{mat_nom.upper().replace(' ', '_').replace('/', '_')}"
        if nom_calque not in doc.layers:
            doc.layers.add(name=nom_calque, color=MATERIAUX[mat_nom]['couleur'])
            doc.layers.add(name=f"{nom_calque}_HACH", color=MATERIAUX[mat_nom]['couleur'])
            
        if couche['type'] == "Structure / Lattage":
            mat_r_nom = couche['materiau_remplissage']
            nom_calque_r = f"MUR_{i+1}_REMP_{mat_r_nom.upper().replace(' ', '_').replace('/', '_')}"
            if nom_calque_r not in doc.layers:
                doc.layers.add(name=nom_calque_r, color=MATERIAUX[mat_r_nom]['couleur'])
                doc.layers.add(name=f"{nom_calque_r}_HACH", color=MATERIAUX[mat_r_nom]['couleur'])

    msp.add_text("VUE EN PLAN (Coupe Horizontale)", dxfattribs={'height': 50}).set_placement((0, -150))
    y_plan = 0
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        if couche['type'] == "Continue" or (couche['type'] == "Structure / Lattage" and couche['orientation'] == "Horizontale"):
            pts = [(0, y_plan), (longueur_mur, y_plan), (longueur_mur, y_plan + ep), (0, y_plan + ep)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
        elif couche['type'] == "Structure / Lattage" and couche['orientation'] == "Verticale":
            mat_r = MATERIAUX[couche['materiau_remplissage']]
            nom_calque_r = f"MUR_{i+1}_REMP_{couche['materiau_remplissage'].upper().replace(' ', '_').replace('/', '_')}"
            x_plan = 0
            while x_plan < longueur_mur:
                larg_m = min(couche.get('largeur_montant', 45), longueur_mur - x_plan)
                if larg_m > 0:
                    pts_m = [(x_plan, y_plan), (x_plan + larg_m, y_plan), (x_plan + larg_m, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts_m, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts_m, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                x_plan += larg_m
                
                larg_v = min(couche.get('entraxe', 600) - couche.get('largeur_montant', 45), longueur_mur - x_plan)
                if larg_v > 0:
                    pts_r = [(x_plan, y_plan), (x_plan + larg_v, y_plan), (x_plan + larg_v, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts_r, close=True, dxfattribs={'layer': nom_calque_r})
                    dessiner_hachure(msp, pts_r, f"{nom_calque_r}_HACH", mat_r['motif'], mat_r['echelle'], mat_r['angle'])
                x_plan += larg_v
        y_plan += ep

    y_coupe_base = - (hauteur_mur + 1000)
    msp.add_text("VUE EN COUPE (Verticale)", dxfattribs={'height': 50}).set_placement((0, y_coupe_base - 150))
    x_coupe = 0
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        if couche['type'] == "Continue":
            pts = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
        elif couche['type'] == "Structure / Lattage":
            mat_r = MATERIAUX[couche['materiau_remplissage']]
            nom_calque_r = f"MUR_{i+1}_REMP_{couche['materiau_remplissage'].upper().replace(' ', '_').replace('/', '_')}"
            
            pts_fond = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts_fond, close=True, dxfattribs={'layer': nom_calque_r})
            dessiner_hachure(msp, pts_fond, f"{nom_calque_r}_HACH", mat_r['motif'], mat_r['echelle'], mat_r['angle'])
            
            if couche['orientation'] == "Verticale":
                lisse_bas = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), (x_coupe + ep, y_coupe_base + couche.get('largeur_montant', 45)), (x_coupe, y_coupe_base + couche.get('largeur_montant', 45))]
                lisse_haut = [(x_coupe, y_coupe_base + hauteur_mur - couche.get('largeur_montant', 45)), (x_coupe + ep, y_coupe_base + hauteur_mur - couche.get('largeur_montant', 45)), (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
                msp.add_lwpolyline(lisse_bas, close=True, dxfattribs={'layer': nom_calque})
                msp.add_lwpolyline(lisse_haut, close=True, dxfattribs={'layer': nom_calque})
                dessiner_hachure(msp, lisse_bas, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                dessiner_hachure(msp, lisse_haut, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                
                esp_ent = couche.get('entraxe_secondaire', 1250)
                if esp_ent > 0:
                    y_ent = y_coupe_base + esp_ent
                    while y_ent < (y_coupe_base + hauteur_mur - couche.get('largeur_montant', 45)):
                        pts_ent = [(x_coupe, y_ent), (x_coupe + ep, y_ent), (x_coupe + ep, y_ent + couche.get('largeur_montant', 45)), (x_coupe, y_ent + couche.get('largeur_montant', 45))]
                        msp.add_lwpolyline(pts_ent, close=True, dxfattribs={'layer': nom_calque})
                        dessiner_hachure(msp, pts_ent, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                        y_ent += esp_ent
            elif couche['orientation'] == "Horizontale":
                esp_tass = couche.get('entraxe', 400)
                y_tass = y_coupe_base
                while y_tass < (y_coupe_base + hauteur_mur):
                    h_tass = min(couche.get('largeur_montant', 27), (y_coupe_base + hauteur_mur) - y_tass)
                    pts_tass = [(x_coupe, y_tass), (x_coupe + ep, y_tass), (x_coupe + ep, y_tass + h_tass), (x_coupe, y_tass + h_tass)]
                    msp.add_lwpolyline(pts_tass, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts_tass, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                    y_tass += esp_tass
        x_coupe += ep

    if len(couches) > 0:
        couche_ext = couches[-1]
        mat_ext = MATERIAUX[couche_ext['materiau']]
        x_elev = x_coupe + 1000 
        msp.add_text("VUE EN ELEVATION (Façade Extérieure)", dxfattribs={'height': 50}).set_placement((x_elev, y_coupe_base - 150))
        pts_elev = [(x_elev, y_coupe_base), (x_elev + longueur_mur, y_coupe_base), (x_elev + longueur_mur, y_coupe_base + hauteur_mur), (x_elev, y_coupe_base + hauteur_mur)]
        doc.layers.add(name="VUE_ELEVATION", color=mat_ext['couleur'])
        msp.add_lwpolyline(pts_elev, close=True, dxfattribs={'layer': "VUE_ELEVATION"})
        dessiner_hachure(msp, pts_elev, "VUE_ELEVATION", mat_ext['motif_elev'], mat_ext['echelle_elev'], mat_ext['angle_elev'])

    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue()


# --- 3. INTERFACE UTILISATEUR & ALGORITHME D'ASSEMBLAGE ---
st.set_page_config(page_title="Configurateur BIM & CAO", layout="wide")
st.title("🏗️ Configurateur Global de Murs")
st.write("Définissez les paramètres de votre mur. L'algorithme se charge d'assembler les couches dans le bon ordre technique.")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("1. Système Constructif")
    type_mur = st.radio("Principe d'isolation", ["ITI (Isolation par l'Intérieur)", "ITE (Isolation par l'Extérieur)"], horizontal=True)
    
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
        mat_par_ext = st.selectbox("Façade extérieure", ["Enduit extérieur", "Bardage bois (Horizontal)", "Bardage bois (Vertical)", "Zinc (Joint debout)", "Céramique / Terre cuite", "Acier nervuré (Bac acier)"])
        ep_par_ext = st.number_input("Épaisseur façade (mm)", value=20)

with col2:
    st.header("Export & Bilan")
    hauteur_mur = st.number_input("Hauteur sous plafond (mm)", value=3000, step=100)
    
    if st.button("🔧 Générer le complexe mural", type="primary"):
        couches = []
        
        # A. PAREMENT INTÉRIEUR
        couches.append({"type": "Continue", "materiau": mat_par_int, "epaisseur": ep_par_int})
        
        # B. ISOLATION ITI (si applicable et non MOB)
        if type_mur == "ITI (Isolation par l'Intérieur)" and mat_structure != "Ossature Bois (MOB)":
            # On simule l'isolant entre des rails placo classiques
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Métal (Acier/Alu)", "materiau_remplissage": mat_isolant, "epaisseur": ep_isolant, "largeur_montant": 45, "entraxe": 600, "entraxe_secondaire": 0})
            
        # C. STRUCTURE PORTEUSE
        if mat_structure == "Ossature Bois (MOB)":
            # Pour un MOB, l'isolant principal est DANS l'ossature
            couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2}) # Frein vapeur int.
            couches.append({"type": "Structure / Lattage", "orientation": "Verticale", "materiau": "Bois massif", "materiau_remplissage": mat_isolant, "epaisseur": ep_structure, "largeur_montant": 45, "entraxe": 600, "entraxe_secondaire": 1250})
            couches.append({"type": "Continue", "materiau": "Panneau OSB / Contreplaqué", "epaisseur": 12}) # Contreventement
        else:
            couches.append({"type": "Continue", "materiau": mat_structure, "epaisseur": ep_structure})
            
        # D. ISOLATION ITE
        if type_mur == "ITE (Isolation par l'Extérieur)":
            # Si c'est un MOB, c'est une ITE supplémentaire (fibre de bois par ex)
            couches.append({"type": "Continue", "materiau": mat_isolant, "epaisseur": ep_isolant})

        # E. SYSTÈME DE FAÇADE (PAREMENT EXT)
        # Si la façade nécessite une accroche ventilée (Bardage, Zinc, Céramique...)
        if mat_par_ext != "Enduit extérieur":
            couches.append({"type": "Continue", "materiau": "Pare-pluie / Pare-vapeur", "epaisseur": 2})
            # Lattage bois horizontal pour créer la lame d'air
            couches.append({"type": "Structure / Lattage", "orientation": "Horizontale", "materiau": "Bois massif", "materiau_remplissage": "Vide / Lame d'air", "epaisseur": 27, "largeur_montant": 45, "entraxe": 400})
            
        couches.append({"type": "Continue", "materiau": mat_par_ext, "epaisseur": ep_par_ext})
        
        # Enregistrement dans la mémoire
        st.session_state.couches_generees = couches
        st.success("Complexe assemblé avec succès !")

    # Affichage du Bilan si généré
    if 'couches_generees' in st.session_state:
        st.write("---")
        st.write("**Empilement calculé (Int. vers Ext.) :**")
        ep_totale = 0
        for i, c in enumerate(st.session_state.couches_generees):
            st.write(f"{i+1}. {c['materiau']} ({c['epaisseur']} mm)")
            ep_totale += c['epaisseur']
            
        st.info(f"Épaisseur totale réelle : **{ep_totale} mm**")
        
        dxf_data = generer_dxf(st.session_state.couches_generees, hauteur_mur)
        st.download_button(
            label="💾 Télécharger les Plans (.dxf)",
            data=dxf_data,
            file_name=f"mur_{'ITI' if 'ITI' in type_mur else 'ITE'}_{mat_structure.split()[0]}.dxf",
            mime="application/dxf",
            use_container_width=True
        )
