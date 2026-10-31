"""Soft, slowly drifting clouds across the top of the page (pure SVG + CSS, no image files)."""
import base64

import streamlit as st


def _cloud_tile(seed, frequency, density):
    """A wide, seamless strip of cloud texture made with fractal noise."""
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='1600' height='420'>
  <filter id='c' x='0' y='0' width='100%' height='100%'>
    <feTurbulence type='fractalNoise' baseFrequency='{frequency}' numOctaves='5'
                  seed='{seed}' stitchTiles='stitch'/>
    <feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  {density} 0 0 0 -0.78'/>
    <feGaussianBlur stdDeviation='1.2'/>
  </filter>
  <rect width='100%' height='100%' filter='url(#c)'/>
</svg>"""
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


def add_clouds():
    far = _cloud_tile(seed=7, frequency='0.0035 0.009', density=1.7)    # big, faint, slow
    near = _cloud_tile(seed=21, frequency='0.005 0.012', density=1.9)   # smaller, brighter, faster
    st.markdown(f"""
<style>
.clouds {{
    position: fixed; top: 0; left: 0; right: 0; height: 48vh;
    pointer-events: none; z-index: 0;
    background-repeat: repeat-x; background-size: 1600px 420px;
    -webkit-mask-image: linear-gradient(to bottom, black 0%, black 35%, transparent 100%);
    mask-image: linear-gradient(to bottom, black 0%, black 35%, transparent 100%);
}}
.clouds-far  {{ background-image: url("{far}");  opacity: 0.35; animation: drift 160s linear infinite; }}
.clouds-near {{ background-image: url("{near}"); opacity: 0.55; animation: drift 90s linear infinite; }}
@keyframes drift {{ from {{ background-position: 0 0; }} to {{ background-position: 1600px 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .clouds {{ animation: none; }} }}
</style>
<div class="clouds clouds-far"></div>
<div class="clouds clouds-near"></div>
""", unsafe_allow_html=True)