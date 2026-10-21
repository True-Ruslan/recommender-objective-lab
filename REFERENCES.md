# Research references

The experiment is a **synthetic mechanism demonstration**. The papers below motivate
the problem framing; they do not validate every equation or coefficient used in the
simulation.

## Production / recommender-system objectives

1. **Yi Wu, Daryl Chang, Jennifer She, Zhe Zhao, Li Wei, Lukasz Heldt (2024).  
   _Learned Ranking Function: From Short-term Behavior Predictions to Long-term User Satisfaction._  
   ACM RecSys 2024, pp. 1004–1009.**  
   DOI: https://doi.org/10.1145/3640457.3688184  
   Preprint: https://arxiv.org/abs/2408.06512  
   Production evidence that the ranking stage can be framed around long-term user
   satisfaction rather than only a hand-tuned combination of short-term behavior
   predictions.

2. **Smitha Milli, Luca Belli, Moritz Hardt (2021).  
   _From Optimizing Engagement to Measuring Value._  
   ACM FAccT 2021, pp. 714–722.**  
   DOI: https://doi.org/10.1145/3442188.3445933  
   Preprint: https://arxiv.org/abs/2008.12623  
   Frames the gap between observable engagement and a latent construct such as
   user value as a measurement problem.

3. **Jonathan Stray, Ivan Vendrov, Jeremy Nixon, Steven Adler, Dylan Hadfield-Menell (2021).  
   _What are you optimizing for? Aligning Recommender Systems with Human Values._**  
   https://arxiv.org/abs/2107.10939  
   Surveys value-sensitive objectives in recommender systems and connects
   recommendation design to AI-alignment questions.

## Preferences and user welfare

4. **Jon Kleinberg, Sendhil Mullainathan, Manish Raghavan (2022).  
   _The Challenge of Understanding What Users Want: Inconsistent Preferences and Engagement Optimization._**  
   https://arxiv.org/abs/2202.11776  
   Provides a theoretical model showing why observed choices and engagement need
   not be identical to user utility when preferences are internally inconsistent.

5. **Poruz Khambatta, Shwetha Mariadassou, Joshua Morris, S. Christian Wheeler (2023).  
   _Tailoring recommendation algorithms to ideal preferences makes users better off._  
   Scientific Reports 13, 9325.**  
   DOI: https://doi.org/10.1038/s41598-023-34192-x  
   A preregistered experiment (n=6488) comparing recommendations tailored to
   actual versus ideal preferences.

## Long-horizon dynamics and feedback

6. **Eden Saig, Nir Rosenfeld (2023).  
   _Learning to Suggest Breaks: Sustainable Optimization of Long-Term User Engagement._  
   ICML 2023, PMLR 202:29671–29696.**  
   https://proceedings.mlr.press/v202/saig23a.html  
   Models recommendation as a dynamic system with positive and negative feedback
   and studies policies that trade immediate engagement for sustainable long-term
   engagement.

7. **Björn Lindström, Martin Bellander, David T. Schultner, Allen Chang,
   Philippe N. Tobler, David M. Amodio (2021).  
   _A computational reward learning account of social media engagement._  
   Nature Communications 12, 1311.**  
   DOI: https://doi.org/10.1038/s41467-020-19607-x  
   Empirical evidence, using large-scale observational data plus an online
   experiment, that social-media behavior can exhibit reward-learning dynamics.

## How these references should be used

The defensible claim is not “engagement is bad.” It is narrower:

> Observable behavior is a proxy. If the proxy differs from the desired
> long-horizon outcome, optimizing the proxy can select a different policy from
> optimizing the outcome itself.

The repository tests that mechanism under explicit synthetic assumptions.
