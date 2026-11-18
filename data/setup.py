import os
import math

import pandas as pd


class Limits:
    def __init__(self, lower: float = 0, upper: float = math.inf, unit: str = "g") -> None:
        self.lower = lower
        self.upper = upper
        self.unit = unit

    @property
    def lower(self) -> float:
        return self._lower

    @property
    def upper(self) -> float:
        return self._upper

    @property
    def unit(self) -> float:
        return self._unit

    @lower.setter
    def lower(self, value):
        self._lower = value

    @upper.setter
    def upper(self, value):
        self._upper = value

    @unit.setter
    def unit(self, value):
        self._unit = value


class Nutrient:
    def __init__(self, name: str, key: str, unit: str, limits: Limits = Limits()) -> None:
        self.name = name
        self.key = key
        self.unit = unit
        self.limits = limits

    @property
    def name(self) -> str:
        return self._name

    @property
    def key(self) -> str:
        return self._key

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def limits(self) -> Limits:
        return self._limits

    @name.setter
    def name(self, value):
        self._name = value

    @key.setter
    def key(self, value: str):
        self._key = value

    @unit.setter
    def unit(self, value: str):
        self._unit = value

    @limits.setter
    def limits(self, value):
        self._limits = value


class PriceInfo:
    def __init__(self, euro: float, grams: float) -> None:
        self.euro = euro
        self.grams = grams

    @property
    def euro(self) -> float:
        return self._euro

    @property
    def grams(self) -> float:
        return self._grams

    @euro.setter
    def euro(self, value):
        self._euro = value

    @grams.setter
    def grams(self, value):
        self._grams = value


class Food:
    def __init__(self, name: str, key: str, price: PriceInfo) -> None:
        self.name = name
        self.key = key
        self.price = price

    @property
    def name(self) -> str:
        return self._name

    @property
    def key(self) -> str:
        return self._key

    @property
    def price(self) -> PriceInfo:
        return self._price

    @name.setter
    def name(self, value):
        self._name = value

    @key.setter
    def key(self, value):
        self._key = value

    @price.setter
    def price(self, value):
        self._price = value


# absolute limits from: https://dricalculator.com/dri-chart/
# saturated fat from: https://cdn.realfood.gov/DGA.pdf
# ones missing from these are modeled approximately by me :)
NUTRIENTS = [
    # energy & macronutrients
    Nutrient("Energy", "ENERCJ Energie (Kilojoule) [kJ/100g]", "kJ/100g", Limits(11000, 14000, "kJ")),
    Nutrient("Carbohydrates", "CHO Kohlenhydrate, verfügbar [g/100g]", "g/100g", Limits(130, math.inf, "g")),
    Nutrient("Sugars", "SUGAR Zucker (Mono- und Disaccharide), gesamt [g/100g]", "g/100g", Limits(0, 0.15, "of total energy")),
    Nutrient("Fiber", "FIBT Ballaststoffe, gesamt [g/100g]", "g/100g", Limits(38, math.inf, "g")),
    Nutrient("Protein", "PROT625 Protein (Nx6,25) [g/100g]", "g/100g", Limits(56, math.inf, "g")),
    Nutrient("Fat", "FAT Fett [g/100g]", "g/100g", Limits(30, math.inf, "g")),
    Nutrient("Saturated fat", "FASAT Fettsäuren, gesättigt, gesamt [g/100g]", "g/100g", Limits(0, 0.1, "of total energy")),
    Nutrient("Monounsaturated fat", "FAMS Fettsäure, einfach ungesättigt, gesamt [g/100g]", "g/100g"),
    Nutrient("Polyunsaturated fat", "FAPU Fettsäuren, mehrfach ungesättigt, gesamt [g/100g]", "g/100g"),
    Nutrient("Omega-3", "FAPUN3 Fettsäuren, mehrfach ungesättigt n-3 (Omega-3), gesamt [g/100g]", "g/100g", Limits(1.6, math.inf, "g")),
    Nutrient("Omega-6", "FAPUN6 Fettsäuren, mehrfach ungesättigt n-6 (Omega-6), gesamt [g/100g]", "g/100g", Limits(17, math.inf, "g")),
    # minerals
    Nutrient("Sodium", "NA Natrium [mg/100g]", "mg/100g", Limits(1500, math.inf, "mg")),
    Nutrient("Potassium", "K Kalium [mg/100g]", "mg/100g", Limits(3400, math.inf, "mg")),
    Nutrient("Calcium", "CA Calcium [mg/100g]", "mg/100g", Limits(1000, 2500, "mg")),
    Nutrient("Magnesium", "MG Magnesium [mg/100g]", "mg/100g", Limits(420, math.inf, "mg")),
    Nutrient("Phosphorus", "P Phosphor [mg/100g]", "mg/100g", Limits(700, math.inf, "mg")),
    Nutrient("Iron", "FE Eisen [mg/100g]", "mg/100g", Limits(8, 45, "mg")),
    Nutrient("Zinc", "ZN Zink [mg/100g]", "mg/100g", Limits(11, 40, "mg")),
    Nutrient("Copper", "CU Kupfer [µg/100g]", "µg/100g", Limits(900, math.inf, "mg")),
    Nutrient("Manganese", "MN Mangan [µg/100g]", "µg/100g", Limits(2300, math.inf, "µg")),
    Nutrient("Iodine", "ID Iodid [µg/100g]", "µg/100g", Limits(150, 1100, "µg")),
    # vitamins
    Nutrient("Vitamin A (RAE)", "VITAA Vitamin A, Retinol-Aktivitäts-Äquivalent (RAE) [µg/100g]", "µg/100g", Limits(900, 3000, "µg")),
    Nutrient("Vitamin D", "VITD Vitamin D [µg/100g]", "µg/100g", Limits(15, 100, "µg")),
    Nutrient("Vitamin E", "VITE Vitamin E (Alpha-Tocopherol) [mg/100g]", "mg/100g", Limits(15, 1000, "mg")),
    Nutrient("Vitamin K", "VITK Vitamin K [µg/100g]", "µg/100g", Limits(120, math.inf, "µg")),
    Nutrient("Thiamine", "THIA Vitamin B1 (Thiamin) [mg/100g]", "mg/100g", Limits(1.2, math.inf, "mg")),
    Nutrient("Riboflavin", "RIBF Vitamin B2 (Riboflavin) [mg/100g]", "mg/100g", Limits(1.3, math.inf, "mg")),
    Nutrient("Niacin", "NIAEQ Niacin-Äquivalent [mg/100g]", "mg/100g", Limits(16, 35, "mg")),
    Nutrient("Vitamin B6", "VITB6 Vitamin B6 [µg/100g]", "µg/100g", Limits(1.3, 100, "mg")),
    Nutrient("Folate", "FOL Folat-Äquivalent [µg/100g]", "µg/100g", Limits(400, math.inf, "µg")),
    Nutrient("Biotin", "BIOT Biotin [µg/100g]", "µg/100g", Limits(30, math.inf, "µg")),
    Nutrient("Vitamin B12", "VITB12 Vitamin B12 (Cobalamine) [µg/100g]", "µg/100g", Limits(2.4, math.inf, "µg")),
    Nutrient("Vitamin C", "VITC Vitamin C [mg/100g]", "mg/100g", Limits(90, 2000, "mg")),
]

