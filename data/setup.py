import os

import pandas as pd


class Nutrient:
    def __init__(self, name: str, key: str, unit: str) -> None:
        self.name = name
        self.key = key
        self.unit = unit

    @property
    def name(self) -> str:
        return self._name

    @property
    def key(self) -> str:
        return self._key

    @property
    def unit(self) -> str:
        return self._unit

    @name.setter
    def name(self, value):
        self._name = value

    @key.setter
    def key(self, value: str):
        self._key = value

    @unit.setter
    def unit(self, value: str):
        self._unit = value


class Food:
    def __init__(self, name: str, key: str) -> None:
        self.name = name
        self.key = key

    @property
    def name(self) -> str:
        return self._name

    @property
    def key(self) -> str:
        return self._key

    @name.setter
    def name(self, value):
        self._name = value

    @key.setter
    def key(self, value):
        self._key = value


NUTRIENTS = [
    # energy & macronutrients
    Nutrient("Energy", "ENERCJ Energie (Kilojoule) [kJ/100g]", "kJ/100g"),
    Nutrient("Carbohydrates", "CHO Kohlenhydrate, verfügbar [g/100g]", "g/100g"),
    Nutrient("Sugars", "SUGAR Zucker (Mono- und Disaccharide), gesamt [g/100g]", "g/100g"),
    Nutrient("Fiber", "FIBT Ballaststoffe, gesamt [g/100g]", "g/100g"),
    Nutrient("Protein", "PROT625 Protein (Nx6,25) [g/100g]", "g/100g"),
    Nutrient("Fat", "FAT Fett [g/100g]", "g/100g"),
    Nutrient("Saturated fat", "FASAT Fettsäuren, gesättigt, gesamt [g/100g]", "g/100g"),
    Nutrient("Monounsaturated fat", "FAMS Fettsäure, einfach ungesättigt, gesamt [g/100g]", "g/100g"),
    Nutrient("Polyunsaturated fat", "FAPU Fettsäuren, mehrfach ungesättigt, gesamt [g/100g]", "g/100g"),
    Nutrient("Omega-3", "FAPUN3 Fettsäuren, mehrfach ungesättigt n-3 (Omega-3), gesamt [g/100g]", "g/100g"),
    Nutrient("Omega-6", "FAPUN6 Fettsäuren, mehrfach ungesättigt n-6 (Omega-6), gesamt [g/100g]", "g/100g"),
    # minerals
    Nutrient("Sodium", "NA Natrium [mg/100g]", "mg/100g"),
    Nutrient("Potassium", "K Kalium [mg/100g]", "mg/100g"),
    Nutrient("Calcium", "CA Calcium [mg/100g]", "mg/100g"),
    Nutrient("Magnesium", "MG Magnesium [mg/100g]", "mg/100g"),
    Nutrient("Phosphorus", "P Phosphor [mg/100g]", "mg/100g"),
    Nutrient("Iron", "FE Eisen [mg/100g]", "mg/100g"),
    Nutrient("Zinc", "ZN Zink [mg/100g]", "mg/100g"),
    Nutrient("Copper", "CU Kupfer [µg/100g]", "µg/100g"),
    Nutrient("Manganese", "MN Mangan [µg/100g]", "µg/100g"),
    Nutrient("Iodine", "ID Iodid [µg/100g]", "µg/100g"),
    # vitamins
    Nutrient("Vitamin A (RAE)", "VITAA Vitamin A, Retinol-Aktivitäts-Äquivalent (RAE) [µg/100g]", "µg/100g"),
    Nutrient("Vitamin D", "VITD Vitamin D [µg/100g]", "µg/100g"),
    Nutrient("Vitamin E", "VITE Vitamin E (Alpha-Tocopherol) [mg/100g]", "mg/100g"),
    Nutrient("Vitamin K", "VITK Vitamin K [µg/100g]", "µg/100g"),
    Nutrient("Thiamine", "THIA Vitamin B1 (Thiamin) [mg/100g]", "mg/100g"),
    Nutrient("Riboflavin", "RIBF Vitamin B2 (Riboflavin) [mg/100g]", "mg/100g"),
    Nutrient("Niacin", "NIAEQ Niacin-Äquivalent [mg/100g]", "mg/100g"),
    Nutrient("Vitamin B6", "VITB6 Vitamin B6 [µg/100g]", "µg/100g"),
    Nutrient("Folate", "FOL Folat-Äquivalent [µg/100g]", "µg/100g"),
    Nutrient("Biotin", "BIOT Biotin [µg/100g]", "µg/100g"),
    Nutrient("Vitamin B12", "VITB12 Vitamin B12 (Cobalamine) [µg/100g]", "µg/100g"),
    Nutrient("Vitamin C", "VITC Vitamin C [mg/100g]", "mg/100g"),
]

