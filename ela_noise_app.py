import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import skimage.filters as filters


def noise_analysis(image, noise_amplitude=1.0, equalize_histogram=False):
    """Perform noise analysis on the given image."""
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Apply median filter to isolate noise
    noise = gray_image - filters.median(gray_image, behavior='ndimage')

    # Enhance noise visibility
    enhanced_noise = cv2.convertScaleAbs(noise, alpha=noise_amplitude, beta=0)

    if equalize_histogram:
        enhanced_noise = cv2.equalizeHist(enhanced_noise)

    return gray_image, enhanced_noise


def error_level_analysis(image, quality=90, scale=10):
    """Perform error level analysis on the given image."""
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    ela_path = 'ela_image.jpg'
    image.save(ela_path, 'JPEG', quality=quality)

    compressed = Image.open(ela_path)
    ela_image = ImageChops.difference(image, compressed)

    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])

    scale_factor = scale * 255.0 / max_diff
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale_factor)

    return image, ela_image


# Streamlit app
st.title("Image Forensics Analysis")

# Tabs
tab1, tab2 = st.tabs(["Noise Analysis", "Error Level Analysis"])

with tab1:
    st.header("Noise Analysis")
    image_path_noise = st.file_uploader(
        "Upload an image for Noise Analysis", type=["png", "jpg", "jpeg"], key="noise"
    )
    noise_amplitude = st.slider('Noise Amplitude', 1.0, 10.0, 1.0)
    equalize_histogram = st.checkbox('Equalize Histogram', value=False)

    if image_path_noise is not None:
        image_noise = Image.open(image_path_noise)
        original_noise, noise_image = noise_analysis(
            image_noise, noise_amplitude, equalize_histogram
        )

        st.image(original_noise, caption="Original Image", use_column_width=True)
        st.image(noise_image, caption="Noise Analysis Image", use_column_width=True)

with tab2:
    st.header("Error Level Analysis")
    image_path_ela = st.file_uploader(
        "Upload an image for Error Level Analysis", type=["png", "jpg", "jpeg"], key="ela"
    )
    quality = st.slider('JPEG Quality', 10, 100, 90)
    scale = st.slider('Error Scale', 1, 20, 10)

    if image_path_ela is not None:
        image_ela = Image.open(image_path_ela)
        original_ela, ela_image = error_level_analysis(image_ela, quality, scale)

        st.image(original_ela, caption="Original Image", use_column_width=True)
        st.image(ela_image, caption="Error Level Analysis (ELA) Image", use_column_width=True)
