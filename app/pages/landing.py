"""ini sample landing page. default ketika user berhasil login."""

import streamlit as st

_STREAM_CONTENT = """
## About oto-dashboard

oto-dashboard is designed to monitor reseller performance and sales metrics for otomax,
a business focused on selling internet data packages through resellers across Indonesia.

## Features
- **Reseller Performance Monitoring** - Track key metrics and KPIs
- **Sales Analysis** - Analyze sales trends and patterns
- **Data-Driven Insights** - Leverage visualizations for better decisions
- **Interactive Dashboards** - Responsive and dynamic data exploration

## Getting Started
To get started, please log in using the sidebar. Once authenticated, you will have access to various
reports and analytics tailored to help make data-driven decisions.

We hope you enjoy using oto-dashboard!
"""


def render_landing_page():
    """Render landing page with greeting shown only once per session.

    The streaming animation and welcome toast only appear on the first
    visit to the landing page. Subsequent visits show static content.
    """
    st.header("Welcome to oto-dashboard!")

    st.markdown(
        "An application built with Streamlit to monitor reseller performance "
        "and drive data-driven decisions for otomax."
    )

    # Show content with st.markdown only
    st.markdown(_STREAM_CONTENT)

    # Always show these info blocks
    st.info(
        "💡 Use the sidebar navigation to explore different reports after logging in."
    )
    st.success("✨ Thank you for using oto-dashboard!")
    st.divider()


render_landing_page()
