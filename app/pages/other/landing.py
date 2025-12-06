"""Landing page - displays project README and welcome information."""

from pathlib import Path

import streamlit as st

from app.services.auth import require_login

require_login()


@st.cache_data
def load_readme() -> str:
    """Load README.md content from project root."""
    readme_path = Path(__file__).parents[3] / "About.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "README file not found."


def render_landing_page():
    """Render landing page with README content and welcome info."""
    # Header with greeting
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("🦈 Welcome to Otomax Dashboard")
    with col2:
        st.write("")  # Spacing

    st.caption(
        "An application built with Streamlit to monitor reseller performance "
        "and drive data-driven decisions for **otomax**."
    )

    st.divider()

    # Load and display README content
    load_readme.clear()
    readme_content = load_readme()

    # Display README but skip mermaid diagrams (Streamlit doesn't render them natively)
    lines = readme_content.split("\n")
    filtered_lines = []
    skip_mermaid = False

    for line in lines:
        if line.strip().startswith("```mermaid"):
            skip_mermaid = True
            filtered_lines.append(
                "\n> 📊 *Diagram view not supported in Streamlit - view in GitHub for visual representation*\n"
            )
            continue
        elif line.strip().startswith("```") and skip_mermaid:
            skip_mermaid = False
            continue
        elif not skip_mermaid:
            filtered_lines.append(line)

    filtered_content = "\n".join(filtered_lines)
    st.markdown(filtered_content)

    # Info boxes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("💡 **Pro Tip**: Use sidebar to navigate between different reports")
    with col2:
        st.success(
            "✨ **Data-Driven**: Make informed decisions with real-time insights"
        )
    with col3:
        st.warning("📊 **Interactive**: Explore and analyze data at your own pace")


render_landing_page()
