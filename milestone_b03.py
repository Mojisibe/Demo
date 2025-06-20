# Commented out IPython magic to ensure Python compatibility.
#Import Libraries and print their versions
%run imports.py

# Commented out IPython magic to ensure Python compatibility.
%run model_B02.py

def calculate_odds_ratio(idata, var_name="effect"):
    """
    Calculates the odds ratio and its 95% HDI from the posterior samples.

    Args:
        idata (az.InferenceData): InferenceData object.
        var_name (str, optional): Name of the parameter. Defaults to "effect".

    Returns:
        pd.DataFrame: DataFrame with mean, lower, and upper HDI for the odds ratio.
                      Returns an empty DataFrame if there's an error.
    """

    try:
        posterior_samples = idata.posterior[var_name].values.flatten()
        odds_ratios = np.exp(posterior_samples)
        hdi = az.hdi(odds_ratios, hdi_prob=0.95)
        mean_or = np.mean(odds_ratios)

        or_summary = pd.DataFrame({
            "mean": [mean_or],
            "hdi_lower": [hdi[0]],
            "hdi_upper": [hdi[1]]
        })
        return or_summary

    except KeyError:
        print(f"Variable '{var_name}' not found in posterior.")
        return pd.DataFrame()  # Return empty DataFrame to signal error

import os
import numpy as np
import matplotlib.pyplot as plt
import arviz as az

def run_and_summarize(data, model_func, label="b02", output_dir="../results", **model_kwargs):
    """
    Runs the specified PyMC model function with data and optional model parameters,
    summarizes results, and saves output files including plots, summaries, and metrics.

    Parameters:
        data (dict): Dictionary with keys 'predictor' and 'outcome'.
        model_func (function): PyMC model function to use.
        label (str): Label to tag output files.
        output_dir (str): Directory to save outputs.
        **model_kwargs: Additional keyword arguments passed to model_func.

    Returns:
        idata (InferenceData): ArviZ inference data object.
        waic (ELPDData): WAIC estimate.
        loo (ELPDData): LOO estimate.
        bic (float): Bayesian Information Criterion.
    """
    os.makedirs(output_dir, exist_ok=True)

    #Call the model function with additional model parameters
    model, idata, waic, loo, bic = model_func(
        data["predictor"],
        data["outcome"],
        **model_kwargs  # Pass arguments like variant="B01", seed=123, etc.
    )

    # Save InferenceData
    idata_path = os.path.join(output_dir, f"idata_{label}.nc")
    idata.to_netcdf(idata_path)

    # Determine var_names based on model
    var_names = ["intercept", "level_effects"]
    if "effect" in idata.posterior:
        var_names += ["effect", "sd_fluctuation"]
    if "p" in idata.posterior:
        var_names.append("p")

    # Remove problematic or degenerate variables
    clean_var_names = []
    for var in var_names:
        if var in idata.posterior:
            values = idata.posterior[var].values
            if np.isnan(values).all():
                print(f"⚠️ Skipping '{var}': all NaNs in posterior.")
            elif np.allclose(values, values.mean()):
                print(f"⚠️ Skipping '{var}': constant values in posterior.")
            else:
                clean_var_names.append(var)
        else:
            print(f"⚠️ Skipping '{var}': not found in posterior.")

    # Save Summary
    summary = az.summary(idata, var_names=clean_var_names)
    summary_path = os.path.join(output_dir, f"survey_summary_{label}.csv")
    summary.to_csv(summary_path)

    # Calculate and save Odds Ratio summary (only for B02)
    if "effect" in idata.posterior:
        try:
            or_summary = calculate_odds_ratio(idata)
            if not or_summary.empty:
                or_summary_path = os.path.join(output_dir, f"survey_or_summary_{label}.csv")
                or_summary.to_csv(or_summary_path)
            else:
                print("Odds ratio calculation failed. Not saving.")
        except Exception as e:
            print(f"❌ Error calculating odds ratio: {e}")
    else:
        print("Model does not have 'effect' parameter. Skipping OR calculation.")

    # Save WAIC, LOO, BIC as a markdown file
    metrics_path = os.path.join(output_dir, f"survey_model_metrics_{label}.md")
    with open(metrics_path, "w") as f:
        f.write(f"## Model {label.upper()} Metrics\n\n")
        f.write("### WAIC\n```\n" + waic.to_string() + "\n```\n")
        f.write("### LOO\n```\n" + loo.to_string() + "\n```\n")
        f.write(f"### BIC\n```\n\nBIC = {bic:.2f}\n```")

    # Trace plot (excluding 'p')
    trace_vars = [v for v in clean_var_names if v != "p"]
    if trace_vars:
        trace_plot_path = os.path.join(output_dir, f"survey_trace_{label}.png")
        az.plot_trace(idata, var_names=trace_vars)
        plt.tight_layout()
        plt.savefig(trace_plot_path, dpi=300)
        plt.close()

    # Posterior plot for effect (if exists)
    if "effect" in idata.posterior:
        effect_plot_path = os.path.join(output_dir, f"survey_posterior_effect_{label}.png")
        az.plot_posterior(idata, var_names=["effect"])
        plt.tight_layout()
        plt.savefig(effect_plot_path, dpi=300)
        plt.close()

    # Posterior plot for a subset of 'p'
    if "p" in idata.posterior:
        try:
            obs_count = idata.posterior["p"].shape[-1]
            plot_indices = np.random.choice(obs_count, size=min(20, obs_count), replace=False)
            posterior_plot_path = os.path.join(output_dir, f"survey_posterior_p_{label}.png")
            az.plot_posterior(idata, var_names=["p"], coords={"obs": plot_indices})
            plt.tight_layout()
            plt.savefig(posterior_plot_path, dpi=300)
            plt.close()
        except Exception as e:
            print(f"⚠️ Failed to plot 'p': {e}")

    # Posterior predictive check
    try:
        ppc_plot_path = os.path.join(output_dir, f"survey_ppc_{label}.png")
        az.plot_ppc(idata)
        plt.tight_layout()
        plt.savefig(ppc_plot_path, dpi=300)
        plt.close()
    except Exception as e:
        print(f"⚠️ Failed to plot PPC: {e}")

    # Rank plot for diagnostics
    try:
        rank_plot_path = os.path.join(output_dir, f"survey_rank_{label}.png")
        az.plot_rank(idata, var_names=trace_vars)
        plt.tight_layout()
        plt.savefig(rank_plot_path, dpi=300)
        plt.close()
    except Exception as e:
        print(f"⚠️ Failed to create rank plot: {e}")

    print(f"✅ Saved all outputs for model {label.upper()} in '{output_dir}' folder.")
    return idata, waic, loo, bic