# prices from various discounters (Rewe, Edeka, etc.) by rough matches :)
FOOD_ITEMS = [
    # grains and starches
    Food("White bread", "B311000", PriceInfo(2.49, 750)),
    Food("Whole-grain bread", "B121000", PriceInfo(2.99, 750)),
    Food("Rye-wheat bread", "B271000", PriceInfo(2.99, 750)),
    Food("Egg pasta", "E432000", PriceInfo(1.19, 500)),
    Food("Whole-grain pasta (no egg)", "E510000", PriceInfo(0.85, 500)),
    Food("White rice", "C352000", PriceInfo(2.39, 500)),
    Food("Oat roll", "B531000", PriceInfo(600, 5.89)),
    Food("Potatoes", "K120100", PriceInfo(2000, 2.59)),
    Food("Sweetened cereal", "C534500", PriceInfo(2.79, 375)),
    Food("Sweetened whole-grain cereal", "C539100", PriceInfo(2.99, 300)),
    # meats and sausages
    Food("Roast chicken", "Y560322", PriceInfo(10.68, 1200)),
    Food("Minced pork/beef meat", "U040182", PriceInfo(5.79, 400)),
    Food("Beef steak", "Y184512", PriceInfo(7.38, 200)),
    Food("Pork loin", "W510082", PriceInfo(7.22, 560)),
    Food("Pork Sausage", "U065100", PriceInfo(2.78, 200)),
    Food("Ham", "W164000", PriceInfo(2.39, 100)),
    Food("Salami", "W140000", PriceInfo(3.69, 80)),
    Food("Veal liver", "V532100", PriceInfo(3.59, 150)),
    # fish
    Food("Salmon", "T410082", PriceInfo(3.24, 150)),
    Food("Cod", "T204162", PriceInfo(7.49, 150)),
    Food("Herring", "T102162", PriceInfo(3.69, 200)),
    Food("Mackerel", "T107182", PriceInfo(5.47, 275)),
    Food("Canned tuna", "T121902", PriceInfo(2.99, 120)),
    # eggs and dairy
    Food("Eggs", "Y740162", PriceInfo(3.49, 300)),
    Food("Cow milk, skimmed", "M111100", PriceInfo(1.49, 1000)),
    Food("Cow milk, whole", "M111300", PriceInfo(1.19, 1000)),
    Food("Yogurt, plain", "M141300", PriceInfo(1.99, 500)),
    Food("Cheese, hard", "M402600", PriceInfo(1.29, 100)),
    Food("Quark", "M713700", PriceInfo(1.45, 185)),
    Food("Butter", "Q6A4000", PriceInfo(1.99, 125)),
    Food("Cream cheese", "M710800", PriceInfo(1.11, 195)),
    Food("Butterkäse cheese", "M302600", PriceInfo(0.99, 100)),
    # vegan alternatives
    Food("Oat milk (fortified)", "C660200", PriceInfo(2.49, 1000)),
    Food("Soy milk (fortified)", "H841400", PriceInfo(2.49, 1000)),
    Food("Almond milk (fortified)", "H800400", PriceInfo(2.99, 1000)),
    Food("Coconut milk", "H154000", PriceInfo(2.99, 1000)),
    Food("Soy yogurt (fortified)", "H844500", PriceInfo(2.19, 400)),
    Food("Vegan cheese (fortified)", "Q590100", PriceInfo(2.49, 140)),
    # legumes, nuts and seeds
    Food("Lentils", "H725100", PriceInfo(2.49, 400)),
    Food("Haricot beans", "H739400", PriceInfo(1.49, 500)),
    Food("Chickpeas", "X574212", PriceInfo(1.49, 500)),
    Food("Tofu", "H861000", PriceInfo(3.29, 400)),
    Food("Peanuts", "H110600", PriceInfo(2.49, 400)),
    Food("Almonds", "S465000", PriceInfo(4.49, 200)),
    Food("Walnuts", "H120100", PriceInfo(3.79, 150)),
    Food("Sunflower seeds", "H430100", PriceInfo(1.89, 200)),
    Food("Chia seeds", "H480100", PriceInfo(4.89, 250)),
    # vegetables
    Food("Broccoli", "G312100", PriceInfo(1.99, 500)),
    Food("Spinach", "G211100", PriceInfo(2.29, 500)),
    Food("Curly kale", "G322100", PriceInfo(2.39, 1000)),
    Food("Carrots", "G620100", PriceInfo(1.39, 1000)),
    Food("Tomatoes", "G561100", PriceInfo(0.30, 120)),
    Food("Onion", "G480100", PriceInfo(1.59, 1500)),
    Food("Garlic", "G490100", PriceInfo(0.83, 70)),
    Food("Bell pepper (red)", "G543100", PriceInfo(2.29, 500)),
    Food("Frozen peas", "G760200", PriceInfo(2.59, 1000)),
    Food("Button mushrooms", "K701100", PriceInfo(2.99, 250)),
    # fruits
    Food("Apples", "F110100", PriceInfo(2.49, 550)),
    Food("Bananas", "F503100", PriceInfo(0.50, 200)),
    Food("Oranges", "F603100", PriceInfo(2.99, 2000)),
    Food("Blueberries", "F304100", PriceInfo(4.49, 300)),
    Food("Dried apricot", "F201400", PriceInfo(4.99, 200)),
    # oils and fats
    Food("Olive oil", "Q120000", PriceInfo(9.99, 450)),
    Food("Rapeseed oil", "Q180000", PriceInfo(4.99, 675)),
    Food("Beef tallow", "Q890000", PriceInfo(7.79, 200)),
    # drinks
    Food("Cola", "N330000", PriceInfo(1.89, 1000)),
    Food("Cola (zero sugar)", "N331000", PriceInfo(1.89, 1000)),
    Food("Orange juice", "F603600", PriceInfo(1.79, 1000)),
    Food("Apple juice", "F110600", PriceInfo(2.19, 700)),
    Food("Coffee", "N410100", PriceInfo(14.99, 1000)),
]


