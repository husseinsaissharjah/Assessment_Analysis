elif page == "🗺️ MAP Analysis":
    st.title("🗺️ MAP Analysis")

    st.info(
        "### What is a RIT Score?\n"
        "The RIT score is the scale used by MAP Growth to measure student achievement and instructional level."
    )

    st.markdown(
        "### What this does\n"
        "- Calculates RIT growth.\n"
        "- Identifies Growth, Decay, or Same performance.\n"
        "- Shows student percentile.\n"
        "- Calculates grade average RIT.\n"
        "- Identifies students below the selected percentile.\n"
        "- Identifies students requiring intervention or enrichment."
    )

    st.download_button(
        "📥 Download MAP Excel Template",
        map_template(),
        "MAP_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    map_file = st.file_uploader(
        "📄 Upload MAP Data Excel",
        type=["xlsx", "xls"],
        key="map"
    )

    if map_file:
        try:
            map_df = pd.read_excel(map_file)

            required_cols = [
                "Student Name",
                "Grade",
                "Subject",
                "Previous RIT",
                "Current RIT",
                "Percentile"
            ]

            missing = [c for c in required_cols if c not in map_df.columns]

            if missing:
                st.error("❌ Missing columns: " + ", ".join(missing))
                st.stop()

            # Convert numeric columns safely
            map_df["Previous RIT"] = pd.to_numeric(
                map_df["Previous RIT"],
                errors="coerce"
            )

            map_df["Current RIT"] = pd.to_numeric(
                map_df["Current RIT"],
                errors="coerce"
            )

            map_df["Percentile"] = pd.to_numeric(
                map_df["Percentile"],
                errors="coerce"
            )

            # Calculate RIT Growth
            map_df["RIT Growth"] = (
                map_df["Current RIT"] - map_df["Previous RIT"]
            )

            # Determine Growth Status
            def get_growth_status(x):
                if pd.isna(x):
                    return "N/A"
                if x > 0:
                    return "Growth"
                elif x < 0:
                    return "Decay"
                else:
                    return "Same"

            map_df["Growth Status"] = map_df["RIT Growth"].apply(
                get_growth_status
            )

            # Determine Support Level
            map_df["Support Level"] = map_df["Percentile"].apply(
                support_level
            )

            # ---------------------------------------------------------
            # MAP DATA PREVIEW
            # ---------------------------------------------------------

            st.subheader("📋 MAP Data Preview")
            st.dataframe(
                map_df,
                use_container_width=True
            )

            st.markdown("---")

            # ---------------------------------------------------------
            # MAP SUMMARY
            # ---------------------------------------------------------

            st.subheader("📊 MAP Summary")

            total_students = len(map_df)

            avg_previous = map_df["Previous RIT"].mean()
            avg_current = map_df["Current RIT"].mean()
            avg_growth = map_df["RIT Growth"].mean()
            avg_percentile = map_df["Percentile"].mean()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "👥 Students",
                total_students
            )

            c2.metric(
                "📉 Previous Avg RIT",
                round(avg_previous, 1) if pd.notna(avg_previous) else "N/A"
            )

            c3.metric(
                "📈 Current Avg RIT",
                round(avg_current, 1) if pd.notna(avg_current) else "N/A"
            )

            c4.metric(
                "🚀 Average Growth",
                round(avg_growth, 1) if pd.notna(avg_growth) else "N/A"
            )

            st.metric(
                "🎯 Average Percentile",
                round(avg_percentile, 1)
                if pd.notna(avg_percentile)
                else "N/A"
            )

            st.markdown("---")

            # ---------------------------------------------------------
            # GROWTH DISTRIBUTION
            # ---------------------------------------------------------

            status_count = (
                map_df["Growth Status"]
                .value_counts()
                .reset_index()
            )

            status_count.columns = ["Status", "Count"]

            v1, v2 = st.columns(2)

            with v1:
                st.subheader("📈 Student Growth")

                st.plotly_chart(
                    px.bar(
                        map_df,
                        x="Student Name",
                        y="RIT Growth",
                        color="Growth Status"
                    ),
                    use_container_width=True
                )

            with v2:
                st.subheader("📊 Growth Distribution")

                st.plotly_chart(
                    px.pie(
                        status_count,
                        names="Status",
                        values="Count",
                        hole=0.3
                    ),
                    use_container_width=True
                )

            st.markdown("---")

            # ---------------------------------------------------------
            # STUDENT PERCENTILE
            # ---------------------------------------------------------

            st.subheader("🎯 Student Percentile")

            st.plotly_chart(
                px.bar(
                    map_df,
                    x="Student Name",
                    y="Percentile",
                    color="Support Level",
                    range_y=[0, 100]
                ),
                use_container_width=True
            )

            # ---------------------------------------------------------
            # SUPPORT GROUPS
            # ---------------------------------------------------------

            st.subheader("👥 Support Groups")

            support_count = (
                map_df["Support Level"]
                .value_counts()
                .reset_index()
            )

            support_count.columns = [
                "Support Level",
                "Students"
            ]

            st.dataframe(
                support_count,
                use_container_width=True
            )

            # ---------------------------------------------------------
            # STUDENT MAP ANALYSIS
            # ---------------------------------------------------------

            st.subheader("📋 Student MAP Analysis")

            st.dataframe(
                map_df.style.map(
                    color_cell,
                    subset=["Growth Status"]
                ),
                use_container_width=True
            )

            # ---------------------------------------------------------
            # DOWNLOAD REPORT
            # ---------------------------------------------------------

            map_buffer = io.BytesIO()

            map_df.to_excel(
                map_buffer,
                index=False
            )

            st.download_button(
                "📥 Download MAP Analysis",
                map_buffer.getvalue(),
                "MAP_Analysis_Report.xlsx"
            )

        except Exception as e:
            st.error(f"❌ Error reading MAP file: {e}")
