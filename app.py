import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import zipfile
from datetime import datetime
import base64

st.set_page_config(page_title="Professional Watermark Studio", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎨 Professional Watermark Studio</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Add stunning watermarks to your images with advanced customization</p>', unsafe_allow_html=True)

# Initialize session state
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []
if 'watermark_preview' not in st.session_state:
    st.session_state.watermark_preview = None

# Sidebar for watermark settings
with st.sidebar:
    st.header("🖼️ Watermark Configuration")
    
    # Watermark Image Upload
    st.subheader("1️⃣ Upload Watermark")
    watermark_image = st.file_uploader(
        "Choose your watermark/logo (PNG with transparency recommended)", 
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="PNG files with transparency work best for professional results"
    )
    
    if watermark_image:
        wm_preview = Image.open(watermark_image)
        st.image(wm_preview, caption="Your Watermark", use_container_width=True)
        
        st.divider()
        
        # Size & Scale Settings
        st.subheader("2️⃣ Size & Positioning")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            scale_mode = st.selectbox("Scaling Mode", [
                "Percentage of Image",
                "Fixed Width (px)",
                "Fixed Height (px)",
                "Custom Size"
            ])
        
        if scale_mode == "Percentage of Image":
            wm_scale = st.slider("Watermark Size (%)", 5, 100, 25, 1,
                               help="Size relative to the main image width")
        elif scale_mode == "Fixed Width (px)":
            wm_fixed_width = st.number_input("Width (pixels)", 50, 2000, 300, 10)
            wm_scale = None
        elif scale_mode == "Fixed Height (px)":
            wm_fixed_height = st.number_input("Height (pixels)", 50, 2000, 300, 10)
            wm_scale = None
        else:
            col_w, col_h = st.columns(2)
            with col_w:
                wm_custom_width = st.number_input("Width (px)", 50, 2000, 300, 10)
            with col_h:
                wm_custom_height = st.number_input("Height (px)", 50, 2000, 300, 10)
            wm_scale = None
        
        # Position Settings
        position_preset = st.selectbox("Position Preset", [
            "Bottom Right",
            "Bottom Left", 
            "Top Right",
            "Top Left",
            "Center",
            "Bottom Center",
            "Top Center",
            "Left Center",
            "Right Center",
            "Custom Position"
        ], help="Choose where to place your watermark")
        
        if position_preset == "Custom Position":
            col_x, col_y = st.columns(2)
            with col_x:
                custom_x = st.slider("X Position (%)", 0, 100, 50, 1)
            with col_y:
                custom_y = st.slider("Y Position (%)", 0, 100, 50, 1)
        else:
            margin_x = st.slider("Horizontal Margin (px)", 0, 200, 30, 5)
            margin_y = st.slider("Vertical Margin (px)", 0, 200, 30, 5)
        
        st.divider()
        
        # Appearance Settings
        st.subheader("3️⃣ Appearance & Effects")
        
        # Opacity
        wm_opacity = st.slider("Opacity (%)", 0, 100, 60, 1,
                              help="Lower values make watermark more transparent")
        
        # Rotation
        wm_rotation = st.slider("Rotation (degrees)", -180, 180, 0, 1,
                               help="Rotate watermark for diagonal placement")
        
        # Blur effect
        add_blur = st.checkbox("Add Soft Blur", value=False,
                              help="Adds a subtle blur for softer appearance")
        if add_blur:
            blur_amount = st.slider("Blur Intensity", 1, 10, 2, 1)
        
        # Shadow effect
        add_shadow = st.checkbox("Add Drop Shadow", value=True,
                                help="Adds depth to your watermark")
        if add_shadow:
            shadow_offset_x = st.slider("Shadow Offset X", -20, 20, 3, 1)
            shadow_offset_y = st.slider("Shadow Offset Y", -20, 20, 3, 1)
            shadow_blur = st.slider("Shadow Blur", 0, 20, 5, 1)
            shadow_opacity = st.slider("Shadow Opacity (%)", 0, 100, 50, 5)
        
        # Border/Outline
        add_border = st.checkbox("Add Border", value=False,
                                help="Adds a border around watermark")
        if add_border:
            border_width = st.slider("Border Width", 1, 20, 3, 1)
            border_color = st.color_picker("Border Color", "#FFFFFF")
        
        # Background Box
        add_background = st.checkbox("Add Background Box", value=False,
                                    help="Places watermark on colored background")
        if add_background:
            bg_color = st.color_picker("Background Color", "#000000")
            bg_opacity = st.slider("Background Opacity (%)", 0, 100, 30, 5)
            bg_padding = st.slider("Padding", 5, 50, 15, 5)
        
        st.divider()
        
        # Tiling Options
        st.subheader("4️⃣ Advanced Options")
        
        tile_watermark = st.checkbox("Tile Watermark", value=False,
                                    help="Repeat watermark across entire image")
        if tile_watermark:
            tile_spacing_x = st.slider("Horizontal Spacing", 50, 500, 200, 10)
            tile_spacing_y = st.slider("Vertical Spacing", 50, 500, 200, 10)
            tile_rotation = st.slider("Tile Rotation", -45, 45, -30, 1)
            tile_opacity = st.slider("Tile Opacity (%)", 5, 50, 15, 1)
        
        # Color adjustment
        adjust_colors = st.checkbox("Adjust Watermark Colors", value=False)
        if adjust_colors:
            brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
            contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
            saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
        
        # Batch processing options
        st.divider()
        st.subheader("5️⃣ Batch Processing")
        maintain_aspect = st.checkbox("Maintain Aspect Ratio", value=True)
        output_format = st.selectbox("Output Format", ["PNG", "JPEG", "WEBP"])
        if output_format == "JPEG":
            jpeg_quality = st.slider("JPEG Quality", 60, 100, 95, 5)
        
        # Prefix/Suffix for filenames
        add_prefix = st.text_input("Add Filename Prefix", "watermarked_")

def hex_to_rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return rgb + (alpha,)

def get_position_coords(img_width, img_height, wm_width, wm_height, position, margin_x=30, margin_y=30):
    positions = {
        "Bottom Right": (img_width - wm_width - margin_x, img_height - wm_height - margin_y),
        "Bottom Left": (margin_x, img_height - wm_height - margin_y),
        "Top Right": (img_width - wm_width - margin_x, margin_y),
        "Top Left": (margin_x, margin_y),
        "Center": ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
        "Bottom Center": ((img_width - wm_width) // 2, img_height - wm_height - margin_y),
        "Top Center": ((img_width - wm_width) // 2, margin_y),
        "Left Center": (margin_x, (img_height - wm_height) // 2),
        "Right Center": (img_width - wm_width - margin_x, (img_height - wm_height) // 2)
    }
    return positions.get(position, positions["Bottom Right"])

def apply_watermark(image, watermark_img, settings):
    img = image.copy()
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    wm = watermark_img.copy()
    if wm.mode != 'RGBA':
        wm = wm.convert('RGBA')
    
    # Apply color adjustments if enabled
    if settings.get('adjust_colors', False):
        wm = ImageEnhance.Brightness(wm).enhance(settings.get('brightness', 1.0))
        wm = ImageEnhance.Contrast(wm).enhance(settings.get('contrast', 1.0))
        wm = ImageEnhance.Color(wm).enhance(settings.get('saturation', 1.0))
    
    # Calculate size
    if settings.get('scale_mode') == "Percentage of Image":
        new_width = int(img.width * settings['scale'] / 100)
        if settings.get('maintain_aspect', True):
            aspect_ratio = wm.height / wm.width
            new_height = int(new_width * aspect_ratio)
        else:
            new_height = int(img.height * settings['scale'] / 100)
    elif settings.get('scale_mode') == "Fixed Width (px)":
        new_width = settings['fixed_width']
        aspect_ratio = wm.height / wm.width
        new_height = int(new_width * aspect_ratio)
    elif settings.get('scale_mode') == "Fixed Height (px)":
        new_height = settings['fixed_height']
        aspect_ratio = wm.width / wm.height
        new_width = int(new_height * aspect_ratio)
    else:  # Custom Size
        new_width = settings['custom_width']
        new_height = settings['custom_height']
    
    wm = wm.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Apply blur if enabled
    if settings.get('add_blur', False):
        wm = wm.filter(ImageFilter.GaussianBlur(radius=settings.get('blur_amount', 2)))
    
    # Rotate watermark
    if settings.get('rotation', 0) != 0:
        wm = wm.rotate(settings['rotation'], expand=True, resample=Image.Resampling.BICUBIC)
    
    # Adjust opacity
    alpha = wm.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(settings['opacity'] / 100)
    wm.putalpha(alpha)
    
    # Create composite layer
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    
    # Check if tiling is enabled
    if settings.get('tile_watermark', False):
        spacing_x = settings.get('tile_spacing_x', 200)
        spacing_y = settings.get('tile_spacing_y', 200)
        
        # Create tiled watermark
        tile_wm = wm.copy()
        if settings.get('tile_rotation', 0) != 0:
            tile_wm = tile_wm.rotate(settings['tile_rotation'], expand=True, resample=Image.Resampling.BICUBIC)
        
        # Adjust tile opacity
        tile_alpha = tile_wm.split()[3]
        tile_alpha = ImageEnhance.Brightness(tile_alpha).enhance(settings.get('tile_opacity', 15) / 100)
        tile_wm.putalpha(tile_alpha)
        
        # Tile across image
        for y in range(-tile_wm.height, img.height + tile_wm.height, spacing_y):
            for x in range(-tile_wm.width, img.width + tile_wm.width, spacing_x):
                layer.paste(tile_wm, (x, y), tile_wm)
    else:
        # Add background box if enabled
        if settings.get('add_background', False):
            padding = settings.get('bg_padding', 15)
            bg_width = wm.width + padding * 2
            bg_height = wm.height + padding * 2
            bg_img = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_img)
            bg_color = hex_to_rgba(settings['bg_color'], int(255 * settings['bg_opacity'] / 100))
            bg_draw.rectangle([0, 0, bg_width, bg_height], fill=bg_color)
            
            # Paste watermark on background
            bg_img.paste(wm, (padding, padding), wm)
            wm = bg_img
        
        # Add border if enabled
        if settings.get('add_border', False):
            border_width = settings.get('border_width', 3)
            bordered = Image.new('RGBA', (wm.width + border_width*2, wm.height + border_width*2), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(bordered)
            border_color = hex_to_rgba(settings['border_color'], 255)
            border_draw.rectangle([0, 0, bordered.width, bordered.height], outline=border_color, width=border_width)
            bordered.paste(wm, (border_width, border_width), wm)
            wm = bordered
        
        # Add shadow if enabled
        if settings.get('add_shadow', False):
            shadow_offset_x = settings.get('shadow_offset_x', 3)
            shadow_offset_y = settings.get('shadow_offset_y', 3)
            shadow_blur = settings.get('shadow_blur', 5)
            shadow_opacity = settings.get('shadow_opacity', 50)
            
            # Create shadow layer
            shadow = Image.new('RGBA', (wm.width + abs(shadow_offset_x)*2 + shadow_blur*2, 
                                       wm.height + abs(shadow_offset_y)*2 + shadow_blur*2), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_color = (0, 0, 0, int(255 * shadow_opacity / 100))
            
            # Draw shadow rectangle
            shadow_pos = (shadow_blur + abs(min(0, shadow_offset_x)), 
                         shadow_blur + abs(min(0, shadow_offset_y)))
            shadow_draw.rectangle([shadow_pos[0], shadow_pos[1], 
                                  shadow_pos[0] + wm.width, shadow_pos[1] + wm.height], 
                                 fill=shadow_color)
            
            # Blur shadow
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
            
            # Paste watermark on shadow
            wm_pos = (shadow_blur + abs(min(0, shadow_offset_x)) - shadow_offset_x,
                     shadow_blur + abs(min(0, shadow_offset_y)) - shadow_offset_y)
            shadow.paste(wm, wm_pos, wm)
            wm = shadow
        
        # Get position
        if settings.get('position') == "Custom Position":
            x = int(img.width * settings['custom_x'] / 100) - wm.width // 2
            y = int(img.height * settings['custom_y'] / 100) - wm.height // 2
        else:
            x, y = get_position_coords(img.width, img.height, wm.width, wm.height, 
                                      settings['position'], settings.get('margin_x', 30), 
                                      settings.get('margin_y', 30))
        
        # Ensure watermark is within bounds
        x = max(0, min(x, img.width - wm.width))
        y = max(0, min(y, img.height - wm.height))
        
        layer.paste(wm, (x, y), wm)
    
    # Composite
    result = Image.alpha_composite(img, layer)
    
    # Convert based on output format
    if settings.get('output_format') == 'JPEG':
        result = result.convert('RGB')
    
    return result

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Your Images")
    st.markdown("Upload single or multiple images to add watermarks")
    
    uploaded_files = st.file_uploader(
        "Choose image(s)", 
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'], 
        accept_multiple_files=True,
        help="Supports PNG, JPEG, WEBP, BMP, and TIFF formats"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} image(s) uploaded")
        
        # Show thumbnails
        with st.expander("📸 View Uploaded Images", expanded=False):
            thumb_cols = st.columns(min(3, len(uploaded_files)))
            for idx, file in enumerate(uploaded_files[:9]):  # Show first 9
                with thumb_cols[idx % 3]:
                    img = Image.open(file)
                    st.image(img, caption=file.name, use_container_width=True)
            if len(uploaded_files) > 9:
                st.info(f"+ {len(uploaded_files) - 9} more images")

# Process images
if uploaded_files and watermark_image:
    
    # Prepare settings dictionary
    settings = {
        'scale_mode': scale_mode,
        'scale': wm_scale if scale_mode == "Percentage of Image" else None,
        'fixed_width': wm_fixed_width if scale_mode == "Fixed Width (px)" else None,
        'fixed_height': wm_fixed_height if scale_mode == "Fixed Height (px)" else None,
        'custom_width': wm_custom_width if scale_mode == "Custom Size" else None,
        'custom_height': wm_custom_height if scale_mode == "Custom Size" else None,
        'position': position_preset,
        'custom_x': custom_x if position_preset == "Custom Position" else None,
        'custom_y': custom_y if position_preset == "Custom Position" else None,
        'margin_x': margin_x if position_preset != "Custom Position" else 30,
        'margin_y': margin_y if position_preset != "Custom Position" else 30,
        'opacity': wm_opacity,
        'rotation': wm_rotation,
        'add_blur': add_blur,
        'blur_amount': blur_amount if add_blur else 0,
        'add_shadow': add_shadow,
        'shadow_offset_x': shadow_offset_x if add_shadow else 0,
        'shadow_offset_y': shadow_offset_y if add_shadow else 0,
        'shadow_blur': shadow_blur if add_shadow else 0,
        'shadow_opacity': shadow_opacity if add_shadow else 0,
        'add_border': add_border,
        'border_width': border_width if add_border else 0,
        'border_color': border_color if add_border else "#FFFFFF",
        'add_background': add_background,
        'bg_color': bg_color if add_background else "#000000",
        'bg_opacity': bg_opacity if add_background else 30,
        'bg_padding': bg_padding if add_background else 15,
        'tile_watermark': tile_watermark,
        'tile_spacing_x': tile_spacing_x if tile_watermark else 200,
        'tile_spacing_y': tile_spacing_y if tile_watermark else 200,
        'tile_rotation': tile_rotation if tile_watermark else 0,
        'tile_opacity': tile_opacity if tile_watermark else 15,
        'adjust_colors': adjust_colors,
        'brightness': brightness if adjust_colors else 1.0,
        'contrast': contrast if adjust_colors else 1.0,
        'saturation': saturation if adjust_colors else 1.0,
        'maintain_aspect': maintain_aspect,
        'output_format': output_format,
        'jpeg_quality': jpeg_quality if output_format == "JPEG" else 95
    }
    
    with col2:
        st.subheader("✨ Preview & Results")
        
        # Process button
        if st.button("🚀 Process All Images", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_images = []
            wm_img = Image.open(watermark_image)
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                image = Image.open(uploaded_file)
                watermarked = apply_watermark(image, wm_img, settings)
                
                # Save to memory
                buf = io.BytesIO()
                if output_format == "JPEG":
                    watermarked.save(buf, format='JPEG', quality=settings['jpeg_quality'])
                elif output_format == "WEBP":
                    watermarked.save(buf, format='WEBP', quality=95)
                else:
                    watermarked.save(buf, format='PNG')
                
                # Generate filename
                name, ext = uploaded_file.name.rsplit('.', 1)
                new_filename = f"{add_prefix}{name}.{output_format.lower()}"
                
                processed_images.append({
                    'name': new_filename,
                    'data': buf.getvalue(),
                    'image': watermarked
                })
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("✅ Processing complete!")
            st.session_state.processed_images = processed_images
            
            # Show results
            st.success(f"🎉 Successfully processed {len(processed_images)} images!")
    
    # Display processed images
    if st.session_state.processed_images:
        st.divider()
        
        # Display options
        display_mode = st.radio("Display Mode", ["Grid View", "Individual View"], horizontal=True)
        
        if display_mode == "Grid View":
            cols_per_row = st.slider("Images per row", 1, 4, 2)
            cols = st.columns(cols_per_row)
            for idx, img_data in enumerate(st.session_state.processed_images):
                with cols[idx % cols_per_row]:
                    st.image(img_data['image'], caption=img_data['name'], use_container_width=True)
        else:
            selected_idx = st.selectbox("Select image to view", 
                                       range(len(st.session_state.processed_images)),
                                       format_func=lambda x: st.session_state.processed_images[x]['name'])
            st.image(st.session_state.processed_images[selected_idx]['image'], 
                    caption=st.session_state.processed_images[selected_idx]['name'],
                    use_container_width=True)
        
        st.divider()
        
        # Download section
        st.subheader("⬇️ Download Your Watermarked Images")
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            if len(st.session_state.processed_images) == 1:
                st.download_button(
                    label="💾 Download Image",
                    data=st.session_state.processed_images[0]['data'],
                    file_name=st.session_state.processed_images[0]['name'],
                    mime=f"image/{output_format.lower()}",
                    use_container_width=True
                )
            else:
                # Individual downloads
                selected_download = st.selectbox("Choose image to download",
                                                range(len(st.session_state.processed_images)),
                                                format_func=lambda x: st.session_state.processed_images[x]['name'])
                st.download_button(
                    label=f"💾 Download Selected",
                    data=st.session_state.processed_images[selected_download]['data'],
                    file_name=st.session_state.processed_images[selected_download]['name'],
                    mime=f"image/{output_format.lower()}",
                    use_container_width=True
                )
        
        with col_d2:
            if len(st.session_state.processed_images) > 1:
                # Create ZIP file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for img_data in st.session_state.processed_images:
                        zip_file.writestr(img_data['name'], img_data['data'])
                
                st.download_button(
                    label=f"📦 Download All as ZIP ({len(st.session_state.processed_images)} images)",
                    data=zip_buffer.getvalue(),
                    file_name=f"watermarked_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

elif uploaded_files and not watermark_image:
    with col2:
        st.warning("⚠️ Please upload a watermark image in the sidebar to continue")
        
elif not uploaded_files and watermark_image:
    with col2:
        st.info("📤 Upload your images to start watermarking")
        
else:
    with col2:
        st.info("👈 Get started by uploading a watermark and images")
        st.markdown("""
        ### 🎯 Professional Features:
        
        **📐 Flexible Sizing**
        - Percentage-based scaling
        - Fixed pixel dimensions
        - Custom width/height control
        - Aspect ratio preservation
        
        **🎨 Advanced Effects**
        - Drop shadows with blur control
        - Border/outline options
        - Background boxes
        - Blur effects
        - Color adjustments (brightness, contrast, saturation)
        
        **📍 Precise Positioning**
        - 9 preset positions
        - Custom X/Y positioning
        - Adjustable margins
        - Rotation support
        
        **✨ Special Features**
        - Tiling watermarks (repeated pattern)
        - Batch processing
        - Multiple output formats (PNG, JPEG, WEBP)
        - Quality control
        - Custom filename prefixes
        
        **💼 Perfect For:**
        - Photographers protecting their work
        - Businesses branding content
        - Artists signing digital art
        - Content creators marking social media posts
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Professional Watermark Studio</strong> | Built with Streamlit</p>
    <p>💡 Tip: PNG watermarks with transparency give the best results!</p>
</div>
""", unsafe_allow_html=True)