if __name__ == "__main__":
    data_path = os.path.join(str(os.path.dirname(__file__)), "BLS_4_0_2025_DE/BLS_4_0_Daten_2025_DE.xlsx")
    bls = pd.read_excel(data_path, header=0, index_col="BLS Code", dtype=str)
    nutrient_table = (
        bls.loc[[f.key for f in FOOD_ITEMS]]
            .loc[:, [n.key for n in NUTRIENTS]]
            .apply(lambda x: pd.to_numeric(x, errors="coerce"))
            .fillna(0)
            .rename(index={f.key: f.name for f in FOOD_ITEMS}, columns={n.key: f"{n.name} [{n.unit}]" for n in NUTRIENTS})
    )
    nutrient_table.index.rename("Item", inplace=True)
    price_table = pd.DataFrame(
        index=[f.name for f in FOOD_ITEMS],
        data={
            "Price [Euro]": [f.price.euro for f in FOOD_ITEMS],
            "Amount [g]": [f.price.grams for f in FOOD_ITEMS],
        }
    )
    price_table.index.rename("Item", inplace=True)
    food_table = pd.concat([price_table, nutrient_table], axis=1)
    food_table.to_csv(os.path.join(str(os.path.dirname(__file__)), "food.csv"))

    limit_table = pd.DataFrame(
        index=[n.name for n in NUTRIENTS],
        data={
            "Lower": [n.limits.lower for n in NUTRIENTS],
            "Upper": [n.limits.upper for n in NUTRIENTS],
            "Unit": [n.limits.unit for n in NUTRIENTS],
        },
    )
    limit_table.index.rename("Nutrient", inplace=True)
    limit_table.to_csv(os.path.join(str(os.path.dirname(__file__)), "limits.csv"))
