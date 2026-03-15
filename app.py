import streamlit as st
import ezdxf
import io

# --- 1. BIBLIOTHÈQUE ARCHITECTURALE ---
MATERIAUX = {
    # STRUCTURE LOURDE / MAÇONNERIE
    "Béton armé": {"motif": "AR-CONC", "echelle": 0.5, "angle": 0, "couleur": 1, "motif_elev": "AR-CONC", "echelle_elev": 1.0, "angle_elev": 0},
    "Bloc béton (Parpaing)": {"motif": "AR-B816", "echelle": 0.5, "angle": 0, "couleur": 8, "motif_elev": "AR-B816", "echelle_elev": 1.0, "angle_elev": 0},
    "Brique creuse": {"motif": "ANSI32", "echelle": 1.0, "angle": 0, "couleur": 12, "motif_elev": "AR-BRSTD", "echelle_elev": 1.0, "angle_elev": 0},
    "Brique Monomur": {"motif": "ANSI32", "echelle": 2.0, "angle": 45, "couleur": 12, "motif_elev": "AR-BRSTD", "echelle_elev": 1.0, "angle_elev": 0},
    "Bois massif": {"motif": "ANSI31", "echelle": 1.5, "angle": 0, "couleur": 32, "motif_elev": "LINE", "echelle_elev": 2.0, "angle_elev": 90},
    "Métal (Acier/Alu)": {"motif": "ANSI31", "echelle": 0.5, "angle": 45, "couleur": 250, "motif_elev": "SOLID", "echelle_elev": 1.0, "angle_elev": 0},
    
    # ISOLANTS
    "Isolant rigide (PSE/PUR)": {"motif": "ANSI38", "echelle": 1.0, "angle": 0, "couleur": 3, "motif_elev": "ANSI38", "echelle_elev": 2.0, "angle_elev": 0},
    "Isolant souple (Laine minérale)": {"motif": "HONEY", "echelle": 2.0, "angle": 0, "couleur": 3, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    "Isolant naturel (Fibre bois)": {"motif": "FLEX", "echelle": 1.5, "angle": 0, "couleur": 50, "motif_elev": None, "echelle_elev": 1.0, "angle_elev": 0},
    
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
    
    # VIDES & MEMBRANES
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

# --- 2. MOTEUR DE GÉNÉRATION 3 VUES ---
def generer_dxf(couches, hauteur_mur=2800):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    longueur_mur = 1500 
    
    # 1. Création des calques
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

    # --- VUE 1 : EN PLAN ---
    msp.add_text("VUE EN PLAN (Coupe Horizontale)", dxfattribs={'height': 50}).set_placement((0, -150))
    y_plan = 0
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        # Si c'est continu OU un lattage horizontal (qui apparait continu en vue de dessus)
        if couche['type'] == "Continue" or (couche['type'] == "Structure / Lattage" and couche['orientation'] == "Horizontale (Tasseaux/Rails)"):
            pts = [(0, y_plan), (longueur_mur, y_plan), (longueur_mur, y_plan + ep), (0, y_plan + ep)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            
        # Si c'est une ossature verticale (Montants visibles en plan)
        elif couche['type'] == "Structure / Lattage" and couche['orientation'] == "Verticale (Montants MOB)":
            mat_r = MATERIAUX[couche['materiau_remplissage']]
            nom_calque_r = f"MUR_{i+1}_REMP_{couche['materiau_remplissage'].upper().replace(' ', '_').replace('/', '_')}"
            x_plan = 0
            while x_plan < longueur_mur:
                larg_m = min(couche['largeur_montant'], longueur_mur - x_plan)
                if larg_m > 0:
                    pts_m = [(x_plan, y_plan), (x_plan + larg_m, y_plan), (x_plan + larg_m, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts_m, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts_m, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                x_plan += larg_m
                
                larg_v = min(couche['entraxe'] - couche['largeur_montant'], longueur_mur - x_plan)
                if larg_v > 0:
                    pts_r = [(x_plan, y_plan), (x_plan + larg_v, y_plan), (x_plan + larg_v, y_plan + ep), (x_plan, y_plan + ep)]
                    msp.add_lwpolyline(pts_r, close=True, dxfattribs={'layer': nom_calque_r})
                    dessiner_hachure(msp, pts_r, f"{nom_calque_r}_HACH", mat_r['motif'], mat_r['echelle'], mat_r['angle'])
                x_plan += larg_v
        y_plan += ep

    # --- VUE 2 : EN COUPE VERTICALE ---
    y_coupe_base = - (hauteur_mur + 1000)
    msp.add_text("VUE EN COUPE (Verticale)", dxfattribs={'height': 50}).set_placement((0, y_coupe_base - 150))
    x_coupe = 0
    
    for i, couche in enumerate(couches):
        ep = couche['epaisseur']
        mat = MATERIAUX[couche['materiau']]
        nom_calque = f"MUR_{i+1}_{couche['materiau'].upper().replace(' ', '_').replace('/', '_')}"
        
        if couche['type'] == "Continue":
            pts = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), 
                   (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': nom_calque})
            dessiner_hachure(msp, pts, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
            
        elif couche['type'] == "Structure / Lattage":
            mat_r = MATERIAUX[couche['materiau_remplissage']]
            nom_calque_r = f"MUR_{i+1}_REMP_{couche['materiau_remplissage'].upper().replace(' ', '_').replace('/', '_')}"
            
            # Fond (Remplissage) continu sur toute la hauteur
            pts_fond = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), 
                        (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
            msp.add_lwpolyline(pts_fond, close=True, dxfattribs={'layer': nom_calque_r})
            dessiner_hachure(msp, pts_fond, f"{nom_calque_r}_HACH", mat_r['motif'], mat_r['echelle'], mat_r['angle'])
            
            if couche['orientation'] == "Verticale (Montants MOB)":
                # Lisses (haut et bas)
                lisse_bas = [(x_coupe, y_coupe_base), (x_coupe + ep, y_coupe_base), (x_coupe + ep, y_coupe_base + couche['largeur_montant']), (x_coupe, y_coupe_base + couche['largeur_montant'])]
                lisse_haut = [(x_coupe, y_coupe_base + hauteur_mur - couche['largeur_montant']), (x_coupe + ep, y_coupe_base + hauteur_mur - couche['largeur_montant']), (x_coupe + ep, y_coupe_base + hauteur_mur), (x_coupe, y_coupe_base + hauteur_mur)]
                for lisse in [lisse_bas, lisse_haut]:
                    msp.add_lwpolyline(lisse, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, lisse, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                
                # Entretoises intermédiaires (tous les X mm)
                espacement_entretoises = couche.get('entraxe_secondaire', 1250)
                y_ent = y_coupe_base + espacement_entretoises
                while y_ent < (y_coupe_base + hauteur_mur - couche['largeur_montant']):
                    pts_ent = [(x_coupe, y_ent), (x_coupe + ep, y_ent), (x_coupe + ep, y_ent + couche['largeur_montant']), (x_coupe, y_ent + couche['largeur_montant'])]
                    msp.add_lwpolyline(pts_ent, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts_ent, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                    y_ent += espacement_entretoises

            elif couche['orientation'] == "Horizontale (Tasseaux/Rails)":
                # Lattage horizontal visible espacé en coupe
                espacement_tasseaux = couche['entraxe']
                y_tass = y_coupe_base
                while y_tass < (y_coupe_base + hauteur_mur):
                    h_tass = min(couche['largeur_montant'], (y_coupe_base + hauteur_mur) - y_tass)
                    pts_tass = [(x_coupe, y_tass), (x_coupe + ep, y_tass), (x_coupe + ep, y_tass + h_tass), (x_coupe, y_tass + h_tass)]
                    msp.add_lwpolyline(pts_tass, close=True, dxfattribs={'layer': nom_calque})
                    dessiner_hachure(msp, pts_tass, f"{nom_calque}_HACH", mat['motif'], mat['echelle'], mat['angle'])
                    y_tass += espacement_tasseaux
        x_coupe += ep

    # --- VUE 3 : ÉLÉVATION / FAÇADE ---
    if len(couches) > 0:
        couche_ext = couches[-1]
        mat_ext = MATERIAUX[couche_ext['materiau']]
        x_elev = x_coupe + 1000 
        
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
    if c2.button("➕ Ajouter Structure / Lattage"):
        st.session_state.couches.append({"type": "Structure / Lattage", "orientation": "Verticale (Montants MOB)", "epaisseur": 145, "materiau": "Bois massif", "materiau_remplissage": "Isolant souple (Laine minérale)", "largeur_montant": 45, "entraxe": 600, "entraxe_secondaire": 1250})
        st.rerun()

    for i, couche in enumerate(st.session_state.couches):
        with st.expander(f"Couche {i+1} : {couche['materiau']} ({couche['epaisseur']}mm)", expanded=True):
            cols = st.columns([3, 2, 1])
            
            couche['materiau'] = cols[0].selectbox("Matériau", list(MATERIAUX.keys()), index=list(MATERIAUX.keys()).index(couche.get('materiau', 'Béton armé')), key=f"mat_{i}")
            couche['epaisseur'] = cols[1].number_input("Épaisseur (mm)", min_value=1, value=couche['epaisseur'], key=f"ep_{i}")
            if cols[2].button("🗑️ Supprimer", key=f"del_{i}"):
                st.session_state.couches.pop(i)
                st.rerun()

            if couche['type'] == "Structure / Lattage":
                couche['orientation'] = st.radio("Sens de l'ossature", ["Verticale (Montants MOB)", "Horizontale (Tasseaux/Rails)"], index=0 if couche.get('orientation', 'Verticale (Montants MOB)') == "Verticale (Montants MOB)" else 1, key=f"ori_{i}")
                
                sc1, sc2 = st.columns(2)
                couche['materiau_remplissage'] = sc1.selectbox("Remplissage / Vide", list(MATERIAUX.keys()), index=list(MATERIAUX.keys()).index(couche.get('materiau_remplissage', 'Vide / Lame d\'air')), key=f"remp_{i}")
                couche['largeur_montant'] = sc2.number_input("Largeur du profilé (mm)", value=couche.get('largeur_montant', 45), key=f"larg_{i}")
                
                sc3, sc4 = st.columns(2)
                couche['entraxe'] = sc3.number_input("Entraxe principal (mm)", value=couche.get('entraxe', 600), key=f"ent_{i}")
                
                if couche['orientation'] == "Verticale (Montants MOB)":
                    couche['entraxe_secondaire'] = sc4.number_input("Entraxe des entretoises (mm)", value=couche.get('entraxe_secondaire', 1250), help="Distance entre les traverses horizontales", key=f"ent_sec_{i}")

with col2:
    st.subheader("2. Bilan & Export")
    hauteur_mur = st.number_input("Hauteur sous plafond (mm)", value=3000, step=100)
    
    if not st.session_state.couches:
        st.info("Ajoutez des couches pour commencer la conception.")
    else:
        epaisseur_totale = sum(c['epaisseur'] for c in st.session_state.couches)
        st.success(f"**Épaisseur du complexe : {epaisseur_totale} mm**")
        st.write(f"Nombre de couches : {len(st.session_state.couches)}")
        
        dxf_data = generer_dxf(st.session_state.couches, hauteur_mur)
        st.download_button(
            label="💾 Télécharger les Plans (.dxf)",
            data=dxf_data,
            file_name="mur_complet_v3.dxf",
            mime="application/dxf",
            use_container_width=True
        )
