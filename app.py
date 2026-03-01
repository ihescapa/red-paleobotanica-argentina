import streamlit as st
import pandas as pd
from models import Session, Researcher, Relationship, User, AuditLog, Suggestion, engine
from sqlalchemy.orm import joinedload
from auth import login_user, register_user
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import base64
import json
import math
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import shutil

# --- AUTO BACKUP ---
def perform_daily_backup():
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    today_str = datetime.now().strftime("%Y-%m-%d")
    db_path = "genealogy.db"
    backup_path = os.path.join(backup_dir, f"genealogy_backup_{today_str}.db")
    if os.path.exists(db_path) and not os.path.exists(backup_path):
        try:
            shutil.copy2(db_path, backup_path)
            # st.toast(f"Backup automático creado: {backup_path}")
        except: pass

perform_daily_backup()


def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
    return None

def generate_pie_node_svg(colors):
    """Generates a base64 encoded SVG pie chart for PyVis nodes."""
    if not colors:
        return None
    
    n = len(colors)
    if n == 1:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <circle cx="50" cy="50" r="45" fill="{colors[0]}" stroke="white" stroke-width="2"/>
        </svg>'''
    else:
        slices = []
        angle_per_slice = 360 / n
        
        for i, color in enumerate(colors):
            start_angle = i * angle_per_slice
            end_angle = (i + 1) * angle_per_slice
            
            def polar_to_cartesian(cx, cy, r, angle_deg):
                angle_rad = (angle_deg - 90) * math.pi / 180.0
                return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)
            
            x1, y1 = polar_to_cartesian(50, 50, 45, start_angle)
            x2, y2 = polar_to_cartesian(50, 50, 45, end_angle)
            
            large_arc = 0 if angle_per_slice <= 180 else 1
            
            path_data = f"M 50 50 L {x1} {y1} A 45 45 0 {large_arc} 1 {x2} {y2} Z"
            slices.append(f'<path d="{path_data}" fill="{color}" stroke="white" stroke-width="1"/>')
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            {"".join(slices)}
            <circle cx="50" cy="50" r="45" fill="none" stroke="white" stroke-width="2"/>
        </svg>'''
    
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"


# --- PAGE CONFIG ---
st.set_page_config(
    layout="wide", 
    page_title="Genealogía Paleobotánica",
    page_icon="🌿",
    initial_sidebar_state="collapsed"
)

# --- CSS (HIGH DESIGN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        color: #333333;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        color: #1A1A1A;
    }
    .stCard {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- HELPERS ---
def get_researchers():
    session = Session()
    # Eager load publications to avoid DetachedInstanceError when session closes
    researchers = session.query(Researcher).options(joinedload(Researcher.publications)).all()
    session.close()
    return researchers

def get_relationships():
    session = Session()
    # Eager load student and director to avoid DetachedInstanceError if accessed later
    rels = session.query(Relationship).options(joinedload(Relationship.student), joinedload(Relationship.director)).all()
    session.close()
    return rels

def add_audit_log(user_id, action, target_type, target_id, details):
    session = Session()
    log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    session.add(log)
    session.commit()
    session.close()

def add_suggestion(user_id, target_type, target_id, changes):
    session = Session()
    sug = Suggestion(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        suggested_changes=changes,
        status="Pending"
    )
    session.add(sug)
    session.commit()
    session.close()

# --- VISUALIZATION FUNCTIONS ---
def get_monochromatic_color(role):
    # Monochromatic Blue Scale (Dark to Light)
    if role and "Pionero" in role: return "#0D47A1"  # Darkest Blue
    if role and "Formador" in role: return "#1565C0" # Dark Blue
    if role and "Investigador" in role: return "#42A5F5" # Medium Blue
    if role and "Becario" in role: return "#90CAF9"  # Lightest Blue
    return "#2196F3" # Default
def get_font_color(role):
    # White text for dark backgrounds
    if role and ("Pionero" in role or "Formador" in role): return "white"
    return "black"

def apply_graph_settings(net, hierarchical=False):    # Configure visualization options
    options = {
        "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "font": { "size": 14, "face": "Lato" }
        },
        "edges": {
            "smooth": { "type": "continuous", "roundness": 0.5 },
            "color": { "inherit": "both" },
            "width": 2
        },
        "interaction": { 
            "hover": True, 
            "navigationButtons": True,
            "selectConnectedEdges": False,
            "zoomView": True,
            "dragView": True,
            "zoomSpeed": 0.5,
            "minZoom": 0.1, # Relaxed global limit to allow seeing large trees
            "maxZoom": 2.5,
            "keyboard": {
                "enabled": True,
                "speed": {"x": 10, "y": 10, "zoom": 0.02}
            }
        }
    }

    if hierarchical:
        options["layout"] = {
            "hierarchical": {
                "enabled": True,
                "direction": "DU", # Bottom-to-Top (Roots/Directors at bottom)
                "sortMethod": "directed",
                "levelSeparation": 150, # Slightly more space for taxonomic lines
                "nodeSpacing": 100,
                "treeSpacing": 150,
                "blockShifting": True,
                "edgeMinimization": True,
                "parentCentralization": True
            }
        }
        options["edges"] = {
            "smooth": {
                "type": "taxi",
                "taxiDirection": "vertical",
                "roundness": 0.2
            },
            "color": { "inherit": "both" },
            "width": 2
        }
        options["physics"] = {
            "enabled": False # Disable physics for strict hierarchical look
        }
    else:
        options["physics"] = {
            "forceAtlas2Based": {
                "gravitationalConstant": -60,
                "centralGravity": 0.015,
                "springLength": 120,
                "springConstant": 0.08,
                "damping": 0.4,
                "avoidOverlap": 0.5
            },
            "solver": "forceAtlas2Based",
            "stabilization": {
                "enabled": True,
                "iterations": 150, 
                "updateInterval": 25,
                "onlyDynamicEdges": False,
                "fit": True
            }
        }

    net.set_options(json.dumps(options))
    return net

