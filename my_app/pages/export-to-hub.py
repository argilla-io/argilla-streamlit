
import argilla as rg
import streamlit as st
from utils.commons import argilla_login_flow, get_dataset_list, hf_login_flow

st.set_page_config(
    page_title="Argilla - ⛭ - Hub Exporter",
    page_icon="⛭",
    layout="wide",
)


api_url, api_key = argilla_login_flow("⛭ Hub Exporter")

st.write(
    """
    This page allows you to share your dataset from Argilla to [Hugging Face Hub](https://huggingface.co/datasets) without requiring any code!
    In the background it uses `argilla.load().prepare_for_training()` and `datasets.push_to_hub()`.
    """
)

hf_auth_token, api = hf_login_flow()


user_info = api.whoami()
organizations = [user_info["name"]] + [org["name"] for org in user_info["orgs"]]
datasets_list = [
    f"{ds['owner']}/{ds['name']}" for ds in get_dataset_list(api_url, api_key)
]
dataset_argilla = st.selectbox("Argilla Dataset Name", options=datasets_list)
dataset_argilla_name = dataset_argilla.split("/")[-1]
dataset_argilla_workspace = dataset_argilla.split("/")[0]
target_organization = st.selectbox(
    "Target Hugging Face organization for saving the data",
    options=organizations,
    help="the namespace where the data should be saved",
)

if dataset_argilla:
    dataset_huggingface = st.text_input(
        "Hugging Face Dataset Name",
        f"{target_organization}/{dataset_argilla_name}",
    )
    query = st.text_input(
        "Query to filter records (optional). See [query"
        " syntax](https://docs.argilla.io/en/latest/guides/query_datasets.html)",
        value="status: Validated",
    )
    with st.spinner(text="Loading dataset..."):
        rg.set_workspace(dataset_argilla_workspace)
        ds = rg.load(dataset_argilla_name, query=query)
    st.write("Below is a subset of the dataframe", ds.to_pandas().head(5))
    train_size = st.number_input(
        "Train size", value=0.8, min_value=0.0, max_value=1.0
    )
    private = st.checkbox("Use Private Repo", value=False)
    button = st.button("Export to Hugging Face")

    if button:
        with st.spinner(text="Export in progress..."):
            ds_ds = ds.prepare_for_training(
                framework="transformers", train_size=train_size
            )
            ds_ds.push_to_hub(dataset_huggingface, token=hf_auth_token)
        st.success(
            "Dataset pushed to Hugging Face and available"
            f" [here](https://huggingface.co/datasets?sort=downloads&search={dataset_huggingface})"
        )
else:
    st.warning("Please enter a dataset name")

