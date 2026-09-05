"""
ThalaGap — a prototype tool that shows which beta-thalassaemia (HBB gene)
mutations are commonly reported in a given Pakistani region/ethnic group,
and flags which of those are covered by the standard 5-mutation ARMS-PCR
screening panel versus which require full sequencing to detect.

This is a literature-derived data tool, not a diagnostic device.
It does not diagnose, predict, or give medical advice to any individual.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Deploy for free:
    1. Push this folder to a public GitHub repo.
    2. Go to https://share.streamlit.io , sign in with GitHub.
    3. Point it at your repo and app.py. It gives you a public link.
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ThalaGap", page_icon="🧬", layout="wide")

DATA_PATH = "data/mutations.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def main():
    st.title("🧬 ThalaGap")
    st.caption(
        "A prototype tool mapping published beta-thalassaemia (HBB gene) mutation "
        "data across Pakistani regions/ethnic groups, and flagging which mutations "
        "fall outside the standard screening panel."
    )

    st.warning(
        "This is a data-aggregation and software prototype built from published "
        "literature. It is **not** a diagnostic tool and gives **no** medical advice. "
        "All figures should be checked against the cited source before any real-world use.",
        icon="⚠️",
    )

    df = load_data()

    # --- Sidebar filters ---
    st.sidebar.header("Filter")
    groups = ["All"] + sorted(df["region_or_ethnicity"].dropna().unique().tolist())
    selected_group = st.sidebar.selectbox("Region / ethnic group", groups)

    tiers = ["All"] + sorted(df["panel_tier"].dropna().unique().tolist())
    selected_tier = st.sidebar.selectbox("Panel coverage", tiers)

    filtered = df.copy()
    if selected_group != "All":
        filtered = filtered[filtered["region_or_ethnicity"] == selected_group]
    if selected_tier != "All":
        filtered = filtered[filtered["panel_tier"] == selected_tier]

    # --- Headline gap stat ---
    total = len(df)
    outside_panel = len(df[df["panel_tier"] != "common_panel"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Mutation records in dataset", total)
    col2.metric("Outside standard 5-mutation panel", outside_panel)
    col3.metric(
        "Share needing sequencing to detect",
        f"{(outside_panel / total * 100):.0f}%" if total else "—",
    )

    st.subheader("Mutation records")
    st.dataframe(
        filtered[
            [
                "mutation_legacy",
                "mutation_hgvs",
                "region_or_ethnicity",
                "n_alleles",
                "frequency_pct",
                "panel_tier",
                "clinvar_status",
                "source_short",
            ]
        ],
        use_container_width=True,
    )

    with st.expander("Sources cited in this view"):
        for src in filtered["source_full"].dropna().unique():
            st.write(f"- {src}")

    st.divider()
    st.caption(
        "Built by Syeda Minhal Jannat as an independent bioinformatics project. "
        "Dataset compiled from published Pakistani-population studies; mutation "
        "database status cross-checked against ClinVar, HbVar, and IthaGenes."
    )


if __name__ == "__main__":
    main()
