"""Test Vietnamese text rendering in Streamlit HTML"""
import streamlit as st

st.set_page_config(page_title="Vietnamese Text Test", layout="wide")

# Test data
sectors = [
    "Xây dựng và Vật liệu",
    "Ngân hàng",
    "Hóa chất",
    "Bất động sản",
    "Công nghệ Thông tin"
]

st.title("Vietnamese Text Rendering Test")

# Test 1: Direct markdown
st.subheader("Test 1: Direct text in st.markdown")
for i, sector in enumerate(sectors):
    st.markdown(f"**{i+1}.** {sector}")

# Test 2: HTML in st.markdown
st.subheader("Test 2: HTML spans")
for i, sector in enumerate(sectors):
    html = f'<span style="color: #E2E8F0; font-weight: 500;">{sector}</span>'
    st.markdown(html, unsafe_allow_html=True)

# Test 3: Complex HTML like dashboard
st.subheader("Test 3: Complex HTML (Dashboard style)")
sectors_html = ""
for i, sector in enumerate(sectors):
    sectors_html += f'''
    <div style="display: flex; align-items: center; justify-content: space-between;
                padding: 10px 12px; background: rgba(0,0,0,0.2); border-radius: 8px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #94A3B8; font-weight: 600;">#{i+1}</span>
            <span style="color: #E2E8F0; font-weight: 500;">{sector}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="color: #94A3B8;">12.3x</span>
            <span style="color: #00D4AA; font-weight: 500;">● Test</span>
        </div>
    </div>
    '''

st.markdown(sectors_html, unsafe_allow_html=True)

# Test 4: Check encoding
st.subheader("Test 4: Encoding info")
test_sector = "Xây dựng và Vật liệu"
st.write(f"Sector: {test_sector}")
st.write(f"Length (chars): {len(test_sector)}")
st.write(f"Length (bytes UTF-8): {len(test_sector.encode('utf-8'))}")
st.write(f"Repr: {test_sector!r}")

# Test 5: Using f-string in markdown
st.subheader("Test 5: F-string in st.markdown")
html_fstring = f'''
<div style="background: rgba(26, 22, 37, 0.9); padding: 20px;">
    <span style="color: #E2E8F0;">Sector name: {test_sector}</span>
</div>
'''
st.markdown(html_fstring, unsafe_allow_html=True)
