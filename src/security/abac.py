from typing import Dict
import pandas as pd

from src.security.user_context import UserContext


def abac_filter_chunks(
    chunks_df: pd.DataFrame,
    user: UserContext
) -> pd.DataFrame:
    """
    Apply ABAC filtering to chunks based on user attributes.

    Args:
        chunks_df: chunk-level dataframe with security metadata
        user: authenticated user context

    Returns:
        Filtered dataframe containing only allowed chunks
    """

    allowed = chunks_df.loc[
        (chunks_df["security_tier_level"] <= user.clearance) &
        (chunks_df["owner_team"] == user.department)
    ].copy()

    return allowed

def abac_allows(metadata_row, user):
    return (
        metadata_row["security_tier_level"] <= user.clearance and
        metadata_row["owner_team"] == user.department
    )
    