def add_nodes_to_graph(net, researchers, ids_to_include=None, highlight_id=None, levels=None, theme_filters=None):
    for r in researchers:
        # Ensure we don't skip the highlighted node even if it would be filtered out as isolated
        is_highlighted = highlight_id and r.id == highlight_id
        if ids_to_include is not None and r.id not in ids_to_include and not is_highlighted:
            continue
            
        # 1. Handle Theme Highlights (Pie Charts)
        matched_colors = []
        if theme_filters:
            r_keywords_str = (r.keywords or "").lower()
            for key, color in theme_filters:
                if key and key in r_keywords_str:
                    matched_colors.append(color)
        
        node_shape = "dot"
        node_image = None
        
        # 2. Base Highlight logic
        if len(matched_colors) > 1:
            node_shape = "image"
            node_image = generate_pie_node_svg(matched_colors)
            color = "#FFFFFF"
            size = 25 # Slightly larger for pie charts
        elif len(matched_colors) == 1:
            color = matched_colors[0]
            size = 22
        elif r.is_phd_in_progress:
            color = "#FF7043" # Distinct Coraly/Orange for PhD in progress
            size = 18
        elif is_highlighted:
            color = "#FFD700"  # Bright gold for highlighted node
            size = 35
        else:
            color = "#2E5C8A"  # Uniform SAPP blue for all nodes
            size = 18
        
        font_color = "white"
        
        # Header Info
        extra_status = ""
        verification_status = ""
        if r.verified:
            verification_status = " <span style='color:#4CAF50; font-size:0.8em; font-weight:bold;'>[CORROBORADO]</span>"
        else:
            verification_status = " <span style='color:#FFD700; font-size:0.8em; font-weight:bold;'>[DATO SIN CORROBORAR]</span>"
            
        if r.is_phd_in_progress:
            extra_status = " <span style='color:#FF5722; font-weight:bold;'>[DOCTORADO EN CURSO]</span>"
            
        # Sanitize data for HTML/JS
        r_name_clean = r.name.replace("'", "&#39;")
        r_inst_clean = (r.institution or 'N/A').replace("'", "&#39;")
        r_role_clean = r.role.replace("'", "&#39;")
        r_notes_clean = (r.notes or '').replace("'", "&#39;").replace("\n", " ")

        # 1. Header with Name and Status
        header_html = f"""
        <div style='background-color: {color}; color: {font_color}; padding: 12px; border-radius: 8px 8px 0 0; margin: -10px -10px 10px -10px;'>
            <h3 style='margin: 0; font-size: 1.1em; font-weight: 700; line-height: 1.2;'>{r_name_clean}{extra_status}</h3>
            <div style='margin-top: 4px;'>{verification_status}</div>
        </div>
        """

        # 2. Main Info Section
        info_html = f"""
        <div style='margin-bottom: 12px; font-size: 0.9em; line-height: 1.4;'>
            <div style='margin-bottom: 4px;'><b>🏛️ Institución:</b> {r_inst_clean}</div>
            <div style='margin-bottom: 4px;'><b>📍 Ubicación:</b> {r.city or '?'}, {r.province or '?'}</div>
            <div style='margin-bottom: 4px;'><b>🎓 Rol:</b> {r_role_clean}</div>
            <div style='margin-bottom: 4px;'><b>📚 Años de Publicación:</b> {r.activity_start or '?'}-{r.activity_end or '?'}</div>
        </div>
        """

        # 3. Profile Links (Modern Badges)
        badge_style = "display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.75em; text-decoration: none; margin-right: 4px; margin-bottom: 4px; font-weight: 600; transition: transform 0.1s;"
        
        profile_links = []
        if r.scholar_url:
            profile_links.append(f"<a href='{r.scholar_url}' target='_blank' style='{badge_style} background-color: #E8F0FE; color: #4285F4; border: 1px solid #4285F4;'>🎓 Scholar</a>")
        else:
            profile_links.append(f"<span style='{badge_style} background-color: #f5f5f5; color: #ccc; border: 1px solid #ddd;'>🎓 Scholar</span>")
            
        if r.researchgate_url:
            profile_links.append(f"<a href='{r.researchgate_url}' target='_blank' style='{badge_style} background-color: #E0F2F1; color: #00ccbb; border: 1px solid #00ccbb;'>📚 ResearchGate</a>")
        else:
            profile_links.append(f"<span style='{badge_style} background-color: #f5f5f5; color: #ccc; border: 1px solid #ddd;'>📚 RG</span>")
            
        if hasattr(r, 'orcid_url') and r.orcid_url:
            profile_links.append(f"<a href='{r.orcid_url}' target='_blank' style='{badge_style} background-color: #F1F8E9; color: #A6CE39; border: 1px solid #A6CE39;'>🆔 ORCID</a>")
        else:
            profile_links.append(f"<span style='{badge_style} background-color: #f5f5f5; color: #ccc; border: 1px solid #ddd;'>🆔 ORCID</span>")
        
        profiles_section = f"<div style='margin: 10px 0;'>{' '.join(profile_links)}</div>"

        # 4. Photo Section
        photo_section = ""
        if r.photo_url:
            photo_section = f"<div style='text-align: center; margin: 10px 0;'><a href='{r.photo_url}' target='_blank' style='display: block;'><img src='{r.photo_url}' style='width: 100%; max-height: 150px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;' alt='{r_name_clean}'></a></div>"

        # 5. Publications section
        pubs_section = ""
        if hasattr(r, 'publications') and r.publications:
            sorted_pubs = sorted(r.publications, key=lambda x: x.citation_count or 0, reverse=True)[:3] # Show 3 for compact look
            pub_items = "".join([f"<div style='margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1px solid #f0f0f0; font-size: 0.78em;'>{p.title[:60]}{'...' if len(p.title)>60 else ''} <span style='color: #888;'>({p.year})</span></div>" for p in sorted_pubs])
            pubs_section = f"""
            <div style='margin-top: 12px; border-top: 2px solid #eee; padding-top: 8px;'>
                <div style='font-weight: 700; font-size: 0.8em; color: #333; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;'>📄 Top Publicaciones</div>
                {pub_items}
            </div>
            """

        # 6. Keywords section
        keywords_section = ""
        if r.keywords:
            kw_list = r.keywords.split(",")
            kw_badges = "".join([f"<span style='display:inline-block; background:#e1f5fe; color:#0288d1; padding:2px 6px; border-radius:4px; font-size:0.75em; margin:2px; font-weight:600;'>#{kw.strip()}</span>" for kw in kw_list])
            keywords_section = f"<div style='margin-top: 10px; border-top: 1px solid #eee; padding-top: 5px;'>{kw_badges}</div>"

        # 7. Notes section
        notes_section = ""
        if r_notes_clean:
            notes_section = f"<div style='font-style: italic; font-size: 0.75em; margin-top: 10px; color: #666; background: #fafafa; padding: 6px; border-radius: 4px;'>{r_notes_clean}</div>"

        # Final Assembly
        title_html = f"""
        <div style='font-family: \"Inter\", \"Lato\", sans-serif; padding: 10px; width: 280px; box-sizing: border-box; background: white; color: #333;'>
            {header_html}
            {info_html}
            {profiles_section}
            {photo_section}
            {pubs_section}
            {keywords_section}
            {notes_section}
        </div>
        """
        
        # Replace actual newlines with spaces to avoid breaking JS string literals
        title_html = title_html.replace("\n", " ").replace("\r", " ")
        
        node_opts = {
            "label": r.name, 
            "title": title_html, 
            "color": color, 
            "shape": node_shape, 
            "size": size,
            "font": {"color": font_color}
        }
        
        if node_image:
            node_opts["image"] = node_image

        if levels and r.id in levels:
            node_opts["level"] = levels[r.id]
            
        net.add_node(r.id, **node_opts)


def generate_graph_html(researchers, relationships, show_dir_doc=False, show_codir_doc=False, show_dir_post=False, show_codir_post=False, highlight_id=None, height="700px", hierarchical=False, theme_filters=None):
    net = Network(height=height, width="100%", bgcolor="#ffffff", font_color="#333333", directed=True)
    
    # Apply settings
    net = apply_graph_settings(net, hierarchical=hierarchical)
    
    # 1. Filter Isolated Nodes (For hierarchical only)
    connected_ids = set()
    for rel in relationships:
        if hierarchical and rel.type == "Secondary": continue # Tree shape primarily based on Primary docs
        connected_ids.add(rel.student_id)
        connected_ids.add(rel.director_id)
        
    # If hierarchical, ONLY show connected nodes. If network, show all.
    nodes_to_render = connected_ids if hierarchical else None
    
    # If hierarchical, calculate levels based on academic generation (topological distance)
    # (Keep level assignment logic same)
    levels = None
    if hierarchical:
        levels = {}
        student_to_director = {}
        for rel in relationships:
            if rel.type == "Secondary": continue
            student_to_director[rel.student_id] = rel.director_id
            
        roots = set()
        for rid in connected_ids:
            if rid not in student_to_director:
                roots.add(rid)
        
        memo = {}
        def get_topological_level(rid, depth=0):
            if rid in memo: return memo[rid]
            if depth > 20: return 0
            if rid not in student_to_director:
                memo[rid] = 0
                return 0
            parent_id = student_to_director[rid]
            parent_lvl = get_topological_level(parent_id, depth + 1)
            memo[rid] = parent_lvl + 1
            return memo[rid]
            
        for rid in connected_ids:
            levels[rid] = get_topological_level(rid)

    # Add nodes
    add_nodes_to_graph(net, researchers, ids_to_include=nodes_to_render, highlight_id=highlight_id, levels=levels, theme_filters=theme_filters)
    
    # Add relationships
    seen_students = set()
    for rel in relationships:
        # Filter based on user selection
        if rel.type in ("Primary", "Doctorado", "Doctoral Director") and not show_dir_doc: continue
        if rel.type == "Secondary" and not show_codir_doc: continue
        if rel.type == "Postdoc" and not show_dir_post: continue
        if rel.type == "Co-Postdoc" and not show_codir_post: continue
        
        # Catch anything else (safety guard): if it's not checked by the above, hide it.
        if rel.type not in ("Primary", "Doctorado", "Doctoral Director"):
            if rel.type != "Secondary" and rel.type != "Postdoc" and rel.type != "Co-Postdoc":
                continue
        
        # In hierarchical mode, enforce a strict tree (one incoming connection per student, usually via primary)
        if hierarchical:
            if rel.student_id in seen_students:
                continue
            seen_students.add(rel.student_id)

        color = "#2E5C8A" # Primary doc (Solid deep SAPP blue)
        dashes = False
        width = 2
        
        if rel.type == "Secondary":
            color = "#64B5F6" # Lighter blue for codir
            dashes = [5, 5]
            width = 1
        elif rel.type == "Postdoc":
            color = "#F57C00" # Distinct orange for Postdoc
            dashes = False
            width = 2
        elif rel.type == "Co-Postdoc":
            color = "#FFB74D" # Light orange for Co-Postdoc
            dashes = [2, 4]
            width = 1
        
        net.add_edge(rel.director_id, rel.student_id, color={"color": color, "highlight": "#ff0000"}, dashes=dashes, width=width)
        
    # Finalize settings and return
    path = "graph_pro.html"
    net.save_graph(path)
    
    # Calculate isolated researchers for display (based on what we actually showed)
    connected_current = set()
    for edge in net.edges:
        connected_current.add(edge['from'])
        connected_current.add(edge['to'])
    
    isolated_researchers = [r for r in researchers if r.id not in connected_current]
    
    return path, isolated_researchers

