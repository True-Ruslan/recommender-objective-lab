# Research references

Fact-checked against primary or authoritative publication pages on **2026-10-21**.

This repository is a **synthetic mechanism demonstration**. The sources below motivate
the framing; they do not validate the simulation's equations or coefficients.

## Production / recommender-system objectives

1. **Yi Wu, Daryl Chang, Jennifer She, Zhe Zhao, Li Wei, Lukasz Heldt (2024).  
   _Learned Ranking Function: From Short-term Behavior Predictions to Long-term User Satisfaction._  
   ACM RecSys 2024, pp. 1004–1009.**  
   DOI: https://doi.org/10.1145/3640457.3688184  
   Preprint: https://arxiv.org/abs/2408.06512  
   RecSys page: https://recsys.acm.org/recsys24/accepted-contributions/  
   **Verified scope:** the paper says LRF takes short-term user-item behavior predictions,
   optimizes a slate for long-term user satisfaction, is evaluated in live experiments,
   and its deployment on YouTube is described.

2. **Smitha Milli, Luca Belli, Moritz Hardt (2021).  
   _From Optimizing Engagement to Measuring Value._  
   ACM FAccT 2021, pp. 714–722.**  
   DOI: https://doi.org/10.1145/3442188.3445933  
   Preprint: https://arxiv.org/abs/2008.12623  
   **Verified scope:** frames the gap between observable engagement and a desired
   notion of value using measurement theory and a latent-variable operationalization.

3. **Jonathan Stray, Ivan Vendrov, Jeremy Nixon, Steven Adler, Dylan Hadfield-Menell (2021).  
   _What are you optimizing for? Aligning Recommender Systems with Human Values._**  
   https://arxiv.org/abs/2107.10939  
   **Publication status:** arXiv preprint; the arXiv record says it was originally
   presented at the ICML 2020 Participatory Approaches to Machine Learning workshop.  
   **Verified scope:** surveys cases where real recommender systems were modified for
   values including diversity, fairness, well-being, time well spent, and factual accuracy.

## Preferences and user welfare

4. **Jon Kleinberg, Sendhil Mullainathan, Manish Raghavan (2022).  
   _The Challenge of Understanding What Users Want: Inconsistent Preferences and Engagement Optimization._**  
   https://arxiv.org/abs/2202.11776  
   **Verified scope:** theoretical model with inconsistent preferences; the platform
   wants to maximize user utility but only observes engagement. The paper characterizes
   cases where increasing engagement need not increase utility.

5. **Poruz Khambatta, Shwetha Mariadassou, Joshua Morris, S. Christian Wheeler (2023).  
   _Tailoring recommendation algorithms to ideal preferences makes users better off._  
   Scientific Reports 13, 9325.**  
   DOI: https://doi.org/10.1038/s41598-023-34192-x  
   **Verified scope:** high-powered preregistered main experiment n=6488. The primary
   actual-vs-ideal analysis for cases where the recommendations differed uses n=2504.
   Actual-preference recommendations were clicked 52% vs 40% for ideal-preference
   recommendations; ideal recommendations scored higher on feeling better off and
   time well spent.

## Long-horizon dynamics and feedback

6. **Eden Saig, Nir Rosenfeld (2023).  
   _Learning to Suggest Breaks: Sustainable Optimization of Long-Term User Engagement._  
   ICML 2023, PMLR 202:29671–29696.**  
   https://proceedings.mlr.press/v202/saig23a.html  
   **Verified scope:** models recommendation dynamics with positive and negative feedback,
   formulates break selection as optimal control, and demonstrates the approach empirically
   on **semi-synthetic data**. Do not cite it as a field experiment on a production platform.

7. **Björn Lindström, Martin Bellander, David T. Schultner, Allen Chang,
   Philippe N. Tobler, David M. Amodio (2021).  
   _A computational reward learning account of social media engagement._  
   Nature Communications 12, 1311.**  
   DOI: https://doi.org/10.1038/s41467-020-19607-x  
   **Verified scope:** analyzes 1,046,857 posts from 4,168 users across four social-media
   datasets and reports an online experiment (n=176) supporting a reward-learning account
   of social-media behavior. This is **not** evidence that a recommender system causes
   preference drift.

## Philosophical / theological parallels

8. **Aristotle. _Nicomachean Ethics_, Book I.**  
   https://classics.mit.edu/Aristotle/nicomachaen.1.i.html  
   Book I distinguishes ends pursued for the sake of something else from a final end
   desired for itself. This is used only as an analogy for instrumental metrics vs goals.

9. **Romans 7:15–19 (within Romans 7:14–8:2).**  
   Orthodox Church in America reading: https://www.oca.org/readings/daily/2026/06/16/1  
   Used only as a theological analogy for a distinction between intended good and
   observed action; it is not empirical support for the recommender-system model.

## Defensible central claim

> Observable behavior is a proxy. If the proxy differs from the desired
> long-horizon outcome, optimizing the proxy can select a different policy from
> optimizing the outcome itself.

The repository tests that mechanism under explicit synthetic assumptions.
