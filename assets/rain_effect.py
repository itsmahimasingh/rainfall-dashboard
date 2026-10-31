"""Animated falling rain over the background (pure CSS, no video needed)."""
import base64
import random

import streamlit as st


def _rain_tile(seed, size, drops, length, opacity):
    """A square picture with thin raindrop lines at random spots; it repeats across the screen."""
    rng = random.Random(seed)
    lines = ''
    for _ in range(drops):
        x = rng.randint(0, size)
        y = rng.randint(0, size - length)
        lines += f"<line x1='{x}' y1='{y}' x2='{x}' y2='{y + length}'/>"
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}'>"
           f"<g stroke='white' stroke-opacity='{opacity}' stroke-width='1.2' "
           f"stroke-linecap='round'>{lines}</g></svg>")
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


def add_rain():
    near = _rain_tile(seed=1, size=220, drops=14, length=28, opacity=0.45)   # bigger, faster drops
    far = _rain_tile(seed=2, size=160, drops=22, length=14, opacity=0.25)    # smaller, slower drops
    st.markdown(f"""
<style>
.rain {{ position: fixed; inset: 0; pointer-events: none; z-index: 0; }}
.rain-near {{ background-image: url("{near}"); animation: fall-near 0.7s linear infinite; }}
.rain-far  {{ background-image: url("{far}");  animation: fall-far 1.4s linear infinite; }}
@keyframes fall-near {{ from {{ background-position: 0 0; }} to {{ background-position: 0 220px; }} }}
@keyframes fall-far  {{ from {{ background-position: 0 0; }} to {{ background-position: 0 160px; }} }}
@media (prefers-reduced-motion: reduce) {{ .rain {{ animation: none; }} }}
</style>
<div class="rain rain-far"></div>
<div class="rain rain-near"></div>
""", unsafe_allow_html=True)