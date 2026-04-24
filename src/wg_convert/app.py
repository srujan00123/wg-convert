import streamlit as st

try:
    from wg_convert.cli import format_conf, load
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from wg_convert.cli import format_conf, load


def run() -> None:
    st.set_page_config(page_title="wg-convert", page_icon=None, layout="centered")
    st.title("WireGuard Config Converter")
    st.caption("Paste an INI or JSON WireGuard config, pick a name, and download the `.conf` file.")

    name = st.text_input("Config name", value="", placeholder="wg0", help="Output file will be <name>.conf")

    uploaded = st.file_uploader("Or upload a file", type=["conf", "txt", "json", "ini"])
    default_text = uploaded.read().decode("utf-8") if uploaded else ""
    text = st.text_area("Config input", value=default_text, height=320, placeholder="[Interface]\n...")

    if not name.strip():
        st.warning("Enter a config name.")
        return

    if not text.strip():
        st.info("Paste a config above.")
        return

    try:
        sections = load(text)
    except Exception as e:
        st.error(f"Failed to parse input: {e}")
        return

    if not sections.get("Interface"):
        st.error("No [Interface] section found.")
        return

    conf = format_conf(sections)
    filename = f"{name.strip()}.conf"

    st.subheader("Output")
    st.code(conf, language="ini")
    st.download_button(
        label=f"Download {filename}",
        data=conf,
        file_name=filename,
        mime="text/plain",
    )


if __name__ == "__main__":
    run()
