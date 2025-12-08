"""
Service utilities package.

To keep the dashboard lightweight (e.g., when only commodity/macro modules are
needed), we avoid importing optional AI/chat helpers or pymongo-based utilities
at package import time. Import the specific helper you need directly, e.g.:

    from streamlit_app.services.chat_manager import ChatManager

Optional dependencies (openai, pymongo, etc.) are thus only required when the
corresponding submodule is explicitly used.
"""

__all__: list[str] = []

