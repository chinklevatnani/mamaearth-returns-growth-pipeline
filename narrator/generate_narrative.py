# Part 3 — Tasks 2–5: Gemini narrative and offline fallback

import json


def generate_scr_narrative_offline(findings: dict) -> dict:
    """Generate the SCR narrative without an API call."""
    try:
        cleaned_revenue = findings["cleaned_total_revenue_inr"]
        raw_revenue = findings["raw_total_revenue_inr"]
        duplicate_delta = findings["duplicate_reconciliation_delta_inr"]
        payment_rates = findings["return_rate_by_payment"]
        risk_segment = findings["highest_risk_segment"]
        peak = findings["true_peak_month"]
        january = findings["outlier_inflated_month"]

        situation = (
            f"Raw revenue was ₹{raw_revenue:,.2f} across 180 orders. "
            f"After removing five duplicate orders, 175 orders remained "
            f"with cleaned revenue of ₹{cleaned_revenue:,.2f}. The "
            f"reconciliation difference was ₹{duplicate_delta:,.2f}."
        )

        complication = (
            f"COD orders have a return rate of {payment_rates['COD']}%, "
            f"compared with {payment_rates['CARD']}% for CARD and "
            f"{payment_rates['UPI']}% for UPI. The highest-risk segment "
            f"is {risk_segment['payment_method']} in Tier-"
            f"{risk_segment['city_tier']} cities, with a return rate of "
            f"{risk_segment['return_rate_pct']}%. January's apparent "
            f"revenue of ₹{january['apparent_revenue_inr']:,.2f} is "
            f"inflated by two bulk orders."
        )

        resolution = (
            f"Investigate COD returns, especially in Tier-2 cities. "
            f"Review the two bulk orders separately when assessing "
            f"monthly performance. January revenue after excluding "
            f"these orders is ₹{january['corrected_revenue_inr']:,.2f}. "
            f"March is the true peak month at ₹{peak['revenue_inr']:,.2f}. "
            f"The analysis does not support the hypothesis that higher "
            f"discounts reduce returns; the observed correlation is "
            f"negligible."
        )

        narrative = (
            "SITUATION\n" + situation
            + "\n\nCOMPLICATION\n" + complication
            + "\n\nRESOLUTION\n" + resolution
        )

        return {
            "status": "success",
            "narrative": narrative,
            "tokens": None
        }

    except Exception as err:
        return {
            "status": "error",
            "narrative": None,
            "message": str(err)
        }


def generate_scr_narrative(findings: dict) -> dict:
    """Use Gemini when configured; otherwise use the offline fallback."""

    # Read the key from Google Colab Secrets, without hardcoding it.
    try:
        from google.colab import userdata
        api_key = userdata.get("GEMINI_API_KEY")
    except Exception:
        # No Colab secret or no configured key: use offline mode.
        return generate_scr_narrative_offline(findings)

    if not api_key:
        return generate_scr_narrative_offline(findings)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # System instruction is separate from the user prompt.
        system_instruction = (
            "You are a senior data analyst writing for Mamaearth's "
            "regional ops and finance heads. Write exactly three labeled "
            "sections: Situation, Complication, and Resolution. Every "
            "number in the output must come from the supplied findings "
            "and appear with the same value. Do not invent statistics. "
            "Give practical recommendations without claiming causation "
            "from correlation alone."
        )

        # Build the user prompt from the supplied findings dictionary.
        contents = (
            "Write a concise, factual SCR business narrative from these "
            "verified findings. Preserve their numerical values.\n\n"
            + json.dumps(findings, indent=2)
        )

        # Temperature 0.0 is appropriate for a factual report,
        # rather than creative writing.
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                max_output_tokens=500
            ),
            # Timeout is measured in milliseconds: 30 seconds.
            http_options=types.HttpOptions(timeout=30000)
        )

        narrative = response.text
        if not narrative:
            raise ValueError("Gemini returned an empty narrative.")

        usage = getattr(response, "usage_metadata", None)
        tokens = (
            getattr(usage, "total_token_count", None)
            if usage else None
        )

        return {
            "status": "success",
            "narrative": narrative,
            "tokens": tokens
        }

    except Exception as err:
        # API errors trigger the deterministic offline fallback.
        offline_result = generate_scr_narrative_offline(findings)

        if offline_result["status"] == "success":
            offline_result["message"] = (
                "Gemini failed; offline fallback used. Details: "
                + str(err)
            )
            return offline_result

        return {
            "status": "error",
            "narrative": None,
            "message": str(err)
        }


def check_numeric_accuracy(narrative: str) -> bool:
    """Check required figures after normalising thousands separators."""
    normalised = narrative.replace(",", "")

    checks = [
        ("Cleaned revenue", "97358.30"),
        ("COD return rate", "44.4"),
        ("COD + Tier-2 risk rate", "54.5"),
        ("Reconciliation difference", "2501.90"),
        ("March peak revenue", "20318.90")
    ]

    all_passed = True

    for label, figure in checks:
        passed = figure in normalised
        print(f"{'PASS' if passed else 'FAIL'} — {label}")
        if not passed:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    with open("narrator/findings.json", "r") as file:
        findings = json.load(file)

    result = generate_scr_narrative(findings)

    print("Status:", result["status"])

    if result["narrative"] is not None:
        print("\n" + result["narrative"])

        print("\nNumeric accuracy checklist:")
        check_numeric_accuracy(result["narrative"])

        with open("narrator/sample_output.txt", "w") as file:
            file.write(result["narrative"])

        print("\nSample saved to narrator/sample_output.txt")

    if result.get("message"):
        print("\nNote:", result["message"])
