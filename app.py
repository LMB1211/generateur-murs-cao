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

COULEURS_MENUISERIE = {"Bois": 34, "Aluminium": 250, "PVC": 7, "Mixte Bois/Alu": 32}

def dessiner_hachure(msp, polyline, points, layer, motif, echelle, angle, hole_pts=None):
    if motif is not None:
        try:
            hatch = msp.add_hatch(color=256, dxfattribs={'layer': layer})
            hatch.dxf.hatch_style = 0 
            hatch.set_pattern_fill(motif, scale=echelle, angle=angle)
            path = hatch.paths.add_polyline_path(points, is_closed=True)
            if hole_pts:
                hatch.paths.add_polyline_path(hole_pts, is_closed=True)
            hatch.dxf.associative = 1
            path.source_boundary_objects = [polyline.dxf.handle]
            polyline.append_reactor_handle(hatch.dxf.handle)
            cx = sum(p[0] for p in points) / len(points)
            cy = sum(p[1] for p in points) / len(points)
            hatch.set_seed_points([(cx, cy)])
        except Exception:
            pass 

# --- 2. MOTEUR DE DESSIN DXF ---
def generer_dxf(couches, hauteur_mur, men_config):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    longueur_mur = 3000 
    
    a_menuiserie = men_config['active']
    w_fen = men_config['largeur']
    h_fen = men_config['hauteur']
    allege = men_config['allege']
    mat_fen = men_config['materiau']
    type_fen = men_config['type_ouverture']
    couleur_fen = COULEURS_MENUISERIE.get(mat_fen, 7)
    y_nu_pose = men_config['profondeur_pose']
    
    # Dimensions génériques pour les profilés (Dormant et Ouvrant)
    w_dormant = 45 # Largeur vue de face
    ep_dormant = 60 # Profondeur dans le mur
    w_ouvrant = 65 
    ep_ouvrant = 50 
    
    if a_menuiserie:
        doc.layers.add(name="MENUISERIE", color=couleur_fen)
        doc.layers.add(name="VITRAGE", color=5) 
        doc.layers.add(name="VUE_FOND_ALLEGE", color=8) # Calque fin/gris pour les traits vus en contrebas
        doc.layers.add(name="SYMBOLE_OUVERTURE", color=couleur_fen, linetype="DASHED")
    
    for i, couche in enumerate(couches):
        mat_nom = couche['materiau']
        nom_calque = f"MUR_{i+1}_{mat_nom.upper().replace(' ', '_').replace('/', '_')}"
        doc.layers.add(name=nom_calque, color=MATERIAUX[mat_nom]['couleur'])
        doc.layers.add(name=f"{nom_calque}_HACH", color=MATERIAUX[mat_nom]['couleur'])

    # --- VUE EN PLAN ---
    msp.add_text("VUE EN PLAN (Coupe sur fenêtre)", dxfattribs={'height': 50}).set_placement((0, -150))
    y_plan = 0
    x_trou_debut = (longueur_mur - w_fen) / 2
    x_trou_fin = x_trou_debut + w_fen
    
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        def dessiner_bloc(x_start, x_end, y):
            pts = [(x_start, y), (x_end, y), (x_end, y + ep), (x_start, y + ep)]
            poly = msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, poly, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])

        if a_menuiserie:
            # On dessine les murs de chaque côté
            dessiner_bloc(0, x_trou_debut, y_plan)
            dessiner_bloc(x_trou_fin, longueur_mur, y_plan)
            # ET on dessine les TRAITS DE FOND (Allège) !
            msp.add_line((x_trou_debut, y_plan), (x_trou_fin, y_plan), dxfattribs={'layer': 'VUE_FOND_ALLEGE'})
            msp.add_line((x_trou_debut, y_plan+ep), (x_trou_fin, y_plan+ep), dxfattribs={'layer': 'VUE_FOND_ALLEGE'})
        else:
            dessiner_bloc(0, longueur_mur, y_plan)
            
        y_plan += ep

    # --- Menuiserie Détaillée (Plan) ---
    if a_menuiserie:
        # Dormant Gauche & Droit
        msp.add_lwpolyline([(x_trou_debut, y_nu_pose), (x_trou_debut+w_dormant, y_nu_pose), (x_trou_debut+w_dormant, y_nu_pose+ep_dormant), (x_trou_debut, y_nu_pose+ep_dormant)], close=True, dxfattribs={'layer': "MENUISERIE"})
        msp.add_lwpolyline([(x_trou_fin-w_dormant, y_nu_pose), (x_trou_fin, y_nu_pose), (x_trou_fin, y_nu_pose+ep_dormant), (x_trou_fin-w_dormant, y_nu_pose+ep_dormant)], close=True, dxfattribs={'layer': "MENUISERIE"})
        
        if type_fen == "Ouvrant (à la française)":
            # Ouvrant (Décalé pour l'effet escalier)
            y_ouv_pose = y_nu_pose + 20
            # Ouvrant Gauche & Droit
            msp.add_lwpolyline([(x_trou_debut+w_dormant-10, y_ouv_pose), (x_trou_debut+w_dormant-10+w_ouvrant, y_ouv_pose), (x_trou_debut+w_dormant-10+w_ouvrant, y_ouv_pose+ep_ouvrant), (x_trou_debut+w_dormant-10, y_ouv_pose+ep_ouvrant)], close=True, dxfattribs={'layer': "MENUISERIE"})
            msp.add_lwpolyline([(x_trou_fin-w_dormant+10-w_ouvrant, y_ouv_pose), (x_trou_fin-w_dormant+10, y_ouv_pose), (x_trou_fin-w_dormant+10, y_ouv_pose+ep_ouvrant), (x_trou_fin-w_dormant+10-w_ouvrant, y_ouv_pose+ep_ouvrant)], close=True, dxfattribs={'layer': "MENUISERIE"})
            # Vitrage
            msp.add_line((x_trou_debut+w_dormant-10+w_ouvrant, y_ouv_pose+ep_ouvrant/2), (x_trou_fin-w_dormant+10-w_ouvrant, y_ouv_pose+ep_ouvrant/2), dxfattribs={'layer': "VITRAGE"})
        else:
            # Fixe (Vitrage direct dans le dormant)
            msp.add_line((x_trou_debut+w_dormant, y_nu_pose+ep_dormant/2), (x_trou_fin-w_dormant, y_nu_pose+ep_dormant/2), dxfattribs={'layer': "VITRAGE"})


    # --- VUE EN COUPE VERTICALE ---
    y_coupe_base = - (hauteur_mur + 1000)
    msp.add_text("VUE EN COUPE", dxfattribs={'height': 50}).set_placement((0, y_coupe_base - 150))
    x_coupe = 0
    y_trou_debut = y_coupe_base + allege
    y_trou_fin = y_trou_debut + h_fen
    
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        def dessiner_bloc_v(y_start, y_end):
            pts = [(x_coupe, y_start), (x_coupe + ep, y_start), (x_coupe + ep, y_end), (x_coupe, y_end)]
            poly = msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, poly, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])

        if a_menuiserie:
            dessiner_bloc_v(y_coupe_base, y_trou_debut) # Allège
            dessiner_bloc_v(y_trou_fin, y_coupe_base + hauteur_mur) # Imposte
            # Ligne de fond (Le mur vu de face au loin)
            msp.add_line((x_coupe, y_trou_debut), (x_coupe, y_trou_fin), dxfattribs={'layer': 'VUE_FOND_ALLEGE'})
            msp.add_line((x_coupe+ep, y_trou_debut), (x_coupe+ep, y_trou_fin), dxfattribs={'layer': 'VUE_FOND_ALLEGE'})
        else:
            dessiner_bloc_v(y_coupe_base, y_coupe_base + hauteur_mur)
        x_coupe += ep

    # --- Menuiserie Détaillée (Coupe) ---
    if a_menuiserie:
        # Dormant Bas & Haut
        msp.add_lwpolyline([(y_nu_pose, y_trou_debut), (y_nu_pose+ep_dormant, y_trou_debut), (y_nu_pose+ep_dormant, y_trou_debut+w_dormant), (y_nu_pose, y_trou_debut+w_dormant)], close=True, dxfattribs={'layer': "MENUISERIE"})
        msp.add_lwpolyline([(y_nu_pose, y_trou_fin-w_dormant), (y_nu_pose+ep_dormant, y_trou_fin-w_dormant), (y_nu_pose+ep_dormant, y_trou_fin), (y_nu_pose, y_trou_fin)], close=True, dxfattribs={'layer': "MENUISERIE"})
        
        if type_fen == "Ouvrant (à la française)":
            y_ouv_pose = y_nu_pose + 20
            # Ouvrant Bas & Haut
            msp.add_lwpolyline([(y_ouv_pose, y_trou_debut+w_dormant-10), (y_ouv_pose+ep_ouvrant, y_trou_debut+w_dormant-10), (y_ouv_pose+ep_ouvrant, y_trou_debut+w_dormant-10+w_ouvrant), (y_ouv_pose, y_trou_debut+w_dormant-10+w_ouvrant)], close=True, dxfattribs={'layer': "MENUISERIE"})
            msp.add_lwpolyline([(y_ouv_pose, y_trou_fin-w_dormant+10-w_ouvrant), (y_ouv_pose+ep_ouvrant, y_trou_fin-w_dormant+10-w_ouvrant), (y_ouv_pose+ep_ouvrant, y_trou_fin-w_dormant+10), (y_ouv_pose, y_trou_fin-w_dormant+10)], close=True, dxfattribs={'layer': "MENUISERIE"})
            # Vitrage
            msp.add_line((y_ouv_pose+ep_ouvrant/2, y_trou_debut+w_dormant-10+w_ouvrant), (y_ouv_pose+ep_ouvrant/2, y_trou_fin-w_dormant+10-w_ouvrant), dxfattribs={'layer': "VITRAGE"})
        else:
            msp.add_line((y_nu_pose+ep_dormant/2, y_trou_debut+w_dormant), (y_nu_pose+ep_dormant/2, y_trou_fin-w_dormant), dxfattribs={'layer': "VITRAGE"})

    # --- VUE EN ÉLÉVATION (DE FACE) ---
    if len(couches) > 0:
        couche_ext = couches[-1]
        mat_ext = MATERIAUX[couche_ext['materiau']]
        x_elev = x_coupe + 1500 
        msp.add_text("VUE EN ELEVATION (Façade)", dxfattribs={'height': 50}).set_placement((x_elev, y_coupe_base - 150))
        doc.layers.add(name="VUE_ELEVATION", color=mat_ext['couleur'])
        doc.layers.add(name="VUE_ELEVATION_JOINTS", color=252) # Couleur grise pour les joints
        
        pts_elev = [(x_elev, y_coupe_base), (x_elev + longueur_mur, y_coupe_base), (x_elev + longueur_mur, y_coupe_base + hauteur_mur), (x_elev, y_coupe_base + hauteur_mur)]
        
        trou_pts = None
        if a_menuiserie:
            x_trou_elev = x_elev + x_trou_debut
            trou_pts = [(x_trou_elev, y_trou_debut), (x_trou_elev + w_fen, y_trou_debut), (x_trou_elev + w_fen, y_trou_fin), (x_trou_elev, y_trou_fin)]
            
            # Dormant
            msp.add_lwpolyline(trou_pts, close=True, dxfattribs={'layer': "MENUISERIE"})
            
            vit_pts = [(x_trou_elev+w_dormant, y_trou_debut+w_dormant), (x_trou_elev + w_fen-w_dormant, y_trou_debut+w_dormant), (x_trou_elev + w_fen-w_dormant, y_trou_fin-w_dormant), (x_trou_elev+w_dormant, y_trou_fin-w_dormant)]
            
            if type_fen == "Ouvrant (à la française)":
                # Ouvrant
                ouv_pts = [(x_trou_elev+w_dormant-10, y_trou_debut+w_dormant-10), (x_trou_elev+w_fen-w_dormant+10, y_trou_debut+w_dormant-10), (x_trou_elev+w_fen-w_dormant+10, y_trou_fin-w_dormant+10), (x_trou_elev+w_dormant-10, y_trou_fin-w_dormant+10)]
                msp.add_lwpolyline(ouv_pts, close=True, dxfattribs={'layer': "MENUISERIE"})
                vit_pts = [(x_trou_elev+w_dormant-10+w_ouvrant, y_trou_debut+w_dormant-10+w_ouvrant), (x_trou_elev+w_fen-w_dormant+10-w_ouvrant, y_trou_debut+w_dormant-10+w_ouvrant), (x_trou_elev+w_fen-w_dormant+10-w_ouvrant, y_trou_fin-w_dormant+10-w_ouvrant), (x_trou_elev+w_dormant-10+w_ouvrant, y_trou_fin-w_dormant+10-w_ouvrant)]
                
                # Symbole d'ouverture (Triangle)
                mid_y = (y_trou_debut + y_trou_fin) / 2
                msp.add_line((vit_pts[0][0], vit_pts[0][1]), (vit_pts[1][0], mid_y), dxfattribs={'layer': "SYMBOLE_OUVERTURE"})
                msp.add_line((vit_pts[1][0], mid_y), (vit_pts[0][0], vit_pts[2][1]), dxfattribs={'layer': "SYMBOLE_OUVERTURE"})

            msp.add_lwpolyline(vit_pts, close=True, dxfattribs={'layer': "VITRAGE"})

        # Hachure du mur (avec le trou de la fenêtre)
        poly_elev = msp.add_lwpolyline(pts_elev, close=True, dxfattribs={'layer': "VUE_ELEVATION"})
        dessiner_hachure(msp, poly_elev, pts_elev, "VUE_ELEVATION", mat_ext['motif_elev'], mat_ext['echelle_elev'], mat_ext['angle_elev'], hole_pts=trou_pts)

        # --- NOUVEAU SYSTÈME DE CALEPINAGE (Traits continus cassés par la fenêtre) ---
        if 'calepinage_l' in couche_ext and couche_ext['calepinage_l'] > 0:
            cal_l = couche_ext['calepinage_l']
            cal_h = couche_ext['calepinage_h']
            
            # Lignes verticales
            cal_x = x_elev + cal_l
            while cal_x < x_elev + longueur_mur:
                if a_menuiserie and x_trou_elev < cal_x < x_trou_elev + w_fen:
                    msp.add_line((cal_x, y_coupe_base), (cal_x, y_trou_debut), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                    msp.add_line((cal_x, y_trou_fin), (cal_x, y_coupe_base + hauteur_mur), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                else:
                    msp.add_line((cal_x, y_coupe_base), (cal_x, y_coupe_base + hauteur_mur), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                cal_x += cal_l
                
            # Lignes horizontales
            cal_y = y_coupe_base + cal_h
            while cal_y < y_coupe_base + hauteur_mur:
                if a_menuiserie and y_trou_debut < cal_y < y_trou_fin:
                    msp.add_line((x_elev, cal_y), (x_trou_elev, cal_y), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                    msp.add_line((x_trou_elev + w_fen, cal_y), (x_elev + longueur_mur, cal_y), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                else:
                    msp.add_line((x_elev, cal_y), (x_elev + longueur_mur, cal_y), dxfattribs={'layer': "VUE_ELEVATION_JOINTS"})
                cal_y += cal_h

    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue()


# --- 3. INTERFACE UTILISATEUR ---
st.set_page_config(page_title="Configurateur BIM & CAO", layout="wide")
st.title("🏗️ Configurateur Global de Murs")

tab_mur, tab_men, tab_export = st.tabs(["🧱 1. Composition du Mur", "🪟 2. Menuiseries", "💾 3. Bilan & Export"])

with tab_mur:
    col1, col2 = st.columns(2)
    with col1:
        st.header("Système & Porteur")
        type_mur = st.radio("Principe", ["ITI", "ITE"], horizontal=True)
        mat_structure = st.selectbox("Porteur", ["Béton armé", "Bloc béton (Parpaing)", "Brique creuse", "Brique Monomur", "Ossature Bois (MOB)"])
        ep_structure = st.number_input("Épaisseur porteur (mm)", value=200 if "Bois" not in mat_structure else 145, step=10)
        
        mat_isolant = st.selectbox("Isolant", ["Isolant rigide (PSE/PUR)", "Isolant souple (Laine minérale)", "Isolant naturel (Fibre bois)"])
        ep_isolant = st.number_input("Épaisseur isolant (mm)", value=120, step=10)

    with col2:
        st.header("Finitions")
        st.subheader("Intérieur")
        mat_par_int = st.selectbox("Parement Int.", ["Plaque de plâtre (BA13/Fermacell)", "Panneau OSB / Contreplaqué", "Bois massif", "Carrelage"])
        ep_par_int = st.number_input("Ép. Intérieure (mm)", value=13)
        
        st.subheader("Extérieur")
        mat_par_ext = st.selectbox("Façade", ["Enduit extérieur", "Bardage bois (Horizontal)", "Bardage bois (Vertical)", "Zinc (Joint debout)", "Céramique / Terre cuite", "Panneau Fibre-ciment", "Acier nervuré (Bac acier)"])
        ep_par_ext = st.number_input("Ép. Façade (mm)", value=20)
        type_pose = st.radio("Pose", ["Ventilée (avec lame d'air)", "Non ventilée"])
        
        calepinage_l, calepinage_h = 0, 0
        if mat_par_ext in ["Céramique / Terre cuite", "Panneau Fibre-ciment"]:
            sc1, sc2 = st.columns(2)
            calepinage_l = sc1.number_input("Largeur calepinage (mm)", value=600, step=50)
            calepinage_h = sc2.number_input("Hauteur calepinage (mm)", value=300, step=50)

with tab_men:
    st.header("Intégration d'une ouverture")
    integrer_men = st.toggle("Activer la menuiserie", value=True)
    
    if integrer_men:
        c1, c2 = st.columns(2)
        with c1:
            type_fen = st.radio("Type d'ouverture", ["Ouvrant (à la française)", "Châssis Fixe"])
            mat_fen = st.selectbox("Matériau du châssis", ["Aluminium", "PVC", "Bois", "Mixte Bois/Alu"])
            w_fen = st.number_input("Largeur Tableau (mm)", value=1200, step=100)
            h_fen = st.number_input("Hauteur Tableau (mm)", value=1350, step=50)
            allege = st.number_input("Hauteur de l'allège (mm du sol)", value=900, step=50)
            
        with c2:
            st.info("💡 **Le Nu de pose** détermine la profondeur de la fenêtre dans l'épaisseur du mur.")
            prof_pose = st.slider("Profondeur de pose (mm depuis le nu intérieur)", min_value=0, max_value=500, value=13, step=5)
            
        men_config = {"active": True, "type_ouverture": type_fen, "materiau": mat_fen, "largeur": w_fen, "hauteur": h_fen, "allege": allege, "profondeur_pose": prof_pose}
    else:
        men_config = {"active": False, "materiau": "PVC"}

with tab_export:
    hauteur_mur = st.number_input("Hauteur totale sous plafond (mm)", value=2800, step=100)
    
    if st.button("🔧 Calculer et Générer le Complexe", type="primary", use_container_width=True):
        couches = []
        couches.append({"type": "Continue", "materiau": mat_par_int, "epaisseur": ep_par_int})
        
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

        couche_finition = {"type": "Continue", "materiau": mat_par_ext, "epaisseur": ep_par_ext}
        if calepinage_l > 0:
            couche_finition['calepinage_l'] = calepinage_l
            couche_finition['calepinage_h'] = calepinage_h
        couches.append(couche_finition)
        
        st.session_state.couches_generees = couches
        st.session_state.men_config = men_config
        st.success("Complexe mural assemblé !")

    if 'couches_generees' in st.session_state:
        ep_totale = sum(c['epaisseur'] for c in st.session_state.couches_generees)
        st.info(f"Épaisseur totale réelle du mur : **{ep_totale} mm**")
        dxf_data = generer_dxf(st.session_state.couches_generees, hauteur_mur, st.session_state.men_config)
        st.download_button(label="💾 Télécharger les Plans (.dxf)", data=dxf_data, file_name="mur_complet.dxf", mime="application/dxf", use_container_width=True)
