
import asyncio
import json
import sys
from pathlib import Path

# Locate the backend folder so we can import the application.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.services.brief_extractor import extract_client_brief


# Locate the evaluation dataset.
CASES_FILE = Path(__file__).with_name("cases.json")


def normalize(value: str) -> str:
    """Normalize text for simple feature comparisons."""
    return " ".join(
        value.casefold().replace("catalogue", "catalog").split()
    )


def evaluate_result(case: dict, result) -> list[tuple[str, bool, str]]:
    """
    Compare Gemini's response against the expected evaluation criteria.

    Returns:
        A list containing the criterion name, pass/fail status,
        and an explanation.
    """

    actual = result.model_dump()
    expected = case["expected"]

    checks = []

    # 1. Check fields that should have exact expected values.
    for field, expected_value in expected.items():

        # These require special evaluation logic.
        if field in (
            "required_features",
            "forbidden_values",
            "contains",
            "non_empty",
        ):
            continue

        actual_value = actual.get(field)

        passed = actual_value == expected_value

        checks.append((
            f"{field} matches expected value",
            passed,
            f"Expected: {expected_value!r}, Actual: {actual_value!r}"
        ))

    # 2. Check that selected fields contain useful information.
    for field in expected.get("non_empty", []):
        actual_value = actual.get(field)
        passed = (
            bool(actual_value.strip())
            if isinstance(actual_value, str)
            else bool(actual_value)
        )
        checks.append((
            f"Field is not empty: {field}",
            passed,
            f"Actual value: {actual_value!r}"
        ))

    # Check that expected phrases appear in text fields or list entries.
    for field, phrases in expected.get("contains", {}).items():
        actual_value = actual.get(field)
        actual_values = (
            actual_value if isinstance(actual_value, list)
            else [actual_value]
        )

        for phrase in phrases:
            target = normalize(phrase)
            found = any(
                target in normalize(str(value))
                for value in actual_values
                if value is not None
            )
            checks.append((
                f"Expected text in {field}: {phrase}",
                found,
                f"Actual value: {actual_value!r}"
            ))

    # 3. Check that all required features were extracted.
    actual_features = actual.get("requested_features", [])

    for feature in expected.get("required_features", []):
        target = normalize(feature)

        found = any(
            target in normalize(str(actual_feature))
            for actual_feature in actual_features
        )

        checks.append((
            f"Required feature: {feature}",
            found,
            f"Actual features: {actual_features}"
        ))

    # 4. Check that forbidden values were NOT extracted.
    for field, forbidden_values in expected.get(
        "forbidden_values", {}
    ).items():

        actual_value = actual.get(field)

        for forbidden in forbidden_values:

            if isinstance(actual_value, list):
                actual_values = actual_value
            else:
                actual_values = [actual_value]

            found = any(
                str(value).casefold() == str(forbidden).casefold()
                for value in actual_values
                if value is not None
            )

            checks.append((
                f"Forbidden value: {field} = {forbidden}",
                not found,
                f"Actual value: {actual_value!r}"
            ))

    return checks


async def run_evaluations():

    # Load evaluation cases from JSON.
    with open(CASES_FILE, "r", encoding="utf-8") as file:
        cases = json.load(file)

    total_cases = len(cases)
    passed_cases = 0
    total_checks = 0
    passed_checks = 0

    print("\n===================================")
    print("       AI EVALUATION RUNNER")
    print("===================================\n")

    for case in cases:

        print(f"\nRunning: {case['id']}")
        print(f"Description: {case['description']}")
        print("-----------------------------------")

        try:
            # Send the test message to the actual Gemini service.
            result = await extract_with_retry(case["input"])

            # Evaluate the returned ClientBrief.
            checks = evaluate_result(case, result)

            case_passed = all(passed for _, passed, _ in checks)

            total_checks += len(checks)
            passed_checks += sum(
                1 for _, passed, _ in checks if passed
            )

            for name, passed, explanation in checks:

                status = "PASS" if passed else "FAIL"

                print(f"[{status}] {name}")

                if not passed:
                    print(f"       {explanation}")

            if case_passed:
                passed_cases += 1
                print("\nCASE RESULT: PASSED")
            else:
                print("\nCASE RESULT: FAILED")

        except Exception as error:
            print(f"\nCASE ERROR: {type(error).__name__}: {error}")

        print("-----------------------------------")

    # Final evaluation summary.
    print("\n===================================")
    print("          FINAL RESULTS")
    print("===================================")

    print(f"Total cases: {total_cases}")
    print(f"Passed cases: {passed_cases}")
    print(f"Failed cases: {total_cases - passed_cases}")

    print(
        f"Criteria passed: {passed_checks}/{total_checks}"
    )

    if total_checks:
        score = (passed_checks / total_checks) * 100
        print(f"Criteria pass rate: {score:.1f}%")

    print("===================================\n")


async def extract_with_retry(message: str, max_attempts: int = 3):
    """
    Retry Gemini extraction when the provider temporarily
    returns a 503 UNAVAILABLE error.
    """

    for attempt in range(1, max_attempts + 1):
        try:
            return await extract_client_brief(message)

        except Exception as error:

            is_temporary_error = (
                "503" in str(error)
                and "UNAVAILABLE" in str(error)
            )

            if not is_temporary_error or attempt == max_attempts:
                raise

            delay = 2 ** attempt

            print(
                f"[RETRY] Gemini unavailable. "
                f"Attempt {attempt}/{max_attempts}. "
                f"Retrying in {delay} seconds..."
            )

            await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(run_evaluations())
