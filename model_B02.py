import pymc as pm
import numpy as np
import arviz as az
import pytensor.tensor as pt
import random
import pytensor

def ordinal_predictor_binary_outcome_model(predictor, outcome, variant="B02", seed = 42, shape = 4):
    """
    PyMC model with a binary outcome and an ordinal predictor with a normal random walk constraint.
    If variant=="B01", uses B01 priors else uses B02 with fluctuations around an estimated effect.
    Returns model, idata, waic, loo, bic.
    """
    #--- Robust Reproducibility Setup ---
    random.seed(seed)
    np.random.seed(seed)
    pytensor.config.on_opt_error = 'raise'

    with pm.Model() as model:
        # Define the 'obs' dimension
        n_obs = len(outcome)
        model.add_coord("obs", np.arange(n_obs))
      

        if variant == "B01":
            # B01: no "effect" or "sd_fluctuation"; level_effects_diff is N(0,2)
            intercept = pm.Normal("intercept", mu=0, sigma=2.5)
            level_effects_diff = pm.Normal("level_effects_diff", mu=0, sigma=2, shape=shape)
        else:
            # B02: has "effect" and "sd_fluctuation"; level_effects_diff ~ N(effect, sd_fluctuation)
            effect = pm.Normal("effect", mu=0, sigma=0.55)
            sd_fluctuation = pm.HalfNormal("sd_fluctuation", sigma = 1)
            intercept = pm.Normal("intercept", mu=0, sigma=abs(effect) + 1e-3)

            level_effects_diff = pm.Normal("level_effects_diff", mu=effect, sigma=sd_fluctuation, shape=shape)

        # Centered level effects
        raw_effects = pm.math.concatenate([[0], pm.math.cumsum(level_effects_diff)])
        centered_effects = raw_effects - pt.mean(raw_effects)
        level_effects = pm.Deterministic("level_effects", centered_effects)
        
        #Linear predictor
        logit_p = intercept + (centered_effects[predictor - 1])
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p), dims="obs")  # Dimension 'p' by 'obs'

        # Likelihood - Associate observed data with 'obs' dimension
        y_obs = pm.Bernoulli("y_obs", p=p, observed=outcome, dims="obs")

        # Posterior predictive samples
        y_pred = pm.Bernoulli("y_pred", p=p, observed=None, dims="obs")

        # Sampling - Request log_likelihood
        idata = pm.sample(
            5000,
            tune=5000,
            random_seed=seed,
            return_inferencedata=True,
            target_accept=0.995,  # Increased target_accept
            init = "adapt_diag",
            idata_kwargs={"log_likelihood": True},
            nuts={"max_treedepth": 15}  
        )
        idata.extend(pm.sample_posterior_predictive(idata))

        waic = az.waic(idata)
        loo = az.loo(idata)

        # --- BIC calculation using highest posterior probability in the trace ---
        n_params = len(model.free_RVs)
        log_likelihood = idata.log_likelihood.y_obs.values  # shape: (chains, draws, obs)
        summed_logps = log_likelihood.sum(axis=-1).flatten()
        max_logp = np.max(summed_logps)
        bic = -2 * max_logp + n_params * np.log(n_obs)  

    return model, idata, waic, loo, bic