import arviz as az
import numpy as np
import matplotlib.pyplot as plt

def run_model_diagnostics(idata, model_name="Model", output_dir="../results"):
    """
    Performs standard Bayesian diagnostics on a PyMC InferenceData object.
    Saves plots and prints summary messages for convergence, divergences, etc.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n🔍 Running diagnostics for {model_name}...\n")

    # --- R-hat and ESS ---
    summary = az.summary(idata)
    rhat_issues = summary["r_hat"].dropna() > 1.05
    ess_bulk_issues = summary["ess_bulk"].dropna() < 200
    ess_tail_issues = summary["ess_tail"].dropna() < 1000

    print("📏 R-hat summary:")
    print(summary["r_hat"].dropna())
    if rhat_issues.any():
        print(f"⚠️ R-hat > 1.05 for: {list(summary[rhat_issues].index)}")
    else:
        print("✅ All R-hat values < 1.05")

    print("\n📏 ESS (bulk) summary:")
    print(summary["ess_bulk"].dropna())
    if summary.loc["effect", "ess_bulk"] < 200:
        print("⚠️ ESS_bulk for 'effect' is below 200")
    else:
        print("✅ ESS_bulk for 'effect' is ≥ 200")

    print("\n📏 ESS (tail) summary:")
    print(summary["ess_tail"].dropna())
    if summary.loc["effect", "ess_tail"] < 1000:
        print("⚠️ ESS_tail for 'effect' is below 1000")
    else:
        print("✅ ESS_tail for 'effect' is ≥ 1000")

    # --- Divergences ---
    if "diverging" in idata.sample_stats:
        n_divergences = idata.sample_stats["diverging"].sum().values
        print(f"\n🚨 Divergences: {n_divergences}")
        if n_divergences > 0:
            print("⚠️ Consider increasing `target_accept` or reparameterizing.")
        else:
            print("✅ No divergences.")
    else:
        print("ℹ️ Divergence info not available.")

    # --- Tree Depth ---
    if "depth" in idata.sample_stats:
        max_depth = idata.sample_stats["depth"].max().values
        print(f"\n🌲 Max tree depth reached: {max_depth}")
        if max_depth >= 10:
            print("⚠️ Consider increasing `max_treedepth` if sampling is inefficient.")
        else:
            print("✅ Tree depth is within acceptable range.")
    else:
        print("ℹ️ Tree depth info not available.")

    # --- Energy plot (E-BFMI) ---
    energy_plot_path = os.path.join(output_dir, f"{model_name.lower()}_energy_plot.png")
    az.plot_energy(idata)
    plt.title("Energy Transition Plot (E-BFMI)")
    plt.tight_layout()
    plt.savefig(energy_plot_path, dpi=300)
    plt.close()
    print(f"\n📈 Saved energy transition plot to: {energy_plot_path}")

    # --- Optional: Posterior Predictive Check Plot ---
    if hasattr(idata, "posterior_predictive") and "y_pred" in idata.posterior_predictive:
        ppc_plot_path = os.path.join(output_dir, f"{model_name.lower()}_ppc_check.png")
        az.plot_ppc(idata)
        plt.title("Posterior Predictive Check")
        plt.tight_layout()
        plt.savefig(ppc_plot_path, dpi=300)
        plt.close()
        print(f"📈 Saved PPC plot to: {ppc_plot_path}")

    print(f"\n✅ Diagnostic check complete for {model_name}.\n")

"""### Tesing the model using the survey dataset"""

