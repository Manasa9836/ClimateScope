from data_preparation import clean_data
from data_validation import validate_data
from feature_engineering import create_features
from generative_summary import generate_summary
from analysis import perform_analysis


def run_pipeline():

    print("\n🚀 Starting ClimateScope Data Pipeline...\n")

    print("🔹 Step 1: Data Preparation")
    df = clean_data()

    print("\n🔹 Step 2: Data Validation")
    validate_data(df)

    print("\n🔹 Step 3: Advanced Analysis")
    df = perform_analysis(df)

    print("\n🔹 Step 4: Feature Engineering")
    create_features(df)

    print("\n🔹 Step 5: Generative Summary")
    generate_summary(df)

    print("\n🎉 Pipeline Execution Completed Successfully!\n")


if __name__ == "__main__":
    run_pipeline()