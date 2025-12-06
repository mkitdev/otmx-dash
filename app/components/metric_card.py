"""Custom Metric Card Component dengan design yang lebih fleksibel."""

import streamlit as st


def metric_card_custom(
    title: str,
    content: str | int | float,
    description: str = "",
    color: str = "blue",
) -> None:
    """Render custom metric card dengan layout 2 kolom minimalistic.

    Args:
        title: Judul utama card (misal: "Operator")
        content: Angka/value yang ditampilkan besar (misal: 42)
        description: Deskripsi di bawah title (misal: "Total Group Operator")
        color: Warna accent untuk angka. Bisa:
            - Named color: blue, green, red, orange, purple, indigo, cyan
            - Hex color: #FF5733, #3B82F6, dll
            - RGB: rgb(255, 87, 51)

    Example:
        >>> metric_card_custom(
        ...     title="Operator",
        ...     content=42,
        ...     description="Total Group Operator",
        ...     color="blue",  # Named color
        ... )
        >>> metric_card_custom(
        ...     title="Revenue",
        ...     content="$5.2M",
        ...     description="Total Revenue",
        ...     color="#FF6B6B",  # Custom hex
        ... )
        >>> metric_card_custom(
        ...     title="Growth",
        ...     content="24%",
        ...     description="YoY Growth",
        ...     color="rgb(34, 197, 94)",  # RGB
        ... )
    """
    # Color palette mapping (named colors)
    color_map = {
        "blue": "#3B82F6",
        "green": "#10B981",
        "red": "#EF4444",
        "orange": "#F97316",
        "purple": "#A855F7",
        "indigo": "#6366F1",
        "cyan": "#06B6D4",
    }

    # Check if color is a named color or hex/rgb code
    accent_color = color_map.get(
        color, color
    )  # If not in map, use as-is (assume hex/rgb)

    # HTML + CSS untuk card layout 2 kolom (left text | right number)
    card_html = f"""
    <div style="
        display: flex;
        align-items: stretch;
        justify-content: space-between;
        padding: 24px;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 12px;
        border-left: 4px solid {accent_color};
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <!-- LEFT SECTION: Title & Description -->
        <div style="
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 8px;
            flex: 1;
        ">
            <!-- Title (Besar) -->
            <div style="
                font-size: 18px;
                color: #1F2937;
                font-weight: 600;
                letter-spacing: 0px;
            ">
                {title}
            </div>

            <!-- Description (Kecil) -->
            <div style="
                font-size: 13px;
                color: #9CA3AF;
                font-weight: 400;
            ">
                {description}
            </div>
        </div>

        <!-- RIGHT SECTION: Content (Big Number) -->
        <div style="
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-left: 20px;
        ">
            <div style="
                font-size: 48px;
                font-weight: 700;
                color: {accent_color};
                line-height: 1;
                letter-spacing: -1px;
            ">
                {content}
            </div>
        </div>
    </div>
    """

    st.html(card_html)