FOOD_ITEMS = [
    # grains and starches
    Food("White bread", "B311000"),
    Food("Whole-grain bread", "B121000"),
    Food("Rye-wheat bread", "B271000"),
    Food("Egg pasta", "E432000"),
    Food("Whole-grain pasta (no egg)", "E510000"),
    Food("White rice", "C352000"),
    Food("Oat roll", "B531000"),
    Food("Potatoes", "K120100"),
    Food("Sweetened cereal", "C534500"),
    Food("Sweetened whole-grain cereal", "C539100"),
    # meats and sausages
    Food("Roast chicken", "Y560322"),
    Food("Minced pork/beef meat", "U040182"),
    Food("Beef steak", "Y184512"),
    Food("Pork loin", "W510082"),
    Food("Pork Sausage", "U065100"),
    Food("Ham", "W164000"),
    Food("Salami", "W140000"),
    Food("Lamb liver", "V535182"),
    # fish
    Food("Salmon", "T410082"),
    Food("Cod", "T204162"),
    Food("Herring", "T102162"),
    Food("Mackerel", "T107182"),
    Food("Canned tuna", "T121902"),
    # eggs and dairy
    Food("Eggs", "Y740162"),
    Food("Cow milk, skimmed", "M111100"),
    Food("Cow milk, whole", "M111300"),
    Food("Yogurt, plain", "M141300"),
    Food("Cheese, hard", "M402600"),
    Food("Quark", "M713700"),
    Food("Butter", "Q6A4000"),
    Food("Cream cheese", "M710800"),
    Food("Butterkäse cheese", "M302600"),
    # vegan alternatives
    Food("Oat milk (fortified)", "C660200"),
    Food("Soy milk (fortified)", "H841400"),
    Food("Almond milk (fortified)", "H800400"),
    Food("Coconut milk", "H154000"),
    Food("Soy yogurt (fortified)", "H844500"),
    Food("Vegan cheese (fortified)", "Q590100"),
    # legumes, nuts and seeds
    Food("Lentils", "H725100"),
    Food("Haricot beans", "H739400"),
    Food("Chickpeas", "X574212"),
    Food("Tofu", "H861000"),
    Food("Peanuts", "H110600"),
    Food("Almonds", "S465000"),
    Food("Walnuts", "H120100"),
    Food("Sunflower seeds", "H430100"),
    Food("Chia seeds", "H480100"),
    # vegetables
    Food("Broccoli", "G312100"),
    Food("Spinach", "G211100"),
    Food("Curly kale", "G322100"),
    Food("Carrots", "G620100"),
    Food("Tomatoes", "G561100"),
    Food("Onion", "G480100"),
    Food("Garlic", "G490100"),
    Food("Bell pepper (red)", "G543100"),
    Food("Frozen peas", "G760200"),
    Food("Button mushrooms", "K701100"),
    # fruits
    Food("Apples", "F110100"),
    Food("Bananas", "F503100"),
    Food("Oranges", "F603100"),
    Food("Blueberries", "F304100"),
    Food("Dried apricot", "F201400"),
    # oils and fats
    Food("Olive oil", "Q120000"),
    Food("Rapeseed oil", "Q180000"),
    Food("Beef tallow", "Q890000"),
    # drinks
    Food("Cola", "N330000"),
    Food("Cola (zero sugar)", "N331000"),
    Food("Orange juice", "F603600"),
    Food("Apple juice", "F110600"),
    Food("Coffee", "N410100"),
]


if __name__ == "__main__":
    data_path = os.path.join(str(os.path.dirname(__file__)), "BLS_4_0_2025_DE/BLS_4_0_Daten_2025_DE.xlsx")
    bls = pd.read_excel(data_path, header=0, index_col="BLS Code", dtype=str)
    food_table = (
        bls.loc[[f.key for f in FOOD_ITEMS]]
            .loc[:, [n.key for n in NUTRIENTS]]
            .apply(lambda x: pd.to_numeric(x, errors="coerce"))
            .fillna(0)
            .rename(index={f.key: f.name for f in FOOD_ITEMS}, columns={n.key: f"{n.name} [{n.unit}]" for n in NUTRIENTS})
    )
    food_table.index.rename("Food", inplace=True)
    food_table.to_csv(os.path.join(str(os.path.dirname(__file__)), "food.csv"))
