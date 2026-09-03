# =========================================================
# OBJECTIVE-STYLE CLASS COMPARISON FOR TOTAL MARK
# =========================================================

st.subheader(t("Better Class by Assessment Total Mark"))

total_comparison_rows = []

# Calculate average total percentage for each class
for section_name, section_df in section_data.items():

    if "Pct" not in section_df.columns:
        continue

    avg_percentage = section_df["Pct"].mean()

    total_comparison_rows.append({
        "Class": section_name,
        "Average": avg_percentage
    })


if total_comparison_rows:

    total_comparison_df = pd.DataFrame(total_comparison_rows)

    # -----------------------------------------------------
    # Find the class with the highest average
    # -----------------------------------------------------
    highest_average = total_comparison_df["Average"].max()
    lowest_average = total_comparison_df["Average"].min()

    best_classes = total_comparison_df[
        total_comparison_df["Average"] == highest_average
    ]["Class"].tolist()

    if len(best_classes) == 1:
        better_class = best_classes[0]
    else:
        better_class = t("Tie")

    difference = highest_average - lowest_average

    # -----------------------------------------------------
    # Create comparison table
    # -----------------------------------------------------
    comparison_display = {}

    for _, row in total_comparison_df.iterrows():
        comparison_display[
            f"{row['Class']} {t('Class Average')}"
        ] = f"{row['Average']:.2f}%"

    comparison_display[t("Better Class")] = better_class
    comparison_display[t("Difference")] = f"{difference:.2f}%"

    comparison_table = pd.DataFrame(
        [comparison_display]
    )

    st.dataframe(
        comparison_table,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Detailed comparison table
    # -----------------------------------------------------
    detailed_rows = []

    for _, row in total_comparison_df.iterrows():
        detailed_rows.append({
            "Class": row["Class"],
            t("Class Average"): f"{row['Average']:.2f}%"
        })

    detailed_df = pd.DataFrame(detailed_rows)

    st.markdown(f"### {t('Class Average')}")

    st.dataframe(
        detailed_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Winner summary
    # -----------------------------------------------------
    winner_summary = pd.DataFrame({
        t("Better Class"): [better_class],
        t("Difference"): [f"{difference:.2f}%"]
    })

    st.markdown(f"### {t('Better Class')}")

    st.dataframe(
        winner_summary,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Comparison chart
    # -----------------------------------------------------
    fig_total_comparison = px.bar(
        total_comparison_df,
        x="Class",
        y="Average",
        text=total_comparison_df["Average"].round(2),
        title=t("Assessment Total Mark Comparison"),
        labels={
            "Class": t("Class"),
            "Average": t("Class Average")
        }
    )

    fig_total_comparison.update_traces(
        texttemplate="%{text}%",
        textposition="outside"
    )

    fig_total_comparison.update_layout(
        yaxis_title=t("Class Average"),
        xaxis_title=t("Class"),
        yaxis=dict(range=[0, 100])
    )

    st.plotly_chart(
        fig_total_comparison,
        use_container_width=True
    )

else:
    st.warning(
        t("No data available for total mark comparison.")
    )