def render_graph_page(researchers, relationships, hierarchical=False, theme_filters=None):
    # THEMATIC SEARCH (in Sidebar)
    st.sidebar.markdown("### 🧬 Búsqueda Temática")
    st.sidebar.caption("Iluminar por palabra clave:")
    
    k1 = st.sidebar.text_input("k1", key=f"k1_{hierarchical}", placeholder="Filtro 1", label_visibility="collapsed")
    c1 = st.sidebar.color_picker("Color 1", "#FF5252", key=f"c1_{hierarchical}", label_visibility="collapsed")
    
    k2 = st.sidebar.text_input("k2", key=f"k2_{hierarchical}", placeholder="Filtro 2", label_visibility="collapsed")
    c2 = st.sidebar.color_picker("Color 2", "#4CAF50", key=f"c2_{hierarchical}", label_visibility="collapsed")
    
    k3 = st.sidebar.text_input("k3", key=f"k3_{hierarchical}", placeholder="Filtro 3", label_visibility="collapsed")
    c3 = st.sidebar.color_picker("Color 3", "#2196F3", key=f"c3_{hierarchical}", label_visibility="collapsed")
    
    theme_filters = []
    if k1: theme_filters.append((k1.lower(), c1))
    if k2: theme_filters.append((k2.lower(), c2))
    if k3: theme_filters.append((k3.lower(), c3))

    # TOP ROW CONTROLS
    key_suffix = "_tree" if hierarchical else "_net"
    search_query = st.text_input("🔍 Buscar Investigador", key=f"search_box{key_suffix}", placeholder="Ej: Archangelsky")
    
    st.markdown("**Filtros de Relación:**")
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    with filter_col1: show_dir_doc = st.checkbox("Dirección de Doc.", value=False, key=f"sd_{key_suffix}")
    with filter_col2: show_codir_doc = st.checkbox("Co-dirección", value=False, key=f"sc_{key_suffix}")
    with filter_col3: show_dir_post = st.checkbox("Dirección de Postdoc", value=False, key=f"sp_{key_suffix}")
    with filter_col4: show_codir_post = st.checkbox("Co-dirección Postdoc", value=False, key=f"scp_{key_suffix}")
    
    # Highlight searched researcher
    highlight_id = None
    if search_query:
        for r in researchers:
            if search_query.lower() in r.name.lower():
                highlight_id = r.id
                st.info(f"✓ Encontrado: **{r.name}** ({r.institution or 'N/A'})")
                break
        if not highlight_id:
            st.warning(f"No se encontró: '{search_query}'")
    
    height = 800 # Slightly shorter to fit toggles
    path, isolated_rearchers = generate_graph_html(researchers, relationships, show_dir_doc, show_codir_doc, show_dir_post, show_codir_post, highlight_id, height=f"{height}px", hierarchical=hierarchical, theme_filters=theme_filters)
    
    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
        # 1. Inject JS for HTML Tooltips (intercept vis.js tooltip popup)
        tooltip_js = """
        <script>
        setTimeout(function() {
            if (typeof network !== 'undefined') {
                network.on("showPopup", function(id) {
                    // Small delay to let the tooltip element be created/updated
                    setTimeout(function() {
                        var tooltips = document.getElementsByClassName("vis-tooltip");
                        if (tooltips.length > 0) {
                            var tooltip = tooltips[0];
                            // If it contains our div marker, convert text to HTML
                            var content = tooltip.innerText || tooltip.textContent;
                            if (content.includes("<div")) {
                                tooltip.innerHTML = content;
                                // Force vis-tooltip styles
                                tooltip.style.backgroundColor = "white";
                                tooltip.style.color = "black";
                                tooltip.style.border = "1px solid #ddd";
                                tooltip.style.borderRadius = "8px";
                                tooltip.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
                                tooltip.style.padding = "0";
                                tooltip.style.maxWidth = "400px";
                                tooltip.style.pointerEvents = "auto"; // Ensure links are clickable
                            }
                        }
                    }, 50);
                });
            }
        }, 1000);
        </script>
        """
        
        # 2. Inject JS to HARD LIMIT zoom out and keep network in view
        zoom_limit_val = 0.05 if hierarchical else 0.35
        zoom_limit_js = f"""
        <script>
        setTimeout(function() {{
            if (typeof network !== 'undefined') {{
                network.on("zoom", function(params) {{
                    if (params.scale < {zoom_limit_val}) {{
                        network.moveTo({{ 
                            scale: {zoom_limit_val}, 
                            animation: {{duration: 150, easingFunction: 'linear'}} 
                        }});
                    }}
                }});
            }}
        }}, 650);
        </script>
        """
        
        # 3. Inject JS for Multi-level Highlighting
        multi_level_highlight_js = """
        <script>
        setTimeout(function() {
            if (typeof network !== 'undefined' && typeof nodes !== 'undefined' && typeof edges !== 'undefined') {
                
                // Store original state
                var allNodes = nodes.get({returnType:"Object"});
                var allEdges = edges.get({returnType:"Object"});
                
                var updateNodesInit = [];
                for (var nodeId in allNodes) {
                    var n = allNodes[nodeId];
                    updateNodesInit.push({
                        id: nodeId, 
                        originalColor: n.color, 
                        originalFontColor: (n.font && n.font.color) ? n.font.color : "white"
                    });
                }
                nodes.update(updateNodesInit);
                
                var updateEdgesInit = [];
                for (var edgeId in allEdges) {
                    var e = allEdges[edgeId];
                    var baseColor = e.color;
                    if (typeof e.color === 'object' && e.color !== null) {
                        baseColor = e.color.color;
                    }
                    updateEdgesInit.push({
                        id: edgeId, 
                        originalColor: baseColor, 
                        originalWidth: e.width || 1
                    });
                }
                edges.update(updateEdgesInit);

                network.on("selectNode", function (params) {
                    var selectedId = params.nodes[0];
                    var directors = []; // edges
                    var students = [];  // edges
                    var grandStudents = []; // edges
                    
                    var connectedNodes = [selectedId];

                    for (var edgeId in allEdges) {
                        var edge = allEdges[edgeId];
                        if (edge.to === selectedId) {
                            directors.push(edge);
                            connectedNodes.push(edge.from);
                        } else if (edge.from === selectedId) {
                            students.push(edge);
                            connectedNodes.push(edge.to);
                        }
                    }
                    
                    var studentIds = students.map(e => e.to);
                    for (var edgeId in allEdges) {
                        var edge = allEdges[edgeId];
                        if (studentIds.includes(edge.from) && edge.to !== selectedId) {
                            grandStudents.push(edge);
                            connectedNodes.push(edge.to);
                        }
                    }
                    
                    // Apply Node Fade
                    var updateNodes = [];
                    for (var nodeId in allNodes) {
                        var isConnected = connectedNodes.includes(nodeId);
                        var fadeOpacity = isConnected ? 1 : 0.15;
                        var fontOpacity = isConnected ? 1 : 0;
                        
                        updateNodes.push({
                            id: nodeId, 
                            opacity: fadeOpacity,
                            font: { color: isConnected ? allNodes[nodeId].originalFontColor : "rgba(0,0,0,0)" }
                        });
                    }
                    nodes.update(updateNodes);
                    
                    // Apply Edge Highlights
                    var updateEdges = [];
                    for (var edgeId in allEdges) {
                        var edge = allEdges[edgeId];
                        var newColor = "rgba(180,180,180,0.18)";
                        var newWidth = 1;
                        var hidden = false; // Never completely hide, just fade out
                        
                        if (directors.includes(edge)) {
                            newColor = "#FF9800"; // Naranja (Directores)
                            newWidth = 3;
                            hidden = false;
                        } else if (students.includes(edge)) {
                            newColor = "#F44336"; // Rojo (Dirigidos)
                            newWidth = 3;
                            hidden = false;
                        } else if (grandStudents.includes(edge)) {
                            newColor = "#4CAF50"; // Verde (Dirigidos de dirigidos)
                            newWidth = 2;
                            hidden = false;
                        }
                        
                        updateEdges.push({
                            id: edgeId, 
                            color: { color: newColor, highlight: newColor, hover: newColor },
                            width: newWidth,
                            hidden: hidden
                        });
                    }
                    edges.update(updateEdges);
                });

                network.on("deselectNode", function (params) {
                    var updateNodes = [];
                    for (var nodeId in allNodes) {
                        updateNodes.push({
                            id: nodeId, 
                            opacity: 1, 
                            font: { color: allNodes[nodeId].originalFontColor }
                        });
                    }
                    nodes.update(updateNodes);
                    
                    var updateEdges = [];
                    for (var edgeId in allEdges) {
                        var e = allEdges[edgeId];
                        updateEdges.push({
                            id: edgeId, 
                            color: { color: e.originalColor, highlight: "#ff0000" },
                            width: e.originalWidth,
                            hidden: false
                        });
                    }
                    edges.update(updateEdges);
                });
            }
        }, 1200);
        </script>
        """
        
        html_content = html_content.replace("</body>", tooltip_js + zoom_limit_js + multi_level_highlight_js + "</body>")
        components.html(html_content, height=height + 50)

    if isolated_rearchers:
        st.caption(f"ℹ️ {len(isolated_rearchers)} investigadores aislados no se muestran en el gráfico principal.")

