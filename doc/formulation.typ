= Diet Optimization

A balanced, healthy diet provides the body with essential nutrition: macronutrients (e.g., carbohydrates, protein), micronutrients (e.g., vitamins, trace elements), fibre and sufficient energy. However, some of these nutrients are unhealthy in excess (e.g., sodium), meaning there is not only a minimum required intake, but also potentially a maximum tolerable intake.

Let $F$ be the set of available food items, $g: F arrow.r bb(R)^+$ be the pack sizes for each item, and $p: F arrow.r bb(R)^+$ be the prices for each pack. Further, let $H$ be the set of tracked nutrients, $ell_min: H arrow.r overline(bb(R))^+$ and equivalently $ell_max$ be the minimum required and maximum tolerable intake, and $n: F times H arrow.r bb(R)^+$ the nutrient breakdown of each food item.

`food.csv` contains a table of food items with its pack size (in gram), the price per pack (in Euro), and its nutrient breakdown (in [unit] per 100 g). `limits.csv` contains the daily minimum required intakes and maximum tolerable intakes for each listed nutrient in the same unit as in the nutrient breakdown in `food.csv`, or in terms of the total energy.

== Problems

1. Formulate a linear program to minimize the daily cost of a diet that meets the required constraints, ignoring the ones given in terms of total energy.
2. Implement this linear program (e.g., in Python using #link("https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html")[scipy]).
3. A store wouldn't let you buy, for example, 0.108 packs of white rice. Adapt the implementation to use integer variables where appropriate.
4. While this is a better model of reality, it's still questionable to assume someone would buy the exact amount of food and drink they consume on every given day. Change the formulation of the (I)LP to allow buying food items to be consumed over $N in bb(N)_(>0)$ days, then adapt the implementation. Does the consumption of fractional packs per day require any additional changes?
5. Some of the constraints are specified in terms of the total energy. How can these be added into the (I)LP? Formulate the constraints and add them to the implementation.

== Proposed Solutions

For the implementations, see the Rust code in `src`.

=== Linear Program

The problem variables $x_f >= 0$ are the packs of food bought per day. The objective is

$
  min sum_(f in F) p(f) dot x_f
$

For each nutrient $h in H$, the constraints are:

$
  ell_min (h) <= sum_(f in F) n(f, h) dot g(f) / 100 dot x_f <= ell_max (h),
$

where any bounds with $ell_min (h) = 0$ and $ell_max (h) = infinity$ are skipped, and the energy-based rows are ignored for now.

=== Integer Linear Program

We further require $x_f in bb(N)_(>= 0)$. Nothing else needs to be changed.

=== N-Day Average

This requires some consideration of what we're actually trying to solve here. One immediate complication of considering multiple days is that an adversary can potentially, e.g., eat all the ham on the first day to exceed the maximum tolerable intake of sodium immediately. The same is also trivially true for minimum required intake of any nutrient. One could implement a follow-up algorithm which computes a meal plan from the shopping list, or introduce additional variables that model the daily consumption, but this is beyond the scope of this problem.

The modification to the (I)LP that is required to make this behavior possible is in the constraints, by multiplying the lower and upper bounds by the number of days:

$
  N dot ell_min (h) <= sum_(f in F) n(f, h) dot g(f) / 100 dot x_f <= N dot ell_max (h),
$

In order to get the daily meal plan from these constraint equations, we can divide them by $N$ (or directly formulate the constraints in this way):

$
  sum_(f in F) n(f, h) dot g(f) / 100 dot x_f / N
$

where the $x_f / N$ are the, possibly fractional, number of packs of each item a non-adversarial actor would consume in order for our shopping list to meet their daily numbers.

=== Total Energy Constraints

The nutrients with these constraints have some conversion factor $c_h$ to get from mass to (usable) energy (e.g., 17 $"kJ" / "g"$ for sugars, 37 $"kJ" / "g"$ for saturated fat). Let $alpha_h, beta_h in [0, 1]$ be the fractional range $[alpha, beta]$ of total energy the nutrient $h$ must land within. Then

$
  E_(min, h) & = alpha_h dot E \
  E_(max, h) & = beta_h dot E \
  E & = sum_(f in F) n(f, "energy") dot g(f) / 100 dot x_f
$

The newly added constraints for each such $h in H$ are then

$
  E_(min, h) & <= sum_(f in F) c_h dot n(f, h) dot g(f) / 100 dot x_f && <= E_(max, h) \
  alpha_h dot sum_(f in F) n(f, "energy") dot g(f) / 100 dot x_f & <= sum_(f in F) c_h dot n(f, h) dot g(f) / 100 dot x_f && <= beta_h dot sum_(f in F) n(f, "energy") dot g(f) / 100 dot x_f
$
