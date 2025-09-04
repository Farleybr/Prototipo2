import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# -----------------------------
# Configuración y estilos CSS
# -----------------------------
st.set_page_config(page_title=" [ TU Marca ]", page_icon="🛍️", layout="wide")

st.markdown(
    """
    <style>
    .big-title { font-size:30px; font-weight:700; margin-bottom: 15px;}
    .option-title { font-size:20px; font-weight:600; margin-bottom:10px; }
    .price-box {
        background: linear-gradient(90deg,#0ea5e9,#7c3aed);
        color: white;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
    }
    .price-amount { font-size:28px; font-weight:800; }
    .swatch { border-radius:10px; height:64px; width:100%; display:block; margin-bottom:8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1em;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] button > div {
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Datos / Catálogo / Precios
# -----------------------------
COLORES = {
    "Blanco": (255, 255, 255), "Negro": (30, 30, 30), "Azul Marino": (20, 50, 160),
    "Rojo": (200, 35, 35), "Verde Oliva": (40, 140, 75), "Gris Claro": (200, 200, 200),
    "Púrpura": (128, 0, 128)
}
MATERIALES = {
    "Algodón Básico": 1.0, "Algodón Premium": 1.25, "Poliéster Deportivo": 0.95, "Seda Ligera": 1.6
}
EXTRAS = {
    "Sin estampado": 0, "Estampado básico": 7, "Estampado premium": 15, "Bordado (Iniciales)": 6
}
TALLAS = ["XS", "S", "M", "L", "XL", "XXL"]
BASE_PRICE = 30.0

# -----------------------------
# Inicializar session_state
# -----------------------------
defaults = {
    "color_name": "Blanco", "material": list(MATERIALES.keys())[0], "extra": "Sin estampado",
    "iniciales": "", "talla": "M", "cantidad": 1, "cart": [], "price": BASE_PRICE,
    "iniciales_pos": "Centro del Pecho", "payment_success": False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Funciones auxiliares
# -----------------------------
def calcular_precio():
    base = BASE_PRICE * MATERIALES.get(st.session_state.material, 1.0)
    base += EXTRAS.get(st.session_state.extra, 0)
    if st.session_state.iniciales and st.session_state.extra != "Bordado (Iniciales)":
        base += 4.5
    if st.session_state.talla in ["XL", "XXL"]:
        base += 3.0
    st.session_state.price = round(base * max(1, st.session_state.cantidad), 2)

def text_color_for_bg(rgb):
    return (255, 255, 255) if (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) < 140 else (0, 0, 0)

def render_tshirt(color_rgb, iniciales="", extra="", pos_iniciales="Centro del Pecho"):
    W, H = 400, 500
    base_path = "assets/tshirt_base.png"
    if os.path.exists(base_path):
        base_tshirt = Image.open(base_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    else:
        base_tshirt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_tshirt)
        draw.polygon([(W*0.1, H*0.2), (W*0.25, H*0.1), (W*0.75, H*0.1), (W*0.9, H*0.2), (W*0.9, H*0.8), (W*0.7, H*0.9), (W*0.3, H*0.9), (W*0.1, H*0.8)], fill=(150, 150, 150, 255))
        draw.polygon([(W*0.05, H*0.25), (W*0.15, H*0.2), (W*0.15, H*0.5), (W*0.05, H*0.55)], fill=(150, 150, 150, 255))
        draw.polygon([(W*0.95, H*0.25), (W*0.85, H*0.2), (W*0.85, H*0.5), (W*0.95, H*0.55)], fill=(150, 150, 150, 255))

    colored_layer = Image.new("RGBA", base_tshirt.size, color_rgb)
    colored_tshirt = Image.composite(colored_layer, Image.new("RGBA", base_tshirt.size, (0,0,0,0)), base_tshirt)
    
    relief_layer = base_tshirt.copy()
    alpha = relief_layer.getchannel('A').point(lambda i: i * 0.5)
    relief_layer.putalpha(alpha)
    colored_tshirt = Image.alpha_composite(colored_tshirt, relief_layer)
    
    draw = ImageDraw.Draw(colored_tshirt)
    if extra == "Estampado básico":
        draw.ellipse([W*0.38, H*0.38, W*0.62, H*0.52], fill=(255,215,0,200), outline=(0,0,0,180), width=2)
    elif extra == "Estampado premium":
        draw.rectangle([W*0.35, H*0.35, W*0.65, H*0.55], fill=(255,50,50,200), outline=(0,0,0,180), width=2)
    
    txt_layer = Image.new("RGBA", colored_tshirt.size, (255, 255, 255, 0))
    draw_txt = ImageDraw.Draw(txt_layer)
    if iniciales:
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        text_bbox = draw_txt.textbbox((0,0), iniciales, font=font)
        text_w, text_h = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        initials_color = text_color_for_bg(color_rgb)
        
        rotation_angle = 0
        if pos_iniciales == "Centro del Pecho":
            text_x, text_y = (W - text_w) // 2, int(H * 0.4)
        elif pos_iniciales == "Bolsillo (Izquierdo)":
            text_x, text_y = int(W * 0.28 - text_w / 2), int(H * 0.25)
        elif pos_iniciales == "Manga (Derecha)":
            text_x, text_y = int(W * 0.72), int(H * 0.26)
            rotation_angle = -15
        elif pos_iniciales == "Inferior (Izquierda)":
            text_x, text_y = int(W * 0.22), int(H * 0.8)
        
        draw_txt.text((text_x, text_y), iniciales, font=font, fill=initials_color)
        
        if rotation_angle != 0:
            txt_layer = txt_layer.rotate(rotation_angle, expand=0, center=(text_x + text_w/2, text_y + text_h/2), resample=Image.BICUBIC)

    colored_tshirt = Image.alpha_composite(colored_tshirt, txt_layer)
    return colored_tshirt

def update_color_callback(color_name):
    st.session_state.color_name = color_name
    calcular_precio()

# -----------------------------
# Layout principal
# -----------------------------
st.markdown('<div class="big-title">[ TU Marca ]</div>', unsafe_allow_html=True)
st.write("Diseña productos en tiempo real. La camiseta permanece visible mientras eliges opciones.")

col_preview, col_controls = st.columns([1.4, 2.6])

with col_preview:
    st.subheader("Vista previa")
    preview_img = render_tshirt(
        COLORES.get(st.session_state.color_name),
        st.session_state.iniciales,
        st.session_state.extra,
        st.session_state.iniciales_pos
    )
    # **CORRECCIÓN AQUÍ:** Se usa use_container_width en lugar de use_column_width
    st.image(preview_img, use_container_width=True, caption=f"Camiseta: {st.session_state.color_name} • {st.session_state.material} • {st.session_state.talla}")

with col_controls:
    calcular_precio()
    price_html = f"""
        <div class="price-box">
            <div style="opacity:0.9">PRECIO ACTUAL</div>
            <div class="price-amount">${st.session_state.price:.2f}</div>
            <div style="opacity:0.9; font-size:12px">Total por {st.session_state.cantidad} unidad(es)</div>
        </div>
    """
    st.markdown(price_html, unsafe_allow_html=True)
    st.write("")

    tabs = st.tabs(["**Color**", "**Material**", "**Talla**", "**Iniciales**", "**Extras**", "**Pago**"])

    with tabs[0]:
        cols = st.columns(4)
        for i, (name, rgb) in enumerate(COLORES.items()):
            c = cols[i % 4]
            hexcolor = "#{:02x}{:02x}{:02x}".format(*rgb)
            border = "border: 1px solid #ddd;" if name == "Blanco" else ""
            c.markdown(f"<div class='swatch' style='background:{hexcolor}; {border}'></div>", unsafe_allow_html=True)
            c.button(f"Seleccionar {name}", key=f"btn_{name}", on_click=update_color_callback, args=(name,))

    with tabs[1]:
        st.selectbox("Material disponible", list(MATERIALES.keys()), key="material", on_change=calcular_precio)
    with tabs[2]:
        st.radio("Talla", TALLAS, key="talla", on_change=calcular_precio, horizontal=True)
    with tabs[3]:
        st.text_input("Iniciales (máx. 3)", key="iniciales", max_chars=3, on_change=calcular_precio)
        st.radio(
            "Posición de las iniciales",
            ["Centro del Pecho", "Bolsillo (Izquierdo)", "Manga (Derecha)", "Inferior (Izquierda)"],
            key="iniciales_pos",
            horizontal=True
        )
    with tabs[4]:
        st.radio("Selecciona un extra", list(EXTRAS.keys()), key="extra", on_change=calcular_precio)
    with tabs[5]:
        st.number_input("Cantidad", min_value=1, max_value=50, key="cantidad", step=1, on_change=calcular_precio)
        st.markdown("---")
        if st.button("Agregar al carrito", use_container_width=True):
            item = {k: st.session_state[k] for k in ["color_name", "material", "talla", "iniciales", "extra", "cantidad", "iniciales_pos"]}
            item["precio_total"] = st.session_state.price
            st.session_state.cart.append(item)
            st.success("Producto añadido al carrito")
            st.session_state.payment_success = False

# -----------------------------
# Sección de carrito inferior
# -----------------------------
st.markdown("---")
st.header("Carrito de compra")

if st.session_state.payment_success:
    st.success("¡Pago simulado exitoso! Gracias por tu compra.")
    if st.button("Crear un nuevo pedido"):
        st.session_state.payment_success = False
        st.rerun()
elif st.session_state.cart:
    items_to_delete = []
    for idx, it in enumerate(st.session_state.cart):
        col1, col2 = st.columns([4, 1])
        desc = (f"{it['cantidad']}x Camiseta {it['color_name']} / {it['material']} / Talla {it['talla']}"
                f"{' / ' + it['iniciales'] + ' (' + it['iniciales_pos'] + ')' if it['iniciales'] else ''}"
                f"{' / ' + it['extra'] if it['extra'] != 'Sin estampado' else ''}")
        col1.write(f"**{idx + 1}** • {desc} — **${it['precio_total']:.2f}**")
        if col2.button("Eliminar", key=f"del_{idx}", use_container_width=True):
            items_to_delete.append(idx)
    
    if items_to_delete:
        for index in sorted(items_to_delete, reverse=True):
            st.session_state.cart.pop(index)
        st.rerun()

    total_order = sum(i['precio_total'] for i in st.session_state.cart)
    st.markdown(f"### **Total del pedido: ${total_order:.2f}**")
    if st.button("Proceder al pago (simulado)"):
        st.session_state.payment_success = True
        st.session_state.cart = []
        st.rerun()
else:

    st.info("No hay productos en el carrito aún.")