def generate_hierarchical_html(researchers, relationships):
    net = Network(height="750px", width="100%", bgcolor="#f8f9fa", font_color="#333", directed=True) # Soft light background for Tree
    
    # Enable High Design CSS in HTML
    # We will inject some custom CSS at the end.

    
    connected_ids = set()
    for rel in relationships:
        connected_ids.add(rel.student_id)
        connected_ids.add(rel.director_id)
        
    add_nodes_to_graph(net, researchers, ids_to_include=connected_ids)
    
    for rel in relationships:
        color = "#B0BEC5"
        if rel.type == "Secondary": color = "#CFD8DC"
        if rel.student_id in connected_ids and rel.director_id in connected_ids:
            net.add_edge(rel.director_id, rel.student_id, color=color)

    apply_graph_settings(net, hierarchical=True)
    
    path = "tree_viz.html"
    net.save_graph(path)
    return path


# --- AUTH VIEW ---
def auth_page():
    # Logo on Top for Login
    logo_path = "assets/images/sapp_logo.jpg"
    if os.path.exists(logo_path):
        col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
        with col_l2:
            st.image(logo_path, use_container_width=True)
            
    st.markdown("<h1 style='text-align: center; margin-bottom: 40px; color: #2E5C8A;'>Red de Paleobotánica y Palinología Argentina</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_reigster = st.tabs(["Ingresar", "Registrarse"])
        with tab_login:
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.button("Iniciar Sesión", use_container_width=True):
                user = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Error de credenciales")
        with tab_reigster:
            new_user = st.text_input("Nuevo Usuario")
            new_pass = st.text_input("Nueva Contraseña", type="password")
            full_name = st.text_input("Nombre y Apellido")
            institution = st.text_input("Institución")
            if st.button("Crear Cuenta", use_container_width=True):
                success, msg = register_user(new_user, new_pass, full_name, institution)
                if success: st.success(msg)
                else: st.error(msg)

# --- MAIN APP ---
def main_app():
    user = st.session_state.user
    
    # Sidebar Header
    logo_path = "assets/images/sapp_logo.jpg"
    if os.path.exists(logo_path):
        col_logo_sb1, col_logo_sb2, col_logo_sb3 = st.sidebar.columns([1, 2, 1])
        with col_logo_sb2:
            st.image(logo_path, use_container_width=True)
    
    st.sidebar.markdown(f"### Red de Paleobotánica<br><span style='font-size: 0.8em; color: gray;'>y Palinología Argentina</span>", unsafe_allow_html=True)
    st.sidebar.caption(f"👤 {user.full_name} ({user.institution})")
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    st.sidebar.markdown("---")
    
    # Navigation
    options = ["Red General", "Análisis de Red, Género y Región", "Colaboradores/as", "Administración"]
    
    # Pre-selection logic for Redirects (from Corroboration/Suggestions to Admin)
    default_page_idx = 0
    if st.session_state.get("page_redirect"):
        dest = st.session_state.page_redirect
        if dest in options:
            default_page_idx = options.index(dest)
        st.session_state.page_redirect = None # Clear after use
    
    page = st.sidebar.radio("Navegación", options, index=default_page_idx)

    # Sidebar Bottom Logo
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    try:
        st.sidebar.markdown("""
            <div style='background: white; padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-top: auto;'>
                <img src='data:image/jpeg;base64,{}' style='width: 80%; max-width: 150px;'>
                <p style='color: #2E5C8A; font-size: 10px; margin-top: 8px; font-weight: 600; line-height: 1.2;'>
                    58º AASP-TPS Annual Meeting<br>19º SAPP
                </p>
            </div>
        """.format(get_base64_image("assets/images/sapp_logo.jpg")), unsafe_allow_html=True)
    except:
        pass

    # Fetch data once for usage in visualization pages
    researchers = get_researchers()
    relationships = get_relationships()

    # Introduction Texts Generator Box (Beautiful UI block)
    def render_intro(title, text, is_admin=False):
        admin_note = "<div style='margin-top: 10px; font-size: 0.85em; color: #d32f2f; font-weight: bold;'>🔒 Acceso Restringido. En caso de solicitar acceso de edición, o si detectó un error, escribir a iescapa@gmail.com o utilizar la pestaña 'Sugerir Corrección'.</div>" if is_admin else ""
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #ffffff, #f0f4f8); border-left: 5px solid #2E5C8A; padding: 20px 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px;">
            <h2 style="margin-top: 0; color: #153A61; font-size: 1.6em; font-family: 'Playfair Display', serif;">{title}</h2>
            <p style="color: #444; font-size: 1.05em; line-height: 1.6; margin-bottom: 0;">{text}</p>
            {admin_note}
        </div>
        """, unsafe_allow_html=True)

    # PAGE: RED GENERAL
    if page == "Red General":
        render_graph_page(researchers, relationships, hierarchical=False, theme_filters=None)

    # PAGE: ÁRBOL GENEALÓGICO
    elif page == "Genealogía (beta)":
        render_graph_page(researchers, relationships, hierarchical=True, theme_filters=None)

    # PAGE: ANÁLISIS DE RED, GÉNERO Y REGIÓN
    elif page == "Análisis de Red, Género y Región":
        st.title("Análisis de Red, Género y Región")
        st.markdown("---")
        
        # Simplified view without advanced metrics/flows
        st.subheader("📍 Distribución Regional")
        st.info("📊 Visibilidad de investigadores por provincias (vincualdos a la institución declarada).")
        
        prov_counts = []
        for r in researchers:
            if r.province:
                prov_counts.append({'Provincia': r.province, 'Nombre': r.name})
        
        if prov_counts:
            df_prov = pd.DataFrame(prov_counts)
            # Group by province and aggregate: count total and join names
            summary_prov = df_prov.groupby('Provincia').agg(
                Total=('Nombre', 'count'),
                Nombres=('Nombre', lambda x: ", ".join(sorted(list(x))))
            ).reset_index().sort_values('Total', ascending=False)
            
            # Formatting researcher names for better display in tooltips (wrap text if too long)
            def format_names(names_str):
                import textwrap
                wrapped = textwrap.fill(names_str, width=50)
                return wrapped.replace('\n', '<br>')
            
            summary_prov['Nombres_HTML'] = summary_prov['Nombres'].apply(format_names)
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                # 1. Argentina Map (using local GeoJSON)
                try:
                    with open("assets/geojson/argentina.geojson", "r") as f:
                        arg_geojson = json.load(f)
                    
                    # Ensure province names match GeoJSON (normalized comparison)
                    fig_map = px.choropleth(summary_prov, 
                                            geojson=arg_geojson, 
                                            locations='Provincia', 
                                            featureidkey="properties.NAME_1",
                                            color='Total',
                                            hover_name='Provincia',
                                            hover_data={
                                                'Total': True,
                                                'Provincia': False,
                                                'Nombres_HTML': True
                                            },
                                            color_continuous_scale="Blues",
                                            labels={'Total':'Investigadores/as', 'Nombres_HTML': 'Integrantes'},
                                            title="Mapa de Distribución (Argentina)")
                    
                    fig_map.update_geos(fitbounds="locations", visible=False)
                    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
                    st.plotly_chart(fig_map, use_container_width=True)
                except Exception as e:
                    st.error(f"Error cargando mapa: {e}")
                    fig_prov = px.bar(summary_prov, x='Provincia', y='Total', text='Total',
                                     title="Investigadores/as por Provincia",
                                     hover_data=['Nombres_HTML'],
                                     color_discrete_sequence=['#2E5C8A'])
                    st.plotly_chart(fig_prov, use_container_width=True)
                    
            with col_m2:
                fig_active = px.pie(summary_prov, names='Provincia', values='Total',
                                   title="Distribución Total por Provincia",
                                   hover_data=['Nombres_HTML'],
                                   labels={'Nombres_HTML': 'Integrantes'},
                                   hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_active, use_container_width=True)
            
            st.caption("ℹ️ La distribución se basa en la institución declarada para cada investigador/a.")
        else:
            st.warning("No hay datos geográficos cargados aún.")

        st.markdown("---")
        # Existing Gender Analysis...
        st.write("Métricas y distribución de investigadores en la red genealógica.")
        
        # Calculate statistics
        m_count = len([r for r in researchers if r.gender == "Masculino"])
        f_count = len([r for r in researchers if r.gender == "Femenino"])
        u_count = len([r for r in researchers if r.gender == "Desconocido"])
        total_count = len(researchers)
        
        # 1. Gender Distribution Pie Chart
        st.subheader("Distribución de Género General")
        labels = ['Femenino', 'Masculino', 'Desconocido']
        values = [f_count, m_count, u_count]
        colors = ['#FF6B6B', '#4ECDC4', '#C7F464']
        
        fig = px.pie(names=labels, values=values, color_discrete_sequence=colors, hole=0.4)
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Investigadores/as", total_count)
            st.metric("Mujeres", f_count)
        with col2:
            st.metric("Relaciones (Aristas)", len(relationships))
            st.metric("Hombres", m_count)
            
        st.markdown("---")
        
        # 2. Career Start per Decade by Gender
        st.subheader("Primeras Publicaciones por Década y Género")
        decades = []
        for r in researchers:
            if r.activity_start:
                # Group by decade
                decade = (r.activity_start // 10) * 10
                decades.append({'Década': decade, 'Género': r.gender})
        
        if decades:
            df = pd.DataFrame(decades)
            df_grouped = df.groupby(['Década', 'Género']).size().reset_index(name='Cantidad')
            fig_bar = px.bar(df_grouped, x='Década', y='Cantidad', color='Género', barmode='group',
                             color_discrete_map={'Femenino': '#FF6B6B', 'Masculino': '#4ECDC4', 'Desconocido': '#C7F464'})
            st.plotly_chart(fig_bar, use_container_width=True)




    elif page == "Colaboradores/as":
        st.title("Aportes y Solicitudes de Edición (Colaboración)")
        st.info("Utilice este panel para colaborar con la red. Un administrador revisará y validará su solicitud antes de integrarla a la base general.")
        
        # Internal navigation state for Collaborators
        colab_options = ["Sumar Investigador/a Nuevo/a", "Modificar Investigador/a", "Sugerir Nueva Relación / Director/a", "🧪 Corroborar Datos", "🏆 Muro de Colaboradores/as"]
        if "colab_tab_index" not in st.session_state:
            st.session_state.colab_tab_index = 0
            
        colab_tab = st.radio("Sección de Colaboración", colab_options, index=st.session_state.colab_tab_index, horizontal=True, label_visibility="collapsed")
        st.session_state.colab_tab_index = colab_options.index(colab_tab) # Sync back
        
        st.markdown("---")
        
        session = Session()
        researchers = session.query(Researcher).all()
        
        # Calculate contributors for the wall of fame
        approved_suggestions = session.query(Suggestion, User).join(User).filter(Suggestion.status == "Approved").all()
        contributors = set()
        for sug, author in approved_suggestions:
            if author.username != "admin": # Exclude the admin from the public wall
                contributors.add(author.full_name)
                
        r_map = {r.id: r.name for r in researchers}


        if colab_tab == "🧪 Corroborar Datos":
            st.subheader("🧪 Corroboración de Datos")
            st.write("Esta sección permite validar manualmente los datos cargados inicialmente. Una vez corroborados, se marcarán como tales en la base.")
            
            unverified_r = session.query(Researcher).filter(Researcher.verified == False).all()
            unverified_rel = session.query(Relationship).filter(Relationship.verified == False).all()
            
            v_col1, v_col2 = st.columns(2)
            
            with v_col1:
                st.markdown(f"**Investigadores/as a Revisar ({len(unverified_r)})**")
                for r in unverified_r:
                    with st.expander(f"👤 {r.name}"):
                        st.write(f"**Institución:** {r.institution}")
                        st.write(f"**Rol:** {r.role}")
                        st.write(f"**Keywords:** {r.keywords}")
                        col_v_r1, col_v_r2 = st.columns(2)
                        with col_v_r1:
                            if st.button(f"Corroborar {r.name}", key=f"v_r_colab_{r.id}", use_container_width=True):
                                try:
                                    robj = session.query(Researcher).get(r.id)
                                    robj.verified = True
                                    session.commit()
                                    st.success(f"{r.name} corroborado/a.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            if st.button(f"📝 Modificar", key=f"edit_r_v_colab_{r.id}", use_container_width=True):
                                st.session_state.edit_target_id = r.id
                                st.session_state.colab_tab_index = 1 # Modificar Investigador/a
                                st.rerun()
            
            with v_col2:
                st.markdown(f"**Relaciones a Revisar ({len(unverified_rel)})**")
                for rel in unverified_rel:
                    student = session.query(Researcher).get(rel.student_id)
                    director = session.query(Researcher).get(rel.director_id)
                    s_name = student.name if student else rel.student_id
                    d_name = director.name if director else rel.director_id
                    
                    with st.expander(f"🔗 {d_name} -> {s_name}"):
                        st.write(f"**Tipo de Vínculo:** {rel.type}")
                        col_v_rel1, col_v_rel2 = st.columns(2)
                        with col_v_rel1:
                            if st.button(f"Corroborar Relación {rel.id}", key=f"v_rel_colab_{rel.id}", use_container_width=True):
                                try:
                                    relobj = session.query(Relationship).get(rel.id)
                                    relobj.verified = True
                                    session.commit()
                                    st.success("Vínculo corroborado.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            if st.button(f"📝 Modificar", key=f"edit_rel_v_colab_{rel.id}", use_container_width=True):
                                st.session_state.edit_rel_dir_id = rel.director_id
                                st.session_state.edit_rel_stu_id = rel.student_id
                                st.session_state.colab_tab_index = 2 # Sugerir Nueva Relación
                                st.rerun()
                            if st.button(f"🗑️ Borrar", key=f"del_rel_v_colab_{rel.id}", use_container_width=True):
                                try:
                                    relobj = session.query(Relationship).get(rel.id)
                                    session.delete(relobj)
                                    session.commit()
                                    st.success("Relación eliminada.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
        

        elif colab_tab == "🏆 Muro de Colaboradores/as":
            st.markdown("### 🏆 Quienes sumaron datos al proyecto")
            st.write("Agradecimiento especial a las personas que han contribuido activamente al crecimiento y precisión de esta red genealógica:")
            if contributors:
                for c in sorted(list(contributors)):
                    st.markdown(f"- **{c}**")
            else:
                st.write("Aún no hay contribuciones externas validadas. ¡Sé la primera persona en aportar!")

        elif colab_tab == "Sumar Investigador/a Nuevo/a":
            st.markdown("### Sugerir Incorporación")
            with st.form("suggestion_add_form"):
                st.write("Complete los datos disponibles para sugerir un nuevo nodo principal:")
                col_a, col_b = st.columns(2)
                with col_a: 
                    new_name = st.text_input("Nombre y Apellido")
                    new_inst = st.text_input("Institución Principal")
                with col_b: 
                    new_role = st.selectbox("Rol Biográfico", ["", "Pionero/a", "Formador/a", "Investigador/a", "Becario/a"])
                    new_gender = st.selectbox("Identidad de Género", ["Desconocido", "Masculino", "Femenino", "Otro"])
                
                new_years = st.text_input("Primera y última publicación (años)", help="Formato: 1980-2024")
                col_geo1, col_geo2 = st.columns(2)
                with col_geo1: new_prov = st.text_input("Provincia (Ej: Chubut)")
                with col_geo2: new_city = st.text_input("Ciudad (Ej: Trelew)")
                
                new_keywords = st.text_input("Palabras Clave (Tópicos, P. Geológicos. Separados por comas)")
                new_scholar = st.text_input("Perfil Google Scholar (URL)")
                
                # We package this as a JSON suggestion
                if st.form_submit_button("Enviar Solicitud de Alta"):
                    if not new_name:
                        st.error("El Nombre es obligatorio para sugerir un alta.")
                    else:
                        sug_data = {
                            "type": "new_researcher",
                            "name": new_name,
                            "institution": new_inst,
                            "role": new_role,
                            "activity_years": new_years,
                            "scholar_url": new_scholar,
                            "keywords": new_keywords,
                            "gender": new_gender,
                            "province": new_prov,
                            "city": new_city
                        }
                        desc = json.dumps(sug_data)
                        # We use target_id="None" for new creations
                        add_suggestion(user.id, "Nuevo/a Investigador/a", "None", desc)
                        st.success("¡Gracias! Solicitud de alta enviada a revisión.")

        elif colab_tab == "Modificar Investigador/a":
            st.markdown("### Sugerir Correcciones a Nodos Existentes")
            # Handle pre-selection from redirect
            default_r_mod = st.session_state.get("edit_target_id", "")
            target_id = st.selectbox("Seleccione Investigador/a o Becario/a a Modificar", options=[""] + list(r_map.keys()), index=([None]+list(r_map.keys())).index(default_r_mod) if default_r_mod in r_map else 0, format_func=lambda x: r_map[x] if x else "-- Elegir Colega --")
            # Clear after use? User might want it to stay. Let's keep it for now.
            
            if target_id:
                r_to_mod = session.query(Researcher).get(target_id)
                st.write("Complete **solamente** los campos que desea corregir o actualizar. (Los datos actuales se muestran en gris).")
                
                with st.form("suggestion_mod_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_inst = st.text_input("Institución Correcta", placeholder=r_to_mod.institution or "")
                        roles = ["", "Pionero/a", "Formador/a", "Investigador/a", "Becario/a"]
                        curr_role_idx = roles.index(r_to_mod.role) if r_to_mod.role in roles else 0
                        new_role = st.selectbox("Rol Biográfico", roles, index=curr_role_idx)
                    with col2:
                        new_is_phd = st.checkbox("Actualmente en Doctorado (Marcar si cursa)", value=getattr(r_to_mod, 'is_phd_in_progress', False))
                        curr_years = f"{r_to_mod.activity_start}-{r_to_mod.activity_end}" if r_to_mod.activity_start and r_to_mod.activity_end else ""
                        new_years = st.text_input("Años de publicación (primer-último)", placeholder=curr_years)
                    new_scholar = st.text_input("Google Scholar URL", placeholder=r_to_mod.scholar_url or "")
                    new_rg = st.text_input("ResearchGate URL", placeholder=r_to_mod.researchgate_url or "")
                    new_orcid = st.text_input("ORCID URL", placeholder=getattr(r_to_mod, 'orcid_url', "") or "")
                    new_keywords = st.text_input("Palabras Clave (sep. por comas)", placeholder=r_to_mod.keywords or "")
                    
                    genders = ["", "Desconocido", "Masculino", "Femenino", "Otro"]
                    curr_gen_idx = genders.index(r_to_mod.gender) if r_to_mod.gender in genders else 0
                    new_gender = st.selectbox("Género", genders, index=curr_gen_idx)
                    
                    col_geo1, col_geo2 = st.columns(2)
                    with col_geo1: new_prov = st.text_input("Provincia", placeholder=r_to_mod.province or "")
                    with col_geo2: new_city = st.text_input("Ciudad", placeholder=r_to_mod.city or "")
                    
                    if st.form_submit_button("Enviar Propuesta de Corrección"):
                        sug_data = {"type": "modification", "id": target_id, "changes": {}}
                        if new_inst: sug_data["changes"]["institution"] = new_inst
                        if new_role and new_role != r_to_mod.role: sug_data["changes"]["role"] = new_role
                        if new_is_phd != getattr(r_to_mod, 'is_phd_in_progress', False): sug_data["changes"]["is_phd_in_progress"] = new_is_phd
                        if new_years: sug_data["changes"]["activity_years"] = new_years
                        if new_scholar: sug_data["changes"]["scholar_url"] = new_scholar
                        if new_rg: sug_data["changes"]["researchgate_url"] = new_rg
                        if new_orcid: sug_data["changes"]["orcid_url"] = new_orcid
                        if new_keywords: sug_data["changes"]["keywords"] = new_keywords
                        if new_gender and new_gender != r_to_mod.gender: sug_data["changes"]["gender"] = new_gender
                        if new_prov: sug_data["changes"]["province"] = new_prov
                        if new_city: sug_data["changes"]["city"] = new_city
                        
                        if not sug_data["changes"]:
                            st.warning("No se detectaron cambios para enviar.")
                        else:
                            desc = json.dumps(sug_data)
                            add_suggestion(user.id, "Modificar Investigador/a", target_id, desc)
                            st.success("Corrección enviada para revisión analítica.")

        elif colab_tab == "Sugerir Nueva Relación / Director/a":
            st.markdown("### Reportar Errores o Nuevas Relaciones")
            st.info("Para sugerir una nueva relación, use los desplegables. Para otros errores, use el campo de texto inferior.")
            
            with st.form("suggestion_rel_form"):
                col_rel1, col_rel2 = st.columns(2)
                with col_rel1:
                    default_dir = st.session_state.get("edit_rel_dir_id", "")
                    d_id = st.selectbox("Director/a", options=[""] + list(r_map.keys()), index=([None]+list(r_map.keys())).index(default_dir) if default_dir in r_map else 0, format_func=lambda x: r_map[x] if x else "-- Seleccionar --")
                with col_rel2:
                    default_stu = st.session_state.get("edit_rel_student_id", st.session_state.get("edit_rel_stu_id", ""))
                    s_id = st.selectbox("Dirigido/a", options=[""] + list(r_map.keys()), index=([None]+list(r_map.keys())).index(default_stu) if default_stu in r_map else 0, format_func=lambda x: r_map[x] if x else "-- Seleccionar --")
                
                type_rel = st.selectbox("Tipo de Vínculo", ["Primary", "Secondary", "Postdoc", "Co-Postdoc"])
                
                other_desc = st.text_area("Otros Detalles / Informe de Error", placeholder="Ej: Juan Pérez fue co-dirigido por Ana Gómez en el año 2005 para su tesis doctoral en la UBA...")
                
                if st.form_submit_button("Enviar Sugerencia / Reporte"):
                    if d_id and s_id:
                        if d_id == s_id:
                            st.error("Un/a investigador/a no puede dirigirse a sí mismo/a.")
                        else:
                            sug_data = {
                                "type": "new_relationship",
                                "director_id": d_id,
                                "student_id": s_id,
                                "rel_type": type_rel,
                                "notes": other_desc
                            }
                            desc = json.dumps(sug_data)
                            add_suggestion(user.id, "Nueva Relación", f"{d_id}->{s_id}", desc)
                            st.success("¡Gracias! Propuesta de vínculo enviada a revisión.")
                    elif other_desc.strip():
                        add_suggestion(user.id, "Informar Error / Relación", "None", other_desc)
                        st.success("Reporte enviado con éxito.")
                    else:
                        st.error("Debe seleccionar ambos investigadores o completar el campo de descripción.")
        
        session.close()


    # PAGE: ADMINISTRACIÓN (Master Admin View)
    elif page == "Administración":
        st.title("Panel de Administración y Control")
        st.info("Acceso restringido. Por favor certifique sus credenciales de alto nivel.")
        
        # Local auth for this specific super-admin tab
        col_cred1, col_cred2 = st.columns(2)
        with col_cred1: admin_user = st.text_input("Usuario Administrador", key="admin_u")
        with col_cred2: admin_pass = st.text_input("Contraseña", type="password", key="admin_p")
        
        if admin_user == "admin" and admin_pass == "admin123":
            st.success("Credenciales Administrativas Verificadas.")
            st.markdown("---")
            
            # Handle tab pre-selection from session state
            dt_idx = st.session_state.get("admin_tab_index", 0)
            
            tab_panel, tab_gestion, tab_monitor, tab_db, tab_backup, tab_audit = st.tabs(["Validar Sugerencias", "Gestión Directa", "📊 Monitoreo de Datos", "Explorador de Tablas", "📦 Copia de Seguridad", "Auditoría Total"])
            
            # Reset the index after use to avoid sticky navigation
            if st.session_state.get("admin_tab_index") == 1:
                st.warning("👈 Seleccione la solapa **'Gestión Directa'** para editar el registro seleccionado.")
            
            st.session_state.admin_tab_index = 0

            with tab_panel:
                st.subheader("Sugerencias de Colaboradores/as Pendientes")
                
                session = Session()
                suggestions = session.query(Suggestion, User).join(User).filter(Suggestion.status == "Pending").all()
                
                if not suggestions:
                    st.write("No hay sugerencias pendientes en este momento.")
                
                for sug, author in suggestions:
                    with st.expander(f"Sugerencia de {author.full_name} ({sug.timestamp.strftime('%Y-%m-%d %H:%M')})"):
                        st.write(f"**Tipo:** {sug.target_type}")
                        
                        is_auto_applicable = False
                        try:
                            sug_json = json.loads(sug.suggested_changes)
                            if isinstance(sug_json, dict) and sug_json.get("type") == "modification":
                                is_auto_applicable = True
                                st.write("**Nuevos Datos Propuestos:**")
                                st.json(sug_json["changes"])
                            elif isinstance(sug_json, dict) and sug_json.get("type") == "new_researcher":
                                is_auto_applicable = True 
                                st.write("**Sugerencia de Nuevo/a Nodo/a:**")
                                st.json(sug_json)
                            elif isinstance(sug_json, dict) and sug_json.get("type") == "new_relationship":
                                is_auto_applicable = True
                                st.write("**Propuesta de Nueva Relación:**")
                                st.json(sug_json)
                            else:
                                st.write(f"**Detalle:** {sug.suggested_changes}")
                        except:
                            st.write(f"**Detalle:** {sug.suggested_changes}")
                        
                        if sug.target_id and sug.target_id != "None":
                            st.write(f"**ID Objetivo:** {sug.target_id}")
                            if st.button(f"📝 Ir a Modificar {sug.target_id}", key=f"edit_sug_{sug.id}"):
                                st.session_state.edit_target_id = sug.target_id
                                st.session_state.page_redirect = "Administración"
                                st.rerun()
                        
                        col_approve, col_reject = st.columns(2)
                        with col_approve:
                            btn_label = "Aprobar e Inyectar" if is_auto_applicable else "Aprobar / Marcar Manualmente Resuelto"
                            if st.button(btn_label, key=f"app_{sug.id}"):
                                if is_auto_applicable:
                                    r_to_mod = session.query(Researcher).filter(Researcher.id == sug.target_id).first()
                                    if r_to_mod:
                                        changes = sug_json["changes"]
                                        if changes.get("institution"): r_to_mod.institution = changes["institution"]
                                        if changes.get("role"): r_to_mod.role = changes["role"]
                                        if "is_phd_in_progress" in changes: r_to_mod.is_phd_in_progress = changes["is_phd_in_progress"]
                                        
                                        years = changes.get("activity_years")
                                        if years and "-" in years:
                                            try:
                                                start, end = years.split("-")
                                                r_to_mod.activity_start = int(start.strip())
                                                r_to_mod.activity_end = int(end.strip())
                                            except: pass
                                        
                                        if changes.get("scholar_url"): r_to_mod.scholar_url = changes["scholar_url"]
                                        if changes.get("researchgate_url"): r_to_mod.researchgate_url = changes["researchgate_url"]
                                        if changes.get("orcid_url"): r_to_mod.orcid_url = changes["orcid_url"]
                                        if changes.get("keywords"): r_to_mod.keywords = changes["keywords"]
                                        if changes.get("gender"): r_to_mod.gender = changes["gender"]
                                        if changes.get("province"): r_to_mod.province = changes["province"]
                                        if changes.get("city"): r_to_mod.city = changes["city"]
                                        
                                        st.success("Cambios inyectados automáticamente en la matriz de datos.")
                                    else:
                                        st.error("No se pudo encontrar al/la investigador/a para modificar.")
                                elif is_auto_applicable and sug_json.get("type") == "new_relationship":
                                    d_id = sug_json["director_id"]
                                    s_id = sug_json["student_id"]
                                    r_type = sug_json["rel_type"]
                                    
                                    existing = session.query(Relationship).filter_by(student_id=s_id, director_id=d_id).first()
                                    if not existing:
                                        new_rel = Relationship(student_id=s_id, director_id=d_id, type=r_type)
                                        session.add(new_rel)
                                        st.success(f"Relación {r_type} inyectada exitosamente.")
                                    else:
                                        st.warning("Esta relación ya existe.")
                                elif is_auto_applicable and sug_json.get("type") == "new_researcher":
                                    # Basic logic to create new researcher from suggestion
                                    new_id = sug_json["name"].lower().replace(" ", "_")
                                    if session.query(Researcher).get(new_id):
                                        new_id = f"{new_id}_{int(datetime.now().timestamp())}"
                                    
                                    new_r = Researcher(
                                        id=new_id,
                                        name=sug_json["name"],
                                        institution=sug_json.get("institution"),
                                        role=sug_json.get("role"),
                                        gender=sug_json.get("gender", "Desconocido"),
                                        province=sug_json.get("province"),
                                        city=sug_json.get("city"),
                                        keywords=sug_json.get("keywords"),
                                        scholar_url=sug_json.get("scholar_url"),
                                        created_by=author.id
                                    )
                                    session.add(new_r)
                                    st.success(f"Nuevo/a investigador/a {sug_json['name']} inyectado/a exitosamente.")
                                
                                sug.status = "Approved"
                                session.commit()
                                st.success("Sugerencia marcada como Aprobada en el Muro.")
                                st.rerun()
                        with col_reject:
                            if st.button("Desestimar", key=f"rej_{sug.id}"):
                                sug.status = "Rejected"
                                session.commit()
                                st.warning("Sugerencia rechazada.")
                                st.rerun()
                session.close()

                st.divider()
                st.subheader("Respaldo Integral")
                if os.path.exists("genealogy.db"):
                    with open("genealogy.db", "rb") as f:
                        st.download_button(
                            label="📥 Descargar SQLite (Backup Diario)",
                            data=f,
                            file_name=f"genealogy_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                            mime="application/octet-stream",
                            help="Asegure copias locales de la base."
                        )

            with tab_gestion:
                st.subheader("Gestión Directa")
                st.warning("⚠️ Ediciones de bajo nivel. Impacto inmediato.")
                
                sub_add, sub_edit, sub_rel = st.tabs(["Forzar Alta Investigador", "Forzar Edición", "Forzar Enlace Formal"])
                
                with sub_add:
                    with st.form("add_researcher"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            r_name = st.text_input("Nombre"); r_id = st.text_input("ID (snake_case)").strip()
                        with col_b:
                            r_inst = st.text_input("Institución"); r_role = st.selectbox("Rol", ["Investigador/a", "Formador/a", "Pionero/a", "Becario/a"])
                            r_phd = st.checkbox("Doctorado en Curso")
                        r_notes = st.text_area("Notas")
                        col_c, col_d, col_gndr = st.columns(3)
                        with col_c: act_start = st.number_input("Año Inicio", 1850, 2030, 2000)
                        with col_d: act_end = st.number_input("Año Fin", 1850, 2030, 2020)
                        with col_gndr: r_gender = st.selectbox("Género", ["Desconocido", "Masculino", "Femenino", "Otro"])
                        
                        col_geo1, col_geo2 = st.columns(2)
                        with col_geo1: r_prov = st.text_input("Provincia")
                        with col_geo2: r_city = st.text_input("Ciudad")
                        
                        col_e, col_f, col_g = st.columns(3)
                        with col_e: r_scholar = st.text_input("Scholar URL")
                        with col_f: r_rg = st.text_input("ResearchGate URL")
                        with col_g: r_orcid = st.text_input("ORCID URL")
                        
                        r_keywords = st.text_input("Palabras Clave")

                        if st.form_submit_button("Inyectar a la DB"):
                            session = Session()
                            if session.query(Researcher).filter_by(id=r_id).first(): st.error("Ese ID ya pertenece a la red.")
                            else:
                                new_r = Researcher(
                                    id=r_id, name=r_name, institution=r_inst, role=r_role, 
                                    notes=r_notes, activity_start=act_start, activity_end=act_end, 
                                    is_phd_in_progress=r_phd, photo_url=None,
                                     scholar_url=r_scholar, researchgate_url=r_rg, orcid_url=r_orcid,
                                     keywords=r_keywords, gender=r_gender,
                                     province=r_prov, city=r_city,
                                     created_by=user.id, last_edited_by=user.id)
                                session.add(new_r); session.commit()
                                add_audit_log(user.id, "CREATE MANUAL", "Researcher/a", r_id, f"Injected {r_name}")
                                st.success("Peritaje concluido. Nodo/a añadido/a.")
                            session.close()

                with sub_edit:
                    session = Session()
                    all_r = session.query(Researcher).all()
                    session.close()
                    r_selector = {r.id: r.name for r in all_r}
                    
                    # Pre-selection logic
                    default_idx_edit = 0
                    st_id = st.session_state.get('edit_target_id')
                    if st_id and st_id in r_selector:
                        default_idx_edit = list(r_selector.keys()).index(st_id)
                    
                    target_edit_id = st.selectbox("Apuntar Investigador/a", list(r_selector.keys()), index=default_idx_edit, format_func=lambda x: r_selector[x])
                    
                    if target_edit_id:
                        session = Session()
                        r_to_edit = session.query(Researcher).get(target_edit_id)
                        session.close()
                        
                        with st.form("edit_researcher_form"):
                            e_name = st.text_input("Nombre", value=r_to_edit.name)
                            col1, col2 = st.columns(2)
                            with col1:
                                e_inst = st.text_input("Institución", value=r_to_edit.institution or "")
                                e_role = st.selectbox("Rol", ["Investigador/a", "Formador/a", "Pionero/a", "Becario/a"], index=["Investigador/a", "Formador/a", "Pionero/a", "Becario/a"].index(r_to_edit.role) if r_to_edit.role in ["Investigador/a", "Formador/a", "Pionero/a", "Becario/a"] else 0)
                            with col2:
                                e_phd = st.checkbox("Doctorado en curso", value=getattr(r_to_edit, 'is_phd_in_progress', False))
                                e_photo = st.text_input("Photo URL", value=r_to_edit.photo_url or "")
                            
                            col3, col4, col5 = st.columns(3)
                            with col3: e_start = st.number_input("Año Inicio", 1850, 2030, r_to_edit.activity_start or 2000)
                            with col4: e_end = st.number_input("Año Fin", 1850, 2030, r_to_edit.activity_end or 2020)
                            with col5: e_gender = st.selectbox("Género", ["Desconocido", "Masculino", "Femenino", "Otro"], index=["Desconocido", "Masculino", "Femenino", "Otro"].index(r_to_edit.gender) if r_to_edit.gender in ["Desconocido", "Masculino", "Femenino", "Otro"] else 0)
                            
                            col_geo_e1, col_geo_e2 = st.columns(2)
                            with col_geo_e1: e_prov = st.text_input("Provincia", value=r_to_edit.province or "")
                            with col_geo_e2: e_city = st.text_input("Ciudad", value=r_to_edit.city or "")
                            
                            e_scholar = st.text_input("Scholar URL", value=r_to_edit.scholar_url or "")
                            e_rg = st.text_input("ResearchGate URL", value=r_to_edit.researchgate_url or "")
                            e_orcid = st.text_input("ORCID URL", value=(r_to_edit.orcid_url if hasattr(r_to_edit, 'orcid_url') else "") or "")
                            e_keywords = st.text_input("Palabras Clave", value=r_to_edit.keywords or "")
                            e_notes = st.text_area("Notas Privadas (Admin)", value=r_to_edit.notes or "")
                            
                            if st.form_submit_button("Sobrescribir Registro"):
                                session = Session()
                                r_to_upd = session.query(Researcher).get(target_edit_id)
                                r_to_upd.name = e_name; r_to_upd.institution = e_inst; r_to_upd.role = e_role
                                r_to_upd.is_phd_in_progress = e_phd; r_to_upd.photo_url = e_photo
                                r_to_upd.activity_start = e_start; r_to_upd.activity_end = e_end
                                r_to_upd.scholar_url = e_scholar; r_to_upd.researchgate_url = e_rg
                                if hasattr(r_to_upd, 'orcid_url'): r_to_upd.orcid_url = e_orcid
                                r_to_upd.keywords = e_keywords
                                r_to_upd.gender = e_gender
                                r_to_upd.province = e_prov
                                r_to_upd.city = e_city
                                r_to_upd.notes = e_notes; r_to_upd.last_edited_by = user.id
                                session.commit(); session.close()
                                add_audit_log(user.id, "UPDATE MANUAL", "Researcher", target_edit_id, f"Overwrote {e_name}")
                                st.success("Alteración Estructural Completada.")
                                st.rerun()

                with sub_rel:
                    session = Session()
                    researchers = session.query(Researcher).all()
                    session.close()
                    r_opts = {r.id: f"{r.name} ({r.id})" for r in researchers}
                    
                    # Pre-selection logic for relations
                    def_stu_idx = 0
                    def_dir_idx = 0
                    st_stu = st.session_state.get('edit_rel_stu_id')
                    st_dir = st.session_state.get('edit_rel_dir_id')
                    if st_stu and st_stu in r_opts: def_stu_idx = list(r_opts.keys()).index(st_stu)
                    if st_dir and st_dir in r_opts: def_dir_idx = list(r_opts.keys()).index(st_dir)

                    with st.form("mk_rel_admin"):
                        s_id = st.selectbox("Dirigido/a", list(r_opts.keys()), index=def_stu_idx, format_func=lambda x: r_opts[x])
                        d_id = st.selectbox("Director/a", list(r_opts.keys()), index=def_dir_idx, format_func=lambda x: r_opts[x])
                        type_rel = st.radio("Jerarquía de la Relación", ["Primary", "Secondary", "Postdoc", "Co-Postdoc"])
                        if st.form_submit_button("Soldar Linaje"):
                            session = Session()
                            if session.query(Relationship).filter_by(student_id=s_id, director_id=d_id).first(): st.warning("Ese vector ya existe.")
                            else:
                                rel = Relationship(student_id=s_id, director_id=d_id, type=type_rel)
                                session.add(rel); session.commit()
                                add_audit_log(user.id, "CREATE MANUAL", "Rel", f"{d_id}->{s_id}", type_rel)
                                st.success("Linaje consolidado.")
                            session.close()

            with tab_monitor:
                st.subheader("Estado de la Carga y Actividad")
                session = Session()
                
                # Fetch data for charts
                researchers_df = pd.read_sql(session.query(Researcher).statement, session.bind)
                relationships_df = pd.read_sql(session.query(Relationship).statement, session.bind)
                audit_df = pd.read_sql(session.query(AuditLog).statement, session.bind)
                
                # Ensure timestamp is datetime (Robust Conversion)
                if not audit_df.empty:
                    audit_df['timestamp'] = pd.to_datetime(audit_df['timestamp'], errors='coerce')
                
                
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    # Researcher growth
                    # Ensure timestamp is truly datetime for the sub-selection
                    audit_res = audit_df[audit_df['target_type'] == 'Researcher'].copy()
                    if not audit_res.empty:
                        audit_res['timestamp'] = pd.to_datetime(audit_res['timestamp'], errors='coerce')
                        audit_res = audit_res.dropna(subset=['timestamp'])
                        
                        researcher_counts = audit_res['timestamp'].dt.date.value_counts().sort_index().cumsum()
                        if not researcher_counts.empty:
                            fig_res = px.line(x=researcher_counts.index, y=researcher_counts.values, 
                                            title="Evolución de Investigadores (Nodos)", 
                                            labels={'x': 'Fecha', 'y': 'Total Nodos'})
                            st.plotly_chart(fig_res, use_container_width=True)
                        else:
                            st.info("No hay datos cronológicos de investigadores.")
                    else:
                        st.info("Aún no hay registros de nuevos investigadores.")

                with col_m2:
                    # Action distribution
                    action_dist = audit_df['action'].value_counts()
                    fig_actions = px.pie(names=action_dist.index, values=action_dist.values, title="Distribución de Acciones")
                    st.plotly_chart(fig_actions, use_container_width=True)
                
                # Edits and Corrections over time
                st.write("**Historial de Ediciones y Correcciones**")
                if not audit_df.empty and 'timestamp' in audit_df.columns:
                    # Filter out invalid timestamps for grouping
                    audit_plot = audit_df.dropna(subset=['timestamp']).copy()
                    if not audit_plot.empty:
                        audit_plot['Fecha'] = audit_plot['timestamp'].dt.date
                        daily_actions = audit_plot.groupby(['Fecha', 'action']).size().unstack(fill_value=0)
                        if not daily_actions.empty:
                            fig_daily = px.bar(daily_actions, title="Actividad Diaria por Tipo de Acción")
                            st.plotly_chart(fig_daily, use_container_width=True)
                        else:
                            st.info("Sin actividad diaria registrada.")
                    else:
                        st.info("Sin datos temporales válidos.")
                else:
                    st.info("Sin datos de auditoría.")
                
                # Overall Stats
                st.divider()
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                stat_col1.metric("Total Investigadores/as", len(researchers_df))
                stat_col2.metric("Total Relaciones", len(relationships_df))
                stat_col3.metric("Ediciones Realizadas", len(audit_df[audit_df['action'].str.contains('UPDATE', na=False)]))
                stat_col4.metric("Sugerencias Totales", session.query(Suggestion).count())
                
                session.close()

            with tab_db:
                st.subheader("Base de Datos General")
                st.caption("Apertura en modo lectura de las tablas subyacentes.")
                session = Session()
                sub_res, sub_rel, sub_usr = st.tabs(["Nodos", "Aristas (Relaciones)", "Usuarios Registrados"])
                with sub_res:
                    data_res = pd.read_sql(session.query(Researcher).statement, session.bind)
                    st.dataframe(data_res, use_container_width=True)
                with sub_rel:
                    data_rel = pd.read_sql(session.query(Relationship).statement, session.bind)
                    st.dataframe(data_rel, use_container_width=True)
                with sub_usr:
                    data_usr = pd.read_sql(session.query(User).statement, session.bind)
                    st.dataframe(data_usr, use_container_width=True)
                session.close()

            with tab_backup:
                st.subheader("📦 Gestión de Versiones y Backups")
                st.write("Esta herramienta permite crear una copia de seguridad 'congelada' de la red actual, incluyendo la base de datos y los recursos visuales.")
                
                col_back1, col_back2 = st.columns([2, 1])
                
                with col_back1:
                    backup_note = st.text_input("Nota de la versión", placeholder="Ej: Antes de la reunión SAPP 2026")
                    if st.button("🚀 Archivar Versión Actual", use_container_width=True):
                        try:
                            from archive_version import archive_version
                            success, result = archive_version(backup_note)
                            if success:
                                st.success(f"Archivo creado exitosamente: {os.path.basename(result)}")
                                add_audit_log(user.id, "ARCHIVE", "System", "Archive", f"Manual backup: {backup_note}")
                            else:
                                st.error(f"Error al archivar: {result}")
                        except Exception as e:
                            st.error(f"Error crítico: {e}")
                
                with col_back2:
                    st.markdown("**Versiones Existentes**")
                    version_path = "versions"
                    if os.path.exists(version_path):
                        v_files = sorted([f for f in os.listdir(version_path) if f.endswith('.zip')], reverse=True)
                        if v_files:
                            for vf in v_files:
                                st.caption(f"📄 {vf}")
                        else:
                            st.write("No hay archivos guardados.")
                    else:
                        st.write("Carpeta de versiones no detectada.")

            with tab_audit:
                st.subheader("Registro Central de Inserciones y Cambios")
                session = Session()
                logs = session.query(AuditLog, User).join(User).order_by(AuditLog.timestamp.desc()).limit(200).all()
                session.close()
                data_aud = [{"Fecha (UTC)": l.timestamp, "Gestor": u.username, "Clase de Acción": l.action, "Foco / Entidad": l.target_id, "Detalle Quirúrgico": l.details} for l, u in logs]
                st.dataframe(pd.DataFrame(data_aud), use_container_width=True)
                
        elif admin_user or admin_pass:
            st.error("Credenciales insuficientes.")






if __name__ == "__main__":
    if st.session_state.user: main_app()
    else: auth_page()