# Commented out IPython magic to ensure Python compatibility.
# Survey Data Generation
%run code_snippets.py

d.columns

# Rename columns to C999 format
new_columns = {old_col: f'C{i:03d}' for i, old_col in enumerate(d.columns)}
d = d.rename(columns=new_columns)

d.columns

#Merge the predictor columns
d["I_I"] = merge_columns(d["C027"], d["C079"])
print("\nDataframe with merged \"I_I\" columns (first 5 rows of relevant columns):")
print(d[["C027", "C079", "I_I"]].head())

#Prepare the outcome variable
print("\nUnique values in the outcome columns (C004):")
print(d["C004"].unique())

d["outcome_binary"] = d["C004"].apply(lambda x: 1 if x == "Igen" else 0)
print("\nFirst few rows with binary outcome:")
print(d[["C004", "outcome_binary"]].head())

#Prepare the predictor variable (I_I)
print("\nUnique values in the merged 'I_I' column:")
print(d["I_I"].unique())

#Change values of the likert scale to english
mapping = {'Egyetértek': 'I Agree', 'Egyáltalán nem értek egyet': 'I Completely Disagree', 'Nem értek egyet': 'I Do Not Agree', 'Teljesen egyetértek': 'I totally Agree'}
d["I_I"] = d["I_I"].map(mapping)
print("\nUnique values in the 'I_I' column after mapping:")
print(d["I_I"].unique())

d.describe()

d.info()

d.isna().sum()

likert_mapping = {
    "I Completely Disagree": 1,
    "I Do Not Agree": 2,
    "I Agree": 3,
    "I totally Agree": 4
}
d["I_I_numeric"] = d["I_I"].map(likert_mapping)

d.describe()

#Prepare data for the Bayesian model
y = d["outcome_binary"].values
X = d["I_I_numeric"].values

d_model = pd.DataFrame({
        "predictor": X,
        "outcome": y
    })
d_model.head()

# Run and save results for B02 for survey data
print("\nResults for B02 Model on survey data:")
idata, *_ = run_and_summarize(d_model, ordinal_predictor_binary_outcome_model, label = "b02", shape = 3)
run_model_diagnostics(idata, model_name="B02", output_dir="results")

"""## Getting Group Size Ratio PastEx to PresentEx"""

count = d_model['outcome'].value_counts()
ratio_PastEx_to_Present_Ex = count[1]/count[0]
print(f"Ratio of PastEx to PresentEx: {ratio_PastEx_to_Present_Ex}")

from scipy.special import expit  # this is the inverse logit
print(expit(0.201))
