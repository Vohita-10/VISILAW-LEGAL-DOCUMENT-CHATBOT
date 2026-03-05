class MetadataStore:
    def __init__(self, metadata_df, key="row_id"):
        self._store = metadata_df.set_index(key).to_dict(orient="index")

    def get(self, row_id):
        return self._store.get(row_id)